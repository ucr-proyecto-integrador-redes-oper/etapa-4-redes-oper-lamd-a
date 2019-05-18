import socket
import sys
import pickle

class ProcessData:
	process_id = 0
	prio = 0
	address = ""
	port = 0
	msg = ""

HOST, PORT = "localhost", 8888


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
variable = ProcessData()
variable.address = HOST
variable.port = PORT
variable.msg = "como esta"

print("Send: %s"  % (variable.msg))
data_string = pickle.dumps(variable)
sock.sendto(data_string, (HOST,PORT))


##received = sock.recv(1024)



