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
          testPack = obPackage(1,2,'e',0,"0.0.0.1",2,neighborList)
          ByteTestPack = testPack.serialize()
          inputQueue.put(ByteTestPack)
        
        
       
def inputThread(inputQueue,outputQueue,sock,nodeID,debug):
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
                 print("I received a Orange & Orange Package category %d sn %d  source %d  target %d type %s request %d " % (pack.packetCategory,pack.sn,pack.orangeSource,pack.orangeTarget,pack.communicationType,pack.requestedGraphPosition)) 
                 payload = pack.serialize()          
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
         if debug == True: print("I received a Orange & Orange Package")         
         #Unserealize the payload to a obPack, in order to access the data inside
         obPack.unserialize(payload)
          
         #Puts the ip and port given by the sock.recvfrom inside the package
         obPack.blueAddressIP = client_address[0]
         obPack.blueAddressPort = client_address[1]  
         
         #Serialize the package
         byteobPack = obPack.serialize()       
         
         #Puts the package into the inputQueue so the logicalThread can proccess it
         inputQueue.put(byteobPack)
         
   

def outputThread(outputQueue,sock,routingTable,debug):
    temp = 0
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
                 print("Im going to send a Orange & Orange Package type %s %d" % (pack.communicationType,temp)) 
                 bytePacket = pack.serialize()     
          targetNode = int.from_bytes(bytePacket[9:10],byteorder='little')
          #Routing_table returns the address
          address = routingTable.retrieveAddress(targetNode)
          
          #Sends the pack to the other Orange node
          sock.sendto(bytePacket,address)
          temp += 1
          #if debug == True: print("Im going to send ooPack to the server %s:%d " % (address[0],address[1]))            
          
      else:
        print("This is a blue to orange pack, still needs the implementation")
        if debug == True: print("Im going to send obPack to the server %s:%d " % (address[0],address[1]))       

def logicalThread(inputQueue,outputQueue,sock,table,nodeID,maxOrangeNodes,debug):


    requestNode = -1
    blueNodeIP = "0.0.0.0"
    blueNodePort = 8888
    MAXORANGENODES = maxOrangeNodes
    acks = []
    acksWrite = []
    acksDone = False #True when all the acks have been received, False otherwise
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
            
           if debug == True: print("This is a request pack from: %s requesting the number: %d with the priority: %d " % (pack.orangeSource,pack.requestedGraphPosition,pack.priority))
           
           if pack.requestedGraphPosition == requestNode: ##If I request the same number
              if pack.priority < priority: ##If my priority is bigger then I win
                       
                  if debug == True: print("I won the request of the blueNode: %d (myID: %d myPriority: %d) (otherNodeID: %d otherNodeIDpriority: %d)" % (requestNode,nodeID,priority,pack.orangeSource,pack.priority))
                  
                  #Creates a decline package
                  declinePack = ooPackage(0,sn,nodeID,pack.orangeSource,'d',requestNode,blueNodeIP,blueNodePort,priority)
                  
                  #Serialize the package
                  bytePacket = declinedPack.serialize()
                  
                  #Puts the package to the outputQueue
                  outputQueue.put(bytePacket)
                  
              elif pack.priority > priority: ##If my priority is smaller then the other node wins    
                  if debug == True: print("I lost the request of the blueNode: %d (myID: %d myPriority: %d) (otherNodeID: %d otherNodeIDpriority: %d)" % (requestNode,nodeID,priority,pack.orangeSource,pack.priority))    
                                
                  #Creates a accept
                  acceptPack = ooPackage(0,sn,nodeID,pack.orangeSource,'a',pack.requestedGraphPosition,pack.blueAddressIP,pack.blueAddressPort,pack.priority)
                  
                  #Serialize the package
                  bytePacket = acceptPack.serialize()
                  
                  #Puts the package to the outputQueue
                  outputQueue.put(bytePacket)
                                    
              else: #When both priorities are equal 
                  
                  if debug == True: print("We draw the request of the blueNode: %d (myID: %d myPriority: %d) (otherNodeID: %d otherNodeIDpriority: %d)" % (requestNode,nodeID,priority,pack.orangeSource,pack.priority))                  
                  
                  #Checks the nodeID and the bigger wins
                  if nodeID > pack.orangeSource: #I win
                        
                       if debug == True: print("I won the request of the blueNode:%d SecondRound (myID:%d) (otherNodeID:%d)" % (requestNode,nodeID,pack.orangeSource))                       
                       
                       #Creates a decline package
                       declinePack = ooPackage(0,sn,nodeID,pack.orangeSource,'d',requestNode,blueNodeIP,blueNodePort,priority)
                       
                       #Serialize the package
                       bytePacket = declinedPack.serialize()
                       
                       #Puts the package to the outputQueue
                       outputQueue.put(bytePacket)
                                         
                  else: ## The other node wins
                         
                       if debug == True: print("I lost the request of the blueNode:%d SecondRound (myID:%d) (otherNodeID:%d)" % (requestNode,nodeID,pack.orangeSource))       
                                            
                       #Creates a accept
                       acceptPack = ooPackage(0,sn,nodeID,pack.orangeSource,'a',pack.requestedGraphPosition,pack.blueAddressIP,pack.blueAddressPort,pack.priority)
                       
                       #Serialize the package
                       bytePacket = acceptPack.serialize()
                       
                       #Puts the package to the outputQueue
                       outputQueue.put(bytePacket)            
                                         
           else: #I did not request that node   
                    
              if debug == True: print("I dont have a problem with the request of the blueNode: %d from the orangeNode: %d" % (pack.requestedGraphPosition,pack.orangeSource))                   
              
              #Creates an accept package
              acceptPack = ooPackage(0,sn,nodeID,pack.orangeSource,'a',pack.requestedGraphPosition,pack.blueAddressIP,pack.blueAddressPort,pack.priority)
              
              #Serialize the package
              bytePacket = acceptPack.serialize()
              
              #Puts the package to the outputQueue
              outputQueue.put(bytePacket)  
              
              #Marks the node as requested                       
              table.markNodeAsRequested(pack.requestedGraphPosition) 
                
        elif pack.communicationType == 'd': #This is a declined package   
                       
             if debug == True: print("Received ack type declined from  orangeNode: %d about the request of the blueNode: %d and my request was: %d" % (pack.orangeSource,pack.requestedGraphPosition,requestNode))             

             #Append the ack to the acks list
             acks.append('d')

             #Checks if the acks list is done. The list is done when the size is MAXORANGENODES - 1
             if len(acks) == MAXORANGENODES - 1:
                   acksDone = True        
                  
                   
        elif pack.communicationType == 'a': #This is a accept package     
             print("Received ack type accept from  orangeNode: %d about the request of the blueNode: %d and my request was: %d" % (pack.orangeSource,pack.requestedGraphPosition,requestNode))
             #Append the ack to the acks list
             acks.append('a')
             
             #Checks if the acks list is done. The list is done when the size is MAXORANGENODES - 1
             if len(acks) == MAXORANGENODES - 1:
                   acksDone = True          
          
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
            priority = random.randrange(4294967294)

            for node in range(0,MAXORANGENODES):
               if not node == nodeID: 
                   requestPack = ooPackage(0,sn,nodeID,node,'r',requestNode,blueNodeIP,blueNodePort,priority)
                   #if debug == True: requestPack.print_data()
                   byteRequestPack = requestPack.serialize()
                   outputQueue.put(byteRequestPack)
                
         
     #Once the acks list is done. Send the write package
     if acksDone == True:
         if debug == True: print("Received all the acks for the requestNode: %d" % (requestNode))   
         #Creates the writePackages
         for node in range(0,MAXORANGENODES):
            if not node == nodeID: 
                writePack = ooPackage(0,sn,nodeID,node,'w',requestNode,blueNodeIP,blueNodePort,priority)
                #writePack.print_data()
                byteWritePack = writePack.serialize()
                outputQueue.put(byteWritePack) 
                
                
     #Once the acksWrite list is done. Send the commit package
     if acksWriteDone == True:
         if debug == True: print("Creating the commitPackage for the requestNode: %d to the blueNode IP: %s Port: %d" % (requestNode,blueNodeIP,blueNodePort))
         #Creates the commitPackage
         neighborList = table.obtainNodesNeighborsAdressList(requestNode)
         commitPack = obPackage(1,sn,'c',requestNode,blueNodeIP,blueNodePort,neighborList)
         commitPack.print_data()
         byteCommitPack = writePack.serialize()
         #outputQueue.put(byteCommitPack)   
         exit()                 



   



