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



class orangeNode:
	

    def __init__(self, ip = '0.0.0.0', port = 8888, nodeID = 0 ,  routingTableDir = "routingTable.txt", blueGraphDir = "Grafo_Referencia.csv"):
        self.ip = ip
        self.port = port
        self.nodeID = nodeID
        self.routingTableDir = routingTableDir
        self.blueGraphDir = blueGraphDir

    def run(self):
        server = (self.ip, self.port)
        inputQueue = queue.Queue()
        outputQueue = queue.Queue()

        ##Creates the routingtable
        routingTable =  RoutingTable(self.routingTableDir)

        #Starts the UDP server
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(server)
        print("Listening on " + self.ip + ":" + str(self.port))
        
        ##Creates the Threads
        t = threading.Thread(target=inputThread, args=(inputQueue,sock,self.nodeID ))
        #t.start()
        t2 = threading.Thread(target=outputThread, args=(outputQueue,sock,routingTable ))
        t2.start()
        t3 = threading.Thread(target=logicalThread, args=(inputQueue,outputQueue,sock,self.blueGraphDir,self.nodeID  ))
        t3.start()
        
        #Testing
        while True:
         test = int(input())
         if test == 1:
          neighborList = []
          testPack = obPackage(1,2,'e',0,"0.0.0.1",2,neighborList)
          ByteTestPack = testPack.serialize()
          inputQueue.put(ByteTestPack)
        
        
       
def inputThread(inputQueue,sock,nodeID):
    while True:
      #Receive a package
      payload, client_address = sock.recvfrom(5000)

      #this determines what type of packet it is (Orange&Orange = 0 or Orange&Blue = 1 )
      if int.from_bytes(payload[:1],byteorder='little') == 0: 
         #Orange & Orange
         ##BYTE 9 has the orangetarget
         targetNode = int.from_bytes(payload[9:10],byteorder='little')
        
         #If this is a package for me then send it to the inputQueue
         if nodeID == targetNode:
            
            inputQueue.put(payload)
         #If not then just put it to the outputQueue
         else:
           outputQueue.put(payload)
         
      ##Orange & Blue     
      else:
         obPack = obPackage()
         obPack.unserialize(payload)
         obPack.blueAddressIP = client_address[0]
         obPack.blueAddressPort = client_address[1]  
         
         byteobPack = obPack.serialize()       
         inputQueue.put(byteobPack)
         
   

def outputThread(outputQueue,sock,routingTable):
    while True:
      ##Takes a package from the queue. If the queue is empty it waits until a package arrives
      bytePacket = outputQueue.get()
  
      #this determines what type of packet it is (Orange&Orange = 0 or Orange&Blue = 1 )
      if int.from_bytes(bytePacket[:1],byteorder='little') == 0: 
       #Orange & Orange
       ##BYTE 9 has the orangetarget    
          targetNode = int.from_bytes(bytePacket[9:10],byteorder='little')
          #Routing_table returns the address
          address = routingTable.retrieveAddress(targetNode)

          sock.sendto(bytePacket,address)
      else:
        print("This is a blue to orange pack, still needs the implementation")
        address = routingTable.retrieveAddress(0)
        sock.sendto(bytePacket,address)
 

def logicalThread(inputQueue,outputQueue,sock,blueGraphDir,nodeID):

    #Creates the orange graph and the blueNodeTable
    table = blueNodeTable(blueGraphDir)
    requestNode = -1
    blueNodeIP = "0.0.0.0"
    blueNodePort = 8888
    MAXORANGENODES = 6
    acks = []
    acksDone = False #True when all the acks have been received, False otherwise
    acksWrite = []
    acksWriteDone = False #True when all the acksWrite have been received, False otherwise
    priority = -1
    sn= nodeID
    
    while True:

     ##Takes a package from the inputQueue. If the queue is empty it waits until a package arrives
     bytePacket = inputQueue.get()
  
     #this determines what type of packet it is (Orange&Orange = 0 or Orange&Blue = 1 )
     if int.from_bytes(bytePacket[:1],byteorder='little') == 0:  #Orage & Orange
        pack = ooPackage()
        pack.unserialize(bytePacket)
        if pack.communicationType == 'r':   ##This a request package
           print("This is a request pack from: %s requesting the number: %d with the priority: %d " % (pack.orangeSource,pack.requestedGraphPosition,pack.priority))
           if pack.requestedGraphPosition == requestNode: ##If I request the same number
              if pack.priority < priority: ##If my priority is bigger then I win
                  print("I won the request of the blueNode: %d (myID: %d myPriority: %d) (otherNodeID: %d otherNodeIDpriority: %d)" % (requestNode,nodeID,priority,pack.orangeSource,pack.priority))
                  #Creates a decline package
                  declinePack = ooPackage(0,sn,nodeID,pack.orangeSource,'d',requestNode,blueNodeIP,blueNodePort,priority)
                  #Serialize the package
                  bytePacket = declinedPack.serialize()
                  #Puts the package to the outputQueue
                  outputQueue.put(bytePacket)
              elif pack.priority > priority: ##If my priority is smaller then the other node wins    
                  print("I lost the request of the blueNode: %d (myID: %d myPriority: %d) (otherNodeID: %d otherNodeIDpriority: %d)" % (requestNode,nodeID,priority,pack.orangeSource,pack.priority))                  
                  #Creates a accept
                  acceptPack = ooPackage(0,sn,nodeID,pack.orangeSource,'a',pack.requestedGraphPosition,pack.blueAddressIP,pack.blueAddressPort,pack.priority)
                  #Serialize the package
                  bytePacket = acceptPack.serialize()
                  #Puts the package to the outputQueue
                  outputQueue.put(bytePacket)                  
              else: #When both priorities are equal 
                  print("We draw the request of the blueNode: %d (myID: %d myPriority: %d) (otherNodeID: %d otherNodeIDpriority: %d)" % (requestNode,nodeID,priority,pack.orangeSource,pack.priority))                  
                  #Checks the nodeID and the bigger wins
                  if nodeID > pack.orangeSource: #I win
                       print("I won the request of the blueNode:%d SecondRound (myID:%d) (otherNodeID:%d)" % (requestNode,nodeID,pack.orangeSource))                       
                       #Creates a decline package
                       declinePack = ooPackage(0,sn,nodeID,pack.orangeSource,'d',requestNode,blueNodeIP,blueNodePort,priority)
                       #Serialize the package
                       bytePacket = declinedPack.serialize()
                       #Puts the package to the outputQueue
                       outputQueue.put(bytePacket)                  
                  else: ## The other node wins
                       print("I lost the request of the blueNode:%d SecondRound (myID:%d) (otherNodeID:%d)" % (requestNode,nodeID,pack.orangeSource))                            
                       #Creates a accept
                       acceptPack = ooPackage(0,sn,nodeID,pack.orangeSource,'a',pack.requestedGraphPosition,pack.blueAddressIP,pack.blueAddressPort,pack.priority)
                       #Serialize the package
                       bytePacket = acceptPack.serialize()
                       #Puts the package to the outputQueue
                       outputQueue.put(bytePacket)                              
           else: #I did not request that node         
              print("I dont have a problem with the request of the blueNode: %d from the orangeNode: %d" % (pack.requestedGraphPosition,pack.orangeSource))                   
              #Creates a accept
              acceptPack = ooPackage(0,sn,nodeID,pack.orangeSource,'a',pack.requestedGraphPosition,pack.blueAddressIP,pack.blueAddressPort,pack.priority)
              #Serialize the package
              bytePacket = acceptPack.serialize()
              #Puts the package to the outputQueue
              outputQueue.put(bytePacket)  
              
              #Marks the node as requested                       
              table.markNodeAsRequested(pack.requestedGraphPosition)   
        elif pack.communicationType == 'd': #This is a declined package             
             print("Received ack type declined from  orangeNode: %d about the request of the blueNode: %d and my request was: %d" % (pack.orangeSource,pack.requestedGraphPosition,requestNode))             
             #Append the ack to the acks list
             acks.append('d')
             #Checks if the acks list is done. The list is done when the size is MAXORANGENODES - 1
             if len(acks) == MAXORANGENODES - 1:
                   acksDone = True        
                   print("Received all the acks for the requestNode: %d" % (requestNode))                      
        elif pack.communicationType == 'a': #This is a accept package     
             print("Received ack type accept from  orangeNode: %d about the request of the blueNode: %d and my request was: %d" % (pack.orangeSource,pack.requestedGraphPosition,requestNode))
             #Append the ack to the acks list
             acks.append('a')
             
             #Checks if the acks list is done. The list is done when the size is MAXORANGENODES - 1
             if len(acks) == MAXORANGENODES - 1:
                   acksDone = True          
                   print("Received all the acks for the requestNode: %d" % (requestNode))             
        elif pack.communicationType == 'w': #This is a write package  
             print("Received write package from  orangeNode: %d about the request of the blueNode: %d" % (pack.orangeSource,pack.requestedGraphPosition))             
             #Writes the node IP and Port into the blueTable   
             address = (pack.blueAddressIP,pack.blueAddressPort)
             table.write(pack.requestedGraphPosition,address)
             
             #Creates the saved package
             savedPack = ooPackage(0,sn,nodeID,pack.orangeSource,'s',pack.requestedGraphPosition,blueNodeIP,blueNodePort,pack.priority)
             byteSavedPack = savedPack.serialize()
             outputQueue.put(byteSavedPack)            
        else: ##This is a saved package      
              print("Received saved ack from  orangeNode:%d about the request of the blueNode: %d my request is: %d" % (pack.orangeSource,pack.requestedGraphPosition,requestNode))                
              #Apeend the ack to the acksWrite list
              acksWrite.append('s')
              
              #Checks if the list is done. The list is done when the size is MAXORANGENODES-1              
              if len(acksWrite) == MAXORANGENODES-1:
                  ##Stop the timer
                  print("All the nodes wrote the blueNode %d with the ip %s port %d" % (requestNode,blueNodeIP,blueNodePort))
                  
     else: #Orange & Blue  Tiene que mandar uno a la vez. Hay que ver como implementar eso
         
         pack = obPackage()
         pack.unserialize(bytePacket)
         
         if pack.communicationType == 'e': #Enroll package
            print("I just receive a enroll package from the blueNode IP: %s Port: %d" % (pack.blueAddressIP,pack.blueAddressPort))
            #Creates the request packages
            blueNodeIP = pack.blueAddressIP
            blueNodePort = pack.blueAddressPort
            requestNode = table.obtainAvailableNode()
            priority = random.randrange(4294967294)

            for node in range(0,MAXORANGENODES):
               if not node == nodeID: 
                   requestPack = ooPackage(0,sn,nodeID,node,'r',requestNode,blueNodeIP,blueNodePort,priority)
                   requestPack.print_data()
                   byteRequestPack = requestPack.serialize()
                   outputQueue.put(byteRequestPack)
                
         
     #Once the acks list is done. Send the write package
     if acksDone == True:
         #Creates the writePackages
         for node in range(0,MAXORANGENODES):
            if not node == nodeID: 
                writePack = ooPackage(0,sn,nodeID,node,'w',requestNode,blueNodeIP,blueNodePort,priority)
                writePack.print_data()
                byteWritePack = writePack.serialize()
                outputQueue.put(byteWritePack) 
                
                
     #Once the acksWrite list is done. Send the commit package
     if acksDone == True:
         print("Creating the commitPackage for the requestNode: %d to the blueNode IP: %s Port: %d" % (requestNode,blueNodeIP,blueNodePort))
         #Creates the commitPackage
         neighborList = table.obtainNodesNeighborsAdressList(requestNode)
         commitPack = obPackage(1,sn,nodeID,node,'c',requestNode,blueNodeIP,blueNodePort,neighborList)
         commitPack.print_data()
         byteCommitPack = writePack.serialize()
         outputQueue.put(byteCommitPack)                    



   



