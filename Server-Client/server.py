import socket
import pickle
import sys


maxSizeHeader = 237

class ProcessData:
	SN = 0
	sourceNode = 0
	destinationNode = 0
	tipo = ""
	requestNode=0
	address = "" #IP:PORT
	prio = 0






sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = '0.0.0.0'
server_port = 8888

server = (server_address, server_port)
sock.bind(server)
print("Listening on" + server_address + ":" + str(server_port))

while True:
	recvPack = ProcessData()
	payload, client_address = sock.recvfrom(maxSizeHeader)
	recvPack = pickle.loads(payload)
	print("Recv from: %s [Sn: %d] [sourceNode: %d] [destinationNode: %d] [type: %s] [requestNode: %d] [address: %s] [prio: %d]"  % (client_address,recvPack.SN,recvPack.sourceNode,recvPack.destinationNode,recvPack.tipo,recvPack.requestNode,recvPack.address,recvPack.prio))
	
	##Adds data to the package
	recvPack.sourceNode=6
	recvPack.requestNode = 599
	
	
	print("Send [Sn: %d] [sourceNode: %d] [destinationNode: %d] [type: %s] [requestNode: %d] [address: %s] [prio: %d]"  % (recvPack.SN,recvPack.sourceNode,recvPack.destinationNode,recvPack.tipo,recvPack.requestNode,recvPack.address,recvPack.prio))
	data_string = pickle.dumps(recvPack)
	
	
	sock.sendto(data_string, client_address)
	print("Tam %d" % (sys.getsizeof(data_string)))
	
	
	#sent = sock.sendto(payload, client_address)
