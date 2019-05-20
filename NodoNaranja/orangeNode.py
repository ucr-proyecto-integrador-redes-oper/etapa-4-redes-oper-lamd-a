import socket
import pickle
import sys
import queue
import threading
from blueNodeTable import blueNodeTable
from RoutingTable import RoutingTable
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
        t = threading.Thread(target=inputThread, args=(inputQueue,sock, ))
        t.start()
        t2 = threading.Thread(target=outputThread, args=(outputQueue,sock,routingTable ))
        t2.start()
        t3 = threading.Thread(target=logicalThread, args=(inputQueue,outputQueue,sock,self.blueGraphDir,  ))
        t3.start()
        
        
def inputThread(inputQueue,sock):
    while True:
      #Receive a package
      payload, client_address = sock.recvfrom(5000)

      #this determines what type of packet it is (Orange&Orange = 0 or Orange&Blue = 1 )
      if int.from_bytes(bytePacket[:1],byteorder='little') == 0: 
         #Orange & Orange
          ##BYTE 9 has the orangetarget
          targetNode = int.from_bytes(bytePacket[:10],byteorder='little')
   
      #Puts the data to the queue
      inputQueue.put(recvPack)
   
   

def outputThread(outputQueue,sock,routingTable):
    while True:
      ##Takes a package from the queue. If the queue is empty it waits until a package arrives
      bytePacket = outputQueue.get()
  
      #this determines what type of packet it is (Orange&Orange = 0 or Orange&Blue = 1 )
      if int.from_bytes(bytePacket[:1],byteorder='little') == 0: 
       #Orange & Orange
       ##BYTE 9 has the orangetarget
          targetNode = int.from_bytes(bytePacket[:10],byteorder='little')
  
          #Routing_table returns the address
          address = routingTable.retrieveAddress(targetNode)
          sock.sendto(bytePacket,address)
      else:
        print("This is a blue to orange pack, still needs the implementation")
 

def logicalThread(inputQueue,outputQueue,sock,blueGraphDir):
    while True:

     ##Creates the orange graph and the blueNodeTable
     table = blueNodeTable(blueGraphDir)


     ##Takes a package from the inputQueue. If the queue is empty it waits until a package arrives
     pack = inputQueue.get()

     ##-------------Logic--------##

     #Puts the data to the outputQueue
     outputQueue.put(recvPack)









