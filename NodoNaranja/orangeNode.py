import socket
import pickle
import sys
import queue
import threading
from blueNodeTable import blueNodeTable
from RoutingTable import RoutingTable
from ooPackage import ooPackage
from obPackage import obPackage
import struct
import random
from threading import Event
import time
from SecureUDP import SecureUdp
import os


'''
	EFE: Recive solicitudes de y naranjas. para procesar o pasar
	REQ: ---
	MOD: ---
'''

def inputThread(inputQueue, outputQueue, sock, nodeID, debug):

    file = open("input.out", "w+")
    file.truncate(0)

    while True:
        # Receive a package
        payload, client_address = sock.recvfrom(5000)

        # this determines what type of packet it is (Orange&Orange = 0 or Orange&Blue = 1 )
        if int.from_bytes(payload[:1], byteorder='little') == 0:
            # Orange & Orange
            # BYTE 9 has the orangetarget
            if debug == True:
                pack = ooPackage()
                pack.unserialize(payload)
                file.write("I received a Orange & Orange packetCategory: %d  sn: %d  orangeSource: %d orangeTarget: %d communicationType: %s requestedGraphPosition: %d blueAddressIP: %s blueAddressPort: %d priority: %d \n" % (
                    pack.packetCategory, pack.sn, pack.orangeSource, pack.orangeTarget, pack.communicationType, pack.requestedGraphPosition, pack.blueAddressIP, pack.blueAddressPort, pack.priority))
                payload = pack.serialize()
            targetNode = int.from_bytes(payload[9:10], byteorder='little')
            # If this is a package for me then send it to the inputQueue
            if nodeID == targetNode:
                inputQueue.put(payload)
                if debug == True:
                    file.write("\tthe package is for me\n")
            # If not then just put it to the outputQueue
            else:
                outputQueue.put(payload)
                if debug == True:
                    file.write("\tthe package is not for me\n")

        # Orange & Blue
        else:
            obPack = obPackage()
            # Unserealize the payload to a obPack, in order to access the data inside
            obPack.unserialize(payload)

            # Puts the ip and port given by the sock.recvfrom inside the package
            obPack.blueAddressIP = client_address[0]
            obPack.blueAddressPort = client_address[1]

            if debug == True:
                file.write("I received a Orange & Blue packetCategory: %d  sn: %d  communicationType: %s obtainedGraphPosition: %d blueAddressIP: %s blueAddressPort: %d neighborList: %s \n" % (
                    obPack.packetCategory, obPack.sn, obPack.communicationType, obPack.obtainedGraphPosition, obPack.blueAddressIP, obPack.blueAddressPort, obPack.neighborList))

            # Serialize the package
            byteobPack = obPack.serialize()

            # Puts the package into the inputQueue so the logicalThread can proccess it
            inputQueue.put(byteobPack)
        if debug == True:
            file.flush()


'''
	EFE: Recive solicitudes de y naranjas. para procesar o pasar
	REQ: ---
	MOD: ---
'''

def inputThreadBlue(secureUDPBlue,inputQueue):
    while True:
        obPack = obPackage()
        # Unserealize the payload to a obPack, in order to access the data inside
        payload , addr = secureUDPBlue.recivefrom()
        if int.from_bytes(payload[:1], byteorder='big') == 14:
            obPack2 = obPackage(16,0,0,addr[0],addr[1])
            byteobPack = obPack2.serialize(16)
            inputQueue.put(byteobPack)



'''
	EFE: Envía los paquetes naranja naranja
	REQ: Saber a donde los va a enviar
	MOD: ---
'''

def outputThread(outputQueue, sock, routingTable, debug):

    file = open("output.out", "w+")
    file.truncate(0)

    while True:
        # Takes a package from the queue. If the queue is empty it waits until a package arrives
        bytePacket = outputQueue.get()

        # this determines what type of packet it is (Orange&Orange = 0 or Orange&Blue = 1 )
        if int.from_bytes(bytePacket[:1], byteorder='little') == 0:
            # Orange & Orange
            # BYTE 9 has the orangetarget
            if debug == True:
                pack = ooPackage()
                pack.unserialize(bytePacket)
                file.write("I send a Orange & Orange packetCategory: %d  sn: %d  orangeSource: %d orangeTarget: %d communicationType: %s requestedGraphPosition: %d blueAddressIP: %s blueAddressPort: %d priority: %d \n" % (
                    pack.packetCategory, pack.sn, pack.orangeSource, pack.orangeTarget, pack.communicationType, pack.requestedGraphPosition, pack.blueAddressIP, pack.blueAddressPort, pack.priority))
                bytePacket = pack.serialize()
            targetNode = int.from_bytes(
                bytePacket[9:10], byteorder='little')
            # Routing_table returns the address
            address = routingTable.retrieveAddress(targetNode)

            # Sends the pack to the other Orange node
            try:
                sock.sendto(bytePacket, address)
                if debug == True:
                    file.write("\t Sended to %s:%d\n" %
                               (address[0], address[1]))
            except OSError:
                if debug == True:
                    file.write("Network is unreachable\n")

        else:
            obPack = obPackage()
            # Unserealize the payload to a obPack, in order to access the data inside
            obPack.unserialize(bytePacket)

            # Takes the ip and port
            ip = obPack.blueAddressIP
            port = obPack.blueAddressPort
            client = (ip, port)

            if debug == True:
                file.write("Sending a Orange & Blue packetCategory: %d  sn: %d  communicationType: %s obtainedGraphPosition: %d blueAddressIP: %s blueAddressPort: %d neighborList: %s \n" % (
                    obPack.packetCategory, obPack.sn, obPack.communicationType, obPack.obtainedGraphPosition, obPack.blueAddressIP, obPack.blueAddressPort, obPack.neighborList))

            # Serialize the package
            byteobPack = obPack.serialize()
            # try:
            #     secureUDP.sendto(byteobPack, client)
            # except:
            #     file.write("ERROR: clientAddress is wrong %s:%d" %
            #                (ip, port))

        if debug == True:
            file.flush()


'''
	EFE: 
	REQ:
	MOD:
'''

def timer(timeout, stop_eventMainThread, stop_eventTimerThread):
    i = 0
    # Loops every 0.1s
    while (timeout * 10) > i:
        i += 1
        # Checks if the other thread recieved all the acks
        if stop_eventMainThread.is_set():
            break
        # print(i)
        time.sleep(0.1)
    # We send a signal that the times up
    stop_eventTimerThread.set()
    exit()


'''
	EFE: Procesa los header de los paquetes y realiza las operaciones necesarias
	REQ: Hilos inicializados
	MOD: ---
'''

def requestPackProcessing(outputQueue,table,nodeID,debug,file2,requestNode,priority,sn,blueNodeIP,blueNodePort,pack,blueNodeEnrolls,stop_eventMainThread,processingBlueNode):
    # Marks the node as requested
    table.markNodeAsRequested(pack.requestedGraphPosition)

    if debug == True:
        print("(Request) from: %s requesting the number: %d with the priority: %d " % (
            pack.orangeSource, pack.requestedGraphPosition, pack.priority))

    if pack.requestedGraphPosition == requestNode:  # If I request the same number
        if pack.priority < priority:  # If my priority is bigger then I win

            if debug == True:
                print("\tI won the request of the blueNode: %d (myID: %d myPriority: %d) (otherNodeID: %d otherNodeIDpriority: %d)" % (
                    requestNode, nodeID, priority, pack.orangeSource, pack.priority))

            # Creates a decline package
            declinedPack = ooPackage(
                0, sn, nodeID, pack.orangeSource, 'd', requestNode, blueNodeIP, blueNodePort, priority)
            # Serialize the package
            bytePacket = declinedPack.serialize()
            # Puts the package to the outputQueue
            outputQueue.put(bytePacket)

        elif pack.priority > priority:  # If my priority is smaller then the other node wins

            if debug == True:
                print("\tI lost the request of the blueNode: %d (myID: %d myPriority: %d) (otherNodeID: %d otherNodeIDpriority: %d)" % (
                    requestNode, nodeID, priority, pack.orangeSource, pack.priority))

            # Creates a accept
            acceptPack = ooPackage(
                0, sn, nodeID, pack.orangeSource, 'a', pack.requestedGraphPosition, pack.blueAddressIP, pack.blueAddressPort, pack.priority)

            # Serialize the package
            bytePacket = acceptPack.serialize()

            # Puts the package to the outputQueue
            outputQueue.put(bytePacket)

            # If i was requesting the same number put my requestNode to -1 and clear the timer signals
            requestNode = -1
            
            # Creates a new joinGraph package 
            obPack2 = obPackage(16,0,0,blueNodeIP,blueNodePort)
            byteobPack = obPack2.serialize(16)
            blueNodeEnrolls.put(byteobPack)

            # We send a signal that the other thread should stop.
            stop_eventMainThread.set()

            processingBlueNode = False

        else:  # When both priorities are equal
            if debug == True:
                print("\tWe draw the request of the blueNode: %d (myID: %d myPriority: %d) (otherNodeID: %d otherNodeIDpriority: %d)" % (
                    requestNode, nodeID, priority, pack.orangeSource, pack.priority))
            # Checks the nodeID and the bigger wins
            if nodeID > pack.orangeSource:  # I win

                if debug == True:
                    print("\t\tI won the request of the blueNode:%d SecondRound (myID:%d) (otherNodeID:%d)" % (
                        requestNode, nodeID, pack.orangeSource))

                # Creates a decline package
                declinedPack = ooPackage(
                    0, sn, nodeID, pack.orangeSource, 'd', requestNode, blueNodeIP, blueNodePort, priority)

                # Serialize the package
                bytePacket = declinedPack.serialize()

                # Puts the package to the outputQueue
                outputQueue.put(bytePacket)

            else:  # The other node wins

                if debug == True:
                    print("\t\tI lost the request of the blueNode:%d SecondRound (myID:%d) (otherNodeID:%d)" % (
                        requestNode, nodeID, pack.orangeSource))

                # Creates a accept
                acceptPack = ooPackage(
                    0, sn, nodeID, pack.orangeSource, 'a', pack.requestedGraphPosition, pack.blueAddressIP, pack.blueAddressPort, pack.priority)

                # Serialize the package
                bytePacket = acceptPack.serialize()

                # Puts the package to the outputQueue
                outputQueue.put(bytePacket)

                # Creates a new joinGraph package 
                obPack2 = obPackage(16,0,0,blueNodeIP,blueNodePort)
                byteobPack = obPack2.serialize(16)
                blueNodeEnrolls.put(byteobPack)
                # If i was requesting the same number put my requestNode to -1 and clear the timer signals
                requestNode = -1
                # We send a signal that the other thread should stop.
                stop_eventMainThread.set()

                processingBlueNode = False

    else:  # I did not request that node

        if debug == True:
            print("\tI dont have a problem with the request of the blueNode: %d from the orangeNode: %d" % (
                pack.requestedGraphPosition, pack.orangeSource))

        # Creates an accept package
        acceptPack = ooPackage(0, sn, nodeID, pack.orangeSource, 'a', pack.requestedGraphPosition,
                                pack.blueAddressIP, pack.blueAddressPort, pack.priority)

        # Serialize the package
        bytePacket = acceptPack.serialize()

        # Puts the package to the outputQueue
        outputQueue.put(bytePacket)



def logicalThread(inputQueue, outputQueue, sock, table, nodeID, maxOrangeNodes, debug,secureUDPBlue):

    file2 = open("logicThread.out", "w+")
    file2.truncate(0)

    processingBlueNode = False
    requestNode = -1
    requestNodeWon = False
    blueNodeIP = "0.0.0.0"
    blueNodePort = 8888
    MAXORANGENODES = maxOrangeNodes
    acks = {}  # Map de ACK {key:node id, value:"a"}
    acksWrite = {}
    acksDone = False  # True when all the acks have been received, False otherwise
    acksWriteDone = False  # True when all the acksWrite have been received, False otherwise
    priority = -1
    sn = 0

    stop_eventMainThread = Event()  # If this is true then I received all the acks
    stop_eventTimerThread = Event()  # If this is true then the times up
    flagTimesUp = False  # True when the timer thread finished before receiving all the acks
    # Event object used to send signals from one thread to another
    stop_eventWrite = Event()
    # True when the timer thread finished before receiving all the acks
    flagWriteTimesUp = False

    testingConfli = 0

    blueNodeEnrolls = queue.Queue()  # Pasarla como parámetro
    blueNodes = [] # Tuple with (requestNode,blueNodeIP,blueNodePort). Saves all the connections with the blueNodes
    cheackingDebug = 0
    workDone = False

    while True:
        # If the queue is not empty
        if not inputQueue.empty():
            # Takes a package from the inputQueue.
            bytePacket = inputQueue.get()
            # this determines what type of packet it is (Orange&Orange = 0 or Orange&Blue = 1 )
            if int.from_bytes(bytePacket[:1], byteorder='little') == 0:
                # Orage & Orange

                pack = ooPackage()
                pack.unserialize(bytePacket)

                if pack.communicationType == 'r':  # This a request package
                    requestPackProcessing(outputQueue,table,nodeID,debug,file2,requestNode,priority,sn,blueNodeIP,blueNodePort,pack,blueNodeEnrolls,stop_eventMainThread,processingBlueNode)
                elif pack.communicationType == 'd':  # This is a declined package
                    if debug == True:
                        print("(Declined) from  orangeNode: %d about the request of: %d and my request was: %d" % (
                        pack.orangeSource, pack.requestedGraphPosition, requestNode))

                    # If this is a declined for my request
                    if requestNode == pack.requestedGraphPosition:
                        # We send a signal that the other thread should stop.
                        stop_eventMainThread.set()
                        requestNodeWon = False
                        requestNode = -1
                        processingBlueNode = False

                    else:
                        if debug == True:
                            print("This is a old ack")

                elif pack.communicationType == 'a':  # This is a accept package
                    print("(Accept) from  orangeNode: %d about the request of: %d and my request was: %d" % (
                        pack.orangeSource, pack.requestedGraphPosition, requestNode))

                    # If this is a accept for my request
                    if requestNode == pack.requestedGraphPosition:

                        # Adds the ack to the map
                        acks[pack.orangeSource] = 'a'

                        flagNoAck = False
                        for keyNode in acks:
                            # print(acks[keyNode])
                            if acks[keyNode] == 'x':
                                # print("found one")
                                flagNoAck = True
                                break

                        if flagNoAck == False:  # I got all the acks
                            acksDone = True

                    else:
                        if debug == True:
                            print("This is a old ack")

                elif pack.communicationType == 'w':  # This is a write package
                    print("(Write) the blueNode: %d" %
                          (pack.requestedGraphPosition))
                    # Writes the node IP and Port into the blueTable
                    address = (pack.blueAddressIP, pack.blueAddressPort)
                    table.write(pack.requestedGraphPosition, address)
                    file2.write("Wrote the request %d\n" %
                                (pack.requestedGraphPosition))
                    # Creates the saved package
                    savedPack = ooPackage(0, sn, nodeID, pack.orangeSource, 's',
                                          pack.requestedGraphPosition, blueNodeIP, blueNodePort, pack.priority)
                    byteSavedPack = savedPack.serialize()
                    outputQueue.put(byteSavedPack)
                else:  # This is a saved package
                    print("(Saved) from  orangeNode:%d about the request of: %d my request is: %d" % (
                        pack.orangeSource, pack.requestedGraphPosition, requestNode))

                    if pack.requestedGraphPosition == requestNode:
                        # Adds the ack to the map
                        acksWrite[pack.orangeSource] = 's'

                        flagNoAckSaved = False
                        for keyNode in acksWrite:
                            # print(acksWrite[keyNode])
                            if acksWrite[keyNode] == 'x':
                                # print("found one")
                                flagNoAckSaved = True
                                break

                        if flagNoAckSaved == False:  # I got all the acks
                            # print("Got all writeAcks")
                            # print("Local variables requestWon: %s  mainThread %s  timerThread %s" %(requestNodeWon,stop_eventMainThread.is_set(),stop_eventTimerThread.is_set()))
                            acksWriteDone = True

                    else:
                        if debug == True:
                            print("This is a old ack")

            else:  # Orange & Blue  Tiene que mandar uno a la vez. Hay que ver como implementar eso

                pack = obPackage()
                pack.unserialize(bytePacket,16)
                blueNodeEnrolls.put(pack)

        if not requestNode == -1:
            # Once the acks list is done. Send the write package (if u won the request)
            if acksDone == True:
                if debug == True:
                    print("\tReceived all the acks for the requestNode: %d" % (
                        requestNode))
                file2.write("I won my request %d\n" % (requestNode))
                stop_eventMainThread.set()
                # stop_event.clear()
                requestNodeWon = True
                if requestNodeWon == True:
                    # Writes the address

                    address = (blueNodeIP, blueNodePort)
                    table.write(requestNode, address)
                    flagTimesUp = True
                    # Creates the writePackages
                    for node in range(0, MAXORANGENODES):
                        if not node == nodeID:
                            writePack = ooPackage(
                                0, sn, nodeID, node, 'w', requestNode, blueNodeIP, blueNodePort, priority)
                            byteWritePack = writePack.serialize()
                            outputQueue.put(byteWritePack)

                # Resets the variables
                acks.clear()
                acksDone = False
                flagTimesUp == True
                cheackingDebug += 1
                stop_eventMainThread.clear()
                stop_eventTimerThread.clear()

                # print("Local variables requestWon: %s  mainThread %s  timerThread %s" %(requestNodeWon,stop_eventMainThread.is_set(),stop_eventTimerThread.is_set()))

            # Checks if the acks Timer is done
            else:
                if requestNodeWon == False and stop_eventMainThread.is_set() == False and stop_eventTimerThread.is_set() == True:
                    print("\tTimes Up Acks from the request %d" %
                          (requestNode))
                    stop_eventMainThread.clear()
                    stop_eventTimerThread.clear()
                    flagTimesUp == False
                    # Needs to resend the package
                    sn += 1
                    # print("Local Variables request: %d requestWon %s blueIP: %s bluePort: %d maxOrange: %d acks :%d acksWrite :%d acksDone: %s acksWriteDone: %s Prio: %d sn :%d" %(requestNode,requestNodeWon,blueNodeIP,blueNodePort, MAXORANGENODES,len(acks), len(acksWrite),acksDone,acksWriteDone,priority,sn))

                    for node in range(0, MAXORANGENODES):
                        if acks[node] == 'x':
                            requestPack = ooPackage(
                                0, sn, nodeID, node, 'r', requestNode, blueNodeIP, blueNodePort, priority)
                            if debug == True:
                                print(
                                    "\t\tResending the  request pack to the orangeNode %d" % (node))
                            byteRequestPack = requestPack.serialize()
                            outputQueue.put(byteRequestPack)
                    # Creates the Timer Thread
                    timeout = 5 * sn  # Waits 5 seconds
                    t = threading.Thread(target=timer, args=(
                        timeout, stop_eventMainThread, stop_eventTimerThread, ))
                    t.start()

            # Once the acksWrite list is done. Send the commit package
            if requestNodeWon == True and acksWriteDone == True:
                if debug == True:
                    print("\tReceived all the acksWrite for the requestNode: %d" % (
                        requestNode))
                # if debug == True: print("Creating the commitPackage for the requestNode: %d to the blueNode IP: %s Port: %d" % (requestNode,blueNodeIP,blueNodePort))

                # Creates the commitPackage
                # neighborList = table.obtainNodesNeighborsAdressList(requestNode)
                # for neighbor in neighborList:
                #     if neighbor[2] == 0: #No tengo la IP y Port del nodo
                #         commitPack = obPackage(15,requestNode,neighbor[0])
                #         test = commitPack.serialize(15)
                #         secureUDPBlue.sendto(test,blueNodeIP,blueNodePort)
                #     else:
                #         commitPack = obPackage(16,requestNode,neighbor[0],neighbor[1],neighbor[2])
                #         test = commitPack.serialize(16)
                #         secureUDPBlue.sendto(test,blueNodeIP,blueNodePort)

                if debug == True:
                    print("Creating a (commit) package")

                blueNodes.append((requestNode,blueNodeIP,blueNodePort))
                print("(Done) with the blueNode %d" % (requestNode))

                # Creates the commitPackage
                neighborList = table.obtainNodesNeighborsAdressList(requestNode)
                for neighbor in neighborList:
                    # print(neighbor[0],neighbor[1],neighbor[2])
                    if neighbor[2] == 0: #No tengo la IP y Port del nodo
                        commitPack = obPackage(15,requestNode,neighbor[0])
                        test = commitPack.serialize(15)
                        secureUDPBlue.sendto(test,blueNodeIP,blueNodePort)
                    else:
                        commitPack = obPackage(16,requestNode,neighbor[0],neighbor[1],neighbor[2])
                        test = commitPack.serialize(16)
                        secureUDPBlue.sendto(test,blueNodeIP,blueNodePort)

                #Resets the variables
                processingBlueNode = False
                requestNode = -1
                requestNodeWon = False
                blueNodeIP = "0.0.0.0"
                blueNodePort = 8888
                MAXORANGENODES = maxOrangeNodes
                acksWrite.clear()
                acksWriteDone = False  # True when all the acksWrite have been received, False otherwise
                priority = -1
                sn = nodeID
                flagTimesUp = False

            # Checks if the acksWrite Timer is done
            elif requestNodeWon == True:
                if stop_eventMainThread.is_set() == False and stop_eventTimerThread.is_set() == True:
                    print("\tTimes Up WriteAcks from the requesr %d" %
                          (requestNode))
                    stop_eventMainThread.clear()
                    stop_eventTimerThread.clear()

                    # Needs to resend the package
                    sn += 1
                    # print("Local Variables request: %d requestWon %s blueIP: %s bluePort: %d maxOrange: %d acks :%d acksWrite :%d acksDone: %s acksWriteDone: %s Prio: %d sn :%d" %(requestNode,requestNodeWon,blueNodeIP,blueNodePort, MAXORANGENODES,len(acks), len(acksWrite),acksDone,acksWriteDone,priority,sn))

                    for node in range(0, MAXORANGENODES):
                        if acksWrite[node] == 'x':
                            requestPack = ooPackage(
                                0, sn, nodeID, node, 'w', requestNode, blueNodeIP, blueNodePort, priority)
                            if debug == True:
                                print(
                                    "\t\tResending the  write pack to the orangeNode %d" % (node))
                            byteRequestPack = requestPack.serialize()
                            outputQueue.put(byteRequestPack)
                    # Creates the Timer Thread
                    timeout = 5 * sn  # Waits 5 seconds
                    t = threading.Thread(target=timer, args=(
                        timeout, stop_eventMainThread, stop_eventTimerThread, ))
                    t.start()

        if processingBlueNode == False:

            # If the queue is not empty takes out a new request
            if not blueNodeEnrolls.empty():
                # Takes a new request
                pack = obPackage()
                pack = blueNodeEnrolls.get()
                # Creates the request packages
                
                blueNodeIP = pack.blueAddressIP
                blueNodePort = pack.blueAddressPort
                
                requestNode = table.obtainAvailableNode()
                #print("Testing %d" % (requestNode))
                sn = 0
                # if debug == True: print("(Enroll) from the blueNode IP: %s Port: %d requesting %d" % (pack.blueAddressIP,pack.blueAddressPort,requestNode))

                if not requestNode == -1:  # Checks if there is more requestNodes
                    if debug == True:
                        print("NodeId: %d"%(pack.nodeID))
                        print("(Enroll) from the blueNode IP: %s Port: %d requesting %d" % (
                            pack.blueAddressIP, pack.blueAddressPort, requestNode))
                    testingConfli += 1
                    priority = random.randrange(4294967294)
                    # Marks the node as requested
                    table.markNodeAsRequested(requestNode)
                    flagTimesUp == False
                    processingBlueNode = True
                    stop_eventMainThread.clear()
                    stop_eventTimerThread.clear()

                    # print("Local Variables request: %d requestWon %s blueIP: %s bluePort: %d maxOrange: %d acks :%d acksWrite :%d acksDone: %s acksWriteDone: %s Prio: %d sn :%d" %(requestNode,requestNodeWon,blueNodeIP,blueNodePort, MAXORANGENODES,len(acks), len(acksWrite),acksDone,acksWriteDone,priority,sn))

                    for node in range(0, MAXORANGENODES):

                        if node == nodeID:
                            acks[node] = 'a'
                            acksWrite[node] = 's'
                        elif not node == nodeID:
                            # Fills with an x (not ack recived)-------------------------------------------------
                            acks[node] = "x"
                            acksWrite[node] = 'x'
                            requestPack = ooPackage(
                                0, sn, nodeID, node, 'r', requestNode, blueNodeIP, blueNodePort, priority)
                            # if debug == True: requestPack.print_data()
                            #print("NodeID: %d, node: %d" % (nodeID, node))
                            byteRequestPack = requestPack.serialize()
                            outputQueue.put(byteRequestPack)

                    # Creates the Timer Thread
                    timeout = 5 #Waits 5s
                    t = threading.Thread(target=timer, args=(
                        timeout, stop_eventMainThread, stop_eventTimerThread, ))
                    t.start()

                else:
                    print("No more requestNumers available")


            #Sends the graphComplete package to the blueNodes, when theres no more blueNodesID's to assign
            if table.tableIsDone() == True and workDone == False:
                for element in range(len(blueNodes)):
                    addr  = blueNodes[element]

                        
                    completeGraph = obPackage(17)
                    bytePacket =  completeGraph.serialize(17)
                    print("sending completeGraph to ",addr[1],str(addr[2]))
                    secureUDPBlue.sendto(bytePacket,addr[1],addr[2])
                    workDone = True

        file2.flush()


class orangeNode:
    '''
		EFE: Construye un nodo Naranja, con valores por defecto o inicializados
		REQ: ---
		MOD: ---
    '''

    def __init__(self, port=8888, nodeID=0,  routingTableDir="routingTable.txt", blueGraphDir="Grafo_Referencia.csv"):
        # Especificaciones del paquete
        self.ip = 0
        self.port = port
        self.nodeID = nodeID
        self.routingTableDir = routingTableDir
        self.blueGraphDir = blueGraphDir
        self.debug = True

    '''
		EFE: Levanta el servidor, las colas, routingTable, blueNodeTable y crea los hilos
		REQ: ---
		MOD: ---
	'''

    def run(self):
        inputQueue = queue.Queue()
        outputQueue = queue.Queue()

        # Create the routingTable
        routingTable = RoutingTable(self.routingTableDir)
        maxOrangeNodes = len(routingTable.table)

        # Creates the orange graph and the blueNodeTable
        table = blueNodeTable(self.blueGraphDir)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.ip = s.getsockname()[0]
        s.close()

        # Starts the UDP server
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.ip,self.port))
        print("Listening Oranges on ip: %s port %d Im orange: %d" %
              (sock.getsockname()[0], self.port, self.nodeID))

        # Starts the UDP Safe
        SecureUdpBlue = SecureUdp(100,1,True) #ventana de 100 con timeout de 1s
        print("Listening Blues on ip: %s port %d Im orange: %d" %
              (SecureUdpBlue.sock.getsockname()[0], SecureUdpBlue.sock.getsockname()[1], self.nodeID))
        # Creates the Threads
        t = threading.Thread(target=inputThread, args=(
            inputQueue, outputQueue, sock, self.nodeID, self.debug, ))
        t.start()
       

        t2 = threading.Thread(target=outputThread, args=(
            outputQueue, sock, routingTable, self.debug, ))
        t2.start()
           
        t3 = threading.Thread(target=logicalThread, args=(
            inputQueue, outputQueue, sock, table, self.nodeID, maxOrangeNodes,self.debug,SecureUdpBlue))
        t3.start()

        t4 = threading.Thread(target=inputThreadBlue, args=(SecureUdpBlue,inputQueue,))
        t4.start()


if __name__== "__main__":

	if len(sys.argv) == 3:		
		orange = orangeNode(int(sys.argv[1]),int(sys.argv[2]),"routingTable.txt", "../Grafo.csv")
		orange.run()
	else:
		print("Error: need the ip and port of the server and the number of the orangeNode")
		exit()

