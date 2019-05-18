import socket
import pickle

class ProcessData:
	process_id = 0
	prio = 0
	address = ""
	port = 0
	msg = ""





sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = '0.0.0.0'
server_port = 8888

server = (server_address, server_port)
sock.bind(server)
print("Listening on" + server_address + ":" + str(server_port))

while True:
	payload, client_address = sock.recvfrom(128)
	print("Echoing data back to" + str(client_address))
	data_variable = ProcessData()
	data_variable = pickle.loads(payload)
	print("Recv: %s" % (data_variable.msg))
	#sent = sock.sendto(payload, client_address)
