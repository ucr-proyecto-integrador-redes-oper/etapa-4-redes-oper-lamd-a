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
         inputQueue.put(payload)
   
   

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
    requestNode = 0
    blueNodeIP = "0.0.0.0"
    blueNodePort = 8888
    MAXORANGENODES = 6
    while True:

     ##Takes a package from the inputQueue. If the queue is empty it waits until a package arrives
     bytePacket = inputQueue.get()
  
     #this determines what type of packet it is (Orange&Orange = 0 or Orange&Blue = 1 )
     if int.from_bytes(bytePacket[:1],byteorder='little') == 0: 
         pack = ooPackage()
         pack.unserialize(bytePacket)
         pack.print_data()
     
     #Orange & Blue
     else:
         
         pack = obPackage()
         pack.unserialize(bytePacket)
         
         #Creates the request packages
         blueNodeIP = pack.blueAddressIP
         blueNodePort = pack.blueAddressPort
         requestNode = table.obtainAvailableNode()
         sn = 1
         priority = random.randrange(4294967294)
         ack = [] #Default value 'x'
         for node in range(0,MAXORANGENODES):
            if not node == nodeID: 
                requestPack = ooPackage(0,sn,nodeID,node,'r',requestNode,blueNodeIP,blueNodePort,priority)
                ack.append('x')
                requestPack.print_data()
         #-------waits the timer------#    


"""
     pack = ooPackage(0,10,1,0,'r',300,'192.168.1.1',8888,8263)
  
     serializedObject = pack.serialize()
     
     #Puts the data to the outputQueue
     outputQueue.put(serializedObject)

    
     graphPostion1 = 4
     host1 = '10.1.135.25'
     port1 = 54444
     graphPostion2 = 27
     host2 = '187.127.511.623'
     port2 = 5477
     graphPostion3 = 400    #Creates the orange graph and the blueNodeTable
    table = blueNodeTable(blueGraphDir)
    requestNode = 0
    blueNodeIP = "0.0.0.0"
    blueNodePort = 8888
    MAXORANGENODES = 6
    while True:

     ##Takes a package from the inputQueue. If the queue is empty it waits until a package arrives
     bytePacket = inputQueue.get()
  
     #this determines what type of packet it is (Orange&Orange = 0 or Orange&Blue = 1 )
     if int.from_bytes(bytePacket[:1],byteorder='little') == 0: 
         pack = ooPackage()
         pack.unserialize(bytePacket)
         pack.print_data()
     
     #Orange & Blue
     else:
         
         pack = obPackage()
         pack.unserialize(bytePacket)
         
         #Creates the request packages
         blueNodeIP = pack.blueAddressIP
         blueNodePort = pack.blueAddressPort
         requestNode = table.obtainAvailableNode()
         sn = 1
         priority = random.randrange(4294967294)
         ack = [] #Default value 'x'
         for node in range(0,MAXORANGENODES):
            if not node == nodeID: 
                requestPack = ooPackage(0,sn,nodeID,node,'r',requestNode,blueNodeIP,blueNodePort,priority)]
                ack.append('x')
                requestPack.print_data()
         #-------waits the timer------#    

     host3 = '127.0.0.1'
     port3 = 65444

     neighborList = []
     pack2 = obPackage(1,1,'r',566,'10.1.127.37',8888,neighborList)
     serializedObject2 = pack2.serialize()

     outputQueue.put(serializedObject2)
"""



