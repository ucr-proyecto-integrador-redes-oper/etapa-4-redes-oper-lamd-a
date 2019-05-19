import socket
import pickle
import sys
import queue
import threading
from Header import Header

##Thread that handles the input messages from the udp socket
def inputThread(inputQueue,sock):
	maxSizeHeader = 237 
	while True:
		#Receive a package
		recvPack = Header()
		payload, client_address = sock.recvfrom(maxSizeHeader)
		
		#Reconstructs the data
		recvPack = pickle.loads(payload)
		
		#recvPack.print_data()
		
		#Puts the data to the queue
		inputQueue.put(recvPack)

##Thread that handles the out messages to the udp socket
def outputThread(outputQueue,sock):
	while True:
		##Takes a package from the queue. If the queue is empty it waits until a package arrives
		pack = Header()
		pack = outputQueue.get()
		
		#print("Recv")
		#pack.print_data()
		
		#Creates a representation of thr object as a bytes stream
		data_string = pickle.dumps(pack)
		
		#Routing_table returns the address
		#address = routing_table.retrieveAddress(pack.destinationNode)
		
		sock.sendto(data_string,address)


def logicalThread(inputQueue,outputQueue,sock):
	while True:
		##Takes a package from the inputQueue. If the queue is empty it waits until a package arrives
		pack = Header()
		pack = inputQueue.get()
		
		##-------------Logic--------##
		
		#Puts the data to the outputQueue
		outputQueue.put(recvPack)

def main():
	

	server_address = '0.0.0.0'
	server_port = 8888
	server = (server_address, server_port)
	inputQueue = queue.Queue()
	outputQueue = queue.Queue()

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(server)
	print("Listening on " + server_address + ":" + str(server_port))
	##Creates the Threads
	t = threading.Thread(target=inputThread, args=(inputQueue,sock, ))
	t.start()
	t2 = threading.Thread(target=outputThread, args=(outputQueue,sock, ))
	t2.start()
	t3 = threading.Thread(target=logicalThread, args=(inputQueue,outputQueue,sock, ))
	t3.start()
	
	
if __name__== "__main__":
  main()
