import socket
import sys
import pickle

totalNodes = 6
maxSizeHeader = 237

class ProcessData:
	SN = 0
	sourceNode = 0
	destinationNode = 0
	tipo = ""
	requestNode=0
	address = "" #IP:PORT
	prio = 0





HOST, PORT = "localhost", 8888




sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

""" 
This is the maxSize pack
##Creates a package
sendPack = ProcessData();
sendPack.SN = 999
sendPack.sourceNode = totalNodes
sendPack.destinationNode = totalNodes
sendPack.tipo = "zZ"
sendPack.requestNode = 600
sendPack.address = "10.1.999.999:9999" #IP:PORT	
sendPack.prio = 999999
"""

##Creates a package
sendPack = ProcessData();
sendPack.SN = 1
sendPack.sourceNode = 1
sendPack.destinationNode = 3
sendPack.tipo = "b"
sendPack.requestNode = 10
sendPack.address = "10.1.138.25:8888" #IP:PORT	
sendPack.prio = 99


print("Sending [Sn: %d] [sourceNode: %d] [destinationNode: %d] [type: %s] [requestNode: %d] [address: %s] [prio: %d]"  % (sendPack.SN,sendPack.sourceNode,sendPack.destinationNode,sendPack.tipo,sendPack.requestNode,sendPack.address,sendPack.prio))
data_string = pickle.dumps(sendPack)
print("Tam  : %d" %(sys.getsizeof(data_string)))

sock.sendto(data_string, (HOST,PORT))

recvPack = ProcessData()
payload, client_address = sock.recvfrom(maxSizeHeader)
recvPack = pickle.loads(payload)
print("Recv from: %s [Sn: %d] [sourceNode: %d] [destinationNode: %d] [type: %s] [requestNode: %d] [address: %s] [prio: %d]"  % (client_address,recvPack.SN,recvPack.sourceNode,recvPack.destinationNode,recvPack.tipo,recvPack.requestNode,recvPack.address,recvPack.prio))

##payload, client_address = sock.recvfrom(128)
##data_variable = ProcessData()
##data_variable = pickle.loads(payload)
##print("Recv: %s" % (data_variable.msg))


##received = sock.recv(1024)



