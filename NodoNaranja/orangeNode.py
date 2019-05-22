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


class orangeNode:
	

    def __init__(self, ip = '0.0.0.0', port = 8888, nodeID = 0 ,  routingTableDir = "routingTable.txt", blueGraphDir = "Grafo_Referencia.csv"):
        self.ip = ip
        self.port = port
        self.nodeID = nodeID
        self.routingTableDir = routingTableDir
        self.blueGraphDir = blueGraphDir
        self.debug = True

    def run(self):
        server = (self.ip, self.port)
        inputQueue = queue.Queue()
        outputQueue = queue.Queue()

        ##Creates the routingtable
        routingTable =  RoutingTable(self.routingTableDir)
        maxOrangeNodes = len(routingTable.table)
                
        #Creates the orange graph and the blueNodeTable
        table = blueNodeTable(self.blueGraphDir)


        #Starts the UDP server
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(server)
        print("Listening on ip: %s port %d Im orange: %d"  % (self.ip,self.port,self.nodeID))
        
        ##Creates the Threads
        t = threading.Thread(target=inputThread, args=(inputQueue,outputQueue,sock,self.nodeID,self.debug ))
        t.start()
        t2 = threading.Thread(target=outputThread, args=(outputQueue,sock,routingTable,self.debug ))
        t2.start()
        t3 = threading.Thread(target=logicalThread, args=(inputQueue,outputQueue,sock,table,self.nodeID,maxOrangeNodes,self.debug  ))
        t3.start()
        
        #Testing
        while True:
         test = int(input())
         if test == 1:
          neighborList = []
          testPack = obPackage(1,2,'e',0,"0.0.0.0",2,neighborList)
          ByteTestPack = testPack.serialize()
          print("\n")
          inputQueue.put(ByteTestPack)
        
        
       
def inputThread(inputQueue,outputQueue,sock,nodeID,debug):


    file = open("input.out","w+")
    file.truncate(0)
    
    while True:
      #Receive a package
      payload, client_address = sock.recvfrom(5000)

      #this determines what type of packet it is (Orange&Orange = 0 or Orange&Blue = 1 )
      if int.from_bytes(payload[:1],byteorder='little') == 0: 
         #Orange & Orange
         ##BYTE 9 has the orangetarget
         if debug == True: 
                 pack = ooPackage()  
                 pack.unserialize(payload)
                 file.write("I received a Orange & Orange packetCategory: %d  sn: %d  orangeSource: %d orangeTarget: %d communicationType: %s requestedGraphPosition: %d blueAddressIP: %s blueAddressPort: %d priority: %d \n" % (pack.packetCategory,pack.sn,pack.orangeSource, pack.orangeTarget,pack.communicationType, pack.requestedGraphPosition, pack.blueAddressIP, pack.blueAddressPort,pack.priority))
                 payload = pack.serialize()          
         targetNode = int.from_bytes(payload[9:10],byteorder='little')
         #If this is a package for me then send it to the inputQueue
         if nodeID == targetNode:
           inputQueue.put(payload)
           if debug == True: file.write("\tthe package is for me\n")
         #If not then just put it to the outputQueue
         else:
            outputQueue.put(payload)
            if debug == True: file.write("\tthe package is not for me\n")
         
      ##Orange & Blue     
      else:
         obPack = obPackage()
       
         #Unserealize the payload to a obPack, in order to access the data inside
         obPack.unserialize(payload)
          
         #Puts the ip and port given by the sock.recvfrom inside the package
         obPack.blueAddressIP = client_address[0]
         obPack.blueAddressPort = client_address[1]  
         
         if debug == True:
                 file.write("I received a Orange & Blue packetCategory: %d  sn: %d  communicationType: %s obtainedGraphPosition: %d blueAddressIP: %s blueAddressPort: %d neighborList: %s \n" % (obPack.packetCategory,obPack.sn,obPack.communicationType, obPack.obtainedGraphPosition, obPack.blueAddressIP, obPack.blueAddressPort,obPack.neighborList))
         
         #Serialize the package
         byteobPack = obPack.serialize()       
         
         #Puts the package into the inputQueue so the logicalThread can proccess it
         inputQueue.put(byteobPack)
      if debug == True: file.flush()   
   

def outputThread(outputQueue,sock,routingTable,debug):

    file = open("output.out","w+")
    file.truncate(0)
    
    while True:
      ##Takes a package from the queue. If the queue is empty it waits until a package arrives
      bytePacket = outputQueue.get()
  
      #this determines what type of packet it is (Orange&Orange = 0 or Orange&Blue = 1 )
      if int.from_bytes(bytePacket[:1],byteorder='little') == 0: 
       #Orange & Orange
       ##BYTE 9 has the orangetarget    
          if debug == True: 
                
                 pack = ooPackage()  
                 pack.unserialize(bytePacket)
                 file.write("I send a Orange & Orange packetCategory: %d  sn: %d  orangeSource: %d orangeTarget: %d communicationType: %s requestedGraphPosition: %d blueAddressIP: %s blueAddressPort: %d priority: %d \n" % (pack.packetCategory,pack.sn,pack.orangeSource, pack.orangeTarget,pack.communicationType, pack.requestedGraphPosition, pack.blueAddressIP, pack.blueAddressPort,pack.priority))
                 bytePacket = pack.serialize()     
          targetNode = int.from_bytes(bytePacket[9:10],byteorder='little')
          #Routing_table returns the address
          address = routingTable.retrieveAddress(targetNode)

          #Sends the pack to the other Orange node
          sock.sendto(bytePacket,address)
          if debug == True: file.write("\t Sended to %s:%d\n"%(address[0],address[1]))       
          
      else:    
         obPack = obPackage()
       
         #Unserealize the payload to a obPack, in order to access the data inside
         obPack.unserialize(bytePacket)
          
         #Takes the ip and port
         ip = obPack.blueAddressIP 
         port = obPack.blueAddressPort
         client = (ip,port)
         
         if debug == True:
                 file.write("Sending a Orange & Blue packetCategory: %d  sn: %d  communicationType: %s obtainedGraphPosition: %d blueAddressIP: %s blueAddressPort: %d neighborList: %s \n" % (obPack.packetCategory,obPack.sn,obPack.communicationType, obPack.obtainedGraphPosition, obPack.blueAddressIP, obPack.blueAddressPort,obPack.neighborList))
         
         #Serialize the package
         byteobPack = obPack.serialize()       
         try:
          sock.sendto(byteobPack,client)      
         except:
          file.write("ERROR: clientAddress is wrong %s:%d"%(ip,port))
         
        
      if debug == True: file.flush()         

def logicalThread(inputQueue,outputQueue,sock,table,nodeID,maxOrangeNodes,debug):


    requestNode = -1
    requestNodeWon = True
    blueNodeIP = "0.0.0.0"
    blueNodePort = 8888
    MAXORANGENODES = maxOrangeNodes
    acks = []
    acksWrite = []
    acksDone = False #True when all the acks have been received, False otherwise
    acksWriteDone = False #True when all the acksWrite have been received, False otherwise
    priority = -1
    sn= nodeID
       
    stop_event = Event() # Event object used to send signals from one thread to another
    flagTimesUp = False #True when the timer thread finished before receiving all the acks
    stop_eventWrite = Event() # Event object used to send signals from one thread to another
    flagWriteTimesUp = False #True when the timer thread finished before receiving all the acks
    
    while True:
     #If the queue is not empty
     if not inputQueue.empty():
         ##Takes a package from the inputQueue. If the queue is empty it waits until a package arrives
         bytePacket = inputQueue.get()    
         #this determines what type of packet it is (Orange&Orange = 0 or Orange&Blue = 1 )
         if int.from_bytes(bytePacket[:1],byteorder='little') == 0:  #Orage & Orange
            pack = ooPackage()
            pack.unserialize(bytePacket)
            if pack.communicationType == 'r':   ##This a request package
                
               if debug == True: print("(Request) from: %s requesting the number: %d with the priority: %d " % (pack.orangeSource,pack.requestedGraphPosition,pack.priority))
               
               if pack.requestedGraphPosition == requestNode: ##If I request the same number
                  if pack.priority < priority: ##If my priority is bigger then I win
                           
                      if debug == True: print("\tI won the request of the blueNode: %d (myID: %d myPriority: %d) (otherNodeID: %d otherNodeIDpriority: %d)" % (requestNode,nodeID,priority,pack.orangeSource,pack.priority))
                      
                      #Creates a decline package
                      declinedPack = ooPackage(0,sn,nodeID,pack.orangeSource,'d',requestNode,blueNodeIP,blueNodePort,priority)
                      
                      #Serialize the package
                      bytePacket = declinedPack.serialize()
                      
                      #Puts the package to the outputQueue
                      outputQueue.put(bytePacket)
                      
                  elif pack.priority > priority: ##If my priority is smaller then the other node wins    
                      if debug == True: print("\tI lost the request of the blueNode: %d (myID: %d myPriority: %d) (otherNodeID: %d otherNodeIDpriority: %d)" % (requestNode,nodeID,priority,pack.orangeSource,pack.priority))    
                                    
                      #Creates a accept
                      acceptPack = ooPackage(0,sn,nodeID,pack.orangeSource,'a',pack.requestedGraphPosition,pack.blueAddressIP,pack.blueAddressPort,pack.priority)
                      
                      #Serialize the package
                      bytePacket = acceptPack.serialize()
                      
                      #Puts the package to the outputQueue
                      outputQueue.put(bytePacket)
                                        
                  else: #When both priorities are equal 
                      if debug == True: print("\tWe draw the request of the blueNode: %d (myID: %d myPriority: %d) (otherNodeID: %d otherNodeIDpriority: %d)" % (requestNode,nodeID,priority,pack.orangeSource,pack.priority))                  
                      
                      #Checks the nodeID and the bigger wins
                      if nodeID > pack.orangeSource: #I win
                            
                           if debug == True: print("\t\tI won the request of the blueNode:%d SecondRound (myID:%d) (otherNodeID:%d)" % (requestNode,nodeID,pack.orangeSource))                       
                           
                           #Creates a decline package
                           declinedPack = ooPackage(0,sn,nodeID,pack.orangeSource,'d',requestNode,blueNodeIP,blueNodePort,priority)
                           
                           #Serialize the package
                           bytePacket = declinedPack.serialize()
                           
                           #Puts the package to the outputQueue
                           outputQueue.put(bytePacket)
                                             
                      else: ## The other node wins
                             
                           if debug == True: print("\t\tI lost the request of the blueNode:%d SecondRound (myID:%d) (otherNodeID:%d)" % (requestNode,nodeID,pack.orangeSource))       
                                                
                           #Creates a accept
                           acceptPack = ooPackage(0,sn,nodeID,pack.orangeSource,'a',pack.requestedGraphPosition,pack.blueAddressIP,pack.blueAddressPort,pack.priority)
                           
                           #Serialize the package
                           bytePacket = acceptPack.serialize()
                           
                           #Puts the package to the outputQueue
                           outputQueue.put(bytePacket)            
                                             
               else: #I did not request that node   
                        
                  if debug == True: print("\tI dont have a problem with the request of the blueNode: %d from the orangeNode: %d" % (pack.requestedGraphPosition,pack.orangeSource))                   
                  
                  #Creates an accept package
                  acceptPack = ooPackage(0,sn,nodeID,pack.orangeSource,'a',pack.requestedGraphPosition,pack.blueAddressIP,pack.blueAddressPort,pack.priority)
                  
                  #Serialize the package
                  bytePacket = acceptPack.serialize()
                  
                  #Puts the package to the outputQueue
                  outputQueue.put(bytePacket)  
                  
                  #Marks the node as requested                       
                  table.markNodeAsRequested(pack.requestedGraphPosition) 
                    
            elif pack.communicationType == 'd': #This is a declined package   
                           
                 if debug == True: print("(Declined) from  orangeNode: %d about the request of: %d and my request was: %d" % (pack.orangeSource,pack.requestedGraphPosition,requestNode))                  
                 # We send a signal that the other thread should stop.
                 stop_event.set()  
                 #Append the ack to the acks list
                 acks.append('d')
                 requestNodeWon = False
                 #Checks if the acks list is done. The list is done when the size is MAXORANGENODES - 1
                 if len(acks) == MAXORANGENODES - 1:
                       acksDone = True        
                      
                       
            elif pack.communicationType == 'a': #This is a accept package     
                 print("(Accept) from  orangeNode: %d about the request of: %d and my request was: %d" % (pack.orangeSource,pack.requestedGraphPosition,requestNode))
                 #Append the ack to the acks list
                 acks.append('a')
                 
                 #Checks if the acks list is done. The list is done when the size is MAXORANGENODES - 1
                 if len(acks) == MAXORANGENODES - 1:
                       acksDone = True
                       # We send a signal that the other thread should stop.
                       stop_event.set()
                       
                                 
              
            elif pack.communicationType == 'w': #This is a write package  
                 print("(Write) the blueNode: %d" % (pack.requestedGraphPosition))             
                 #Writes the node IP and Port into the blueTable   
                 address = (pack.blueAddressIP,pack.blueAddressPort)
                 table.write(pack.requestedGraphPosition,address)
                 
                 #Creates the saved package
                 savedPack = ooPackage(0,sn,nodeID,pack.orangeSource,'s',pack.requestedGraphPosition,blueNodeIP,blueNodePort,pack.priority)
                 byteSavedPack = savedPack.serialize()
                 outputQueue.put(byteSavedPack)            
            else: ##This is a saved package      
                  print("(Saved) from  orangeNode:%d about the request of: %d my request is: %d" % (pack.orangeSource,pack.requestedGraphPosition,requestNode))                
                  #Apeend the ack to the acksWrite list
                  acksWrite.append('s')
                  
                  #Checks if the list is done. The list is done when the size is MAXORANGENODES-1              
                  if len(acksWrite) == MAXORANGENODES-1:
                      ##Stop the timer
                      acksWriteDone = True
                      
         else: #Orange & Blue  Tiene que mandar uno a la vez. Hay que ver como implementar eso
         
           pack = obPackage()
           pack.unserialize(bytePacket)
         
           if pack.communicationType == 'e': #Enroll package
              
              if debug == True: print("I just receive a enroll package from the blueNode IP: %s Port: %d" % (pack.blueAddressIP,pack.blueAddressPort))
                

              #Creates the request packages
              blueNodeIP = pack.blueAddressIP
              blueNodePort = pack.blueAddressPort
              requestNode = table.obtainAvailableNode()
              if not requestNode == -1: ##Checks if there is more requestNodes 
                  priority = random.randrange(4294967294)  
                  #Marks the node as requested                       
                  table.markNodeAsRequested(requestNode) 
                  flagTimesUp == False  
                  for node in range(0,MAXORANGENODES):
                     if not node == nodeID: 
                         requestPack = ooPackage(0,sn,nodeID,node,'r',requestNode,blueNodeIP,blueNodePort,priority)
                         #if debug == True: requestPack.print_data()
                         byteRequestPack = requestPack.serialize()
                         outputQueue.put(byteRequestPack)
                         
                  ##Creates the Timer Thread
                  timeout = 5 #Waits 5 seconds
                  t = threading.Thread(target=timer, args=(timeout,stop_event, ))
                  t.start()
                         
              else:
                 print("No more requestNumers available")            
        

       
     if not requestNode == -1:  
         #Once the acks list is done. Send the write package (if u won the request)
         if acksDone == True:
             if debug == True: print("\tReceived all the acks for the requestNode: %d" % (requestNode)) 
             stop_event.clear()
             
             if requestNodeWon == True:
                #Writes the address
                address = (blueNodeIP,blueNodePort)
                table.write(requestNode,address)
                flagTimesUp = True
                #Creates the writePackages
                for node in range(0,MAXORANGENODES):
                   if not node == nodeID: 
                       writePack = ooPackage(0,sn,nodeID,node,'w',requestNode,blueNodeIP,blueNodePort,priority)
                       byteWritePack = writePack.serialize()
                       outputQueue.put(byteWritePack)
     
                       
                       
             else:     
                requestNode = -1
                requestNodeWon = True
                blueNodeIP = "0.0.0.0"
                blueNodePort = 8888
                acksWrite = []
                acksWriteDone = False #True when all the acksWrite have been received, False otherwise
                priority = -1
                sn= nodeID  
                       
             #Resets the variables
             acks = []
             acksDone = False       
             flagTimesUp == True      
                    
                    
         #Checks if the acks Timer is done
         else:
            if stop_event.is_set() and flagTimesUp == False: 
               print("Times Up")
               stop_event.clear()
               flagTimesUp == False
               ##Needs to resend the package           
               for node in range(0,MAXORANGENODES):
                  if not node == nodeID: 
                     requestPack = ooPackage(0,sn,nodeID,node,'r',requestNode,blueNodeIP,blueNodePort,priority)
                     if debug == True: requestPack.print_data()
                     byteRequestPack = requestPack.serialize()
                     outputQueue.put(byteRequestPack)
               ##Creates the Timer Thread
               timeout = 5 #Waits 5 seconds
               t = threading.Thread(target=timer, args=(timeout,stop_event, ))
               t.start()
                 
                    
         #Once the acksWrite list is done. Send the commit package
         if requestNodeWon == True and acksWriteDone == True:
            if debug == True: print("\tReceived all the acksWrite for the requestNode: %d" % (requestNode)) 
            #if debug == True: print("Creating the commitPackage for the requestNode: %d to the blueNode IP: %s Port: %d" % (requestNode,blueNodeIP,blueNodePort))
            
            #Creates the commitPackage
            neighborList = table.obtainNodesNeighborsAdressList(requestNode)
            commitPack = obPackage(1,sn,'c',requestNode,blueNodeIP,blueNodePort,neighborList)
            #commitPack.print_data()
            byteCommitPack = commitPack.serialize()
            outputQueue.put(byteCommitPack)   
             
            requestNode = -1
            requestNodeWon = True
            blueNodeIP = "0.0.0.0"
            blueNodePort = 8888
            MAXORANGENODES = maxOrangeNodes
            acksWrite = []
            acksWriteDone = False #True when all the acksWrite have been received, False otherwise
            priority = -1
            sn= nodeID 
            flagTimesUp = False  
            stop_event.clear()       



def timer(timeout,stop_event):
    i = 0
    while timeout > i:
        i += 1
        #print(i)
        time.sleep(1)
        # Here we make the check if the other thread sent a signal to stop execution.
        if stop_event.is_set():
            break
      
    # We send a signal that the other thread should stop.
    stop_event.set()

