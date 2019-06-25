import time
import struct
import socket as socket
import queue
import threading

class PacketStruct:
	def __init__(self, ip=0, port=0, payload=b'', sn=0, timeStamp=0.0):
		self.ip = ip
		self.port = port
		self.payload = payload
		self.sn = sn
		self.timeStamp = timeStamp


class SecureUdp:
	TIMEOUT = 5
	TimeStamp = 0
	# Esta es la ventana que muestra el espacio libre
	AckWindow = []
	index_last_sent = 0
	waiting_queue = []
	SNRN = 0
	sock = 0
	AcksReceived = []
	MAX_WINDOW_SIZE = 4
	reciveQueue = queue.Queue()

	'''
		EFE: Contruye la clase SecureUdp
		REQ: Se requiere el tamaño de la ventana para llenarlo
		MOD: ---
	'''

	def __init__(self, window_size, ip, port):
		self.window_size = window_size

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket UDP
		self.sock.bind((ip, port))
		##Creates the Threads
		send = threading.Thread(target=self.dummysendThread, args=())
		send.start()

		##Creates the Threads
		recive = threading.Thread(target=self.dummtReceive, args=())
		recive.start()	



	'''
		EFE: Checkea el campo de tiempo a ver si ya está en timeout
		REQ: ---
		MOD: Ackwindow
	'''

	def checkTimeStamps(self):  # resuelve todos los problemas, hasta nachos gg izi pici
		to_delete = []
		for item in self.AckWindow:
			if (self.AcksReceived.count(item.sn + 1) > 0):
				print("Put shit in the ackreceived queue")
				to_delete.append(item)  # Haven't received the ack
			elif ((time.time() - item.timeStamp) > self.TIMEOUT):
				print("TimesUp ",item.payload)
				self.sock.sendto(item.payload, (item.ip, item.port))
				# resets the timestamp with the current time since we just resend it.
				item.timeStamp = time.time()


		for deleted in to_delete:  # Solo borra lo que hay en todelete
			self.AckWindow.remove(deleted)
			print("Removed an ACK")

	'''
		EFE: Devuelve el SNRN evitando que el mismo sea mas grande que la capacidad de un short
		REQ:  ---
		MOD: self.SNRN
	'''

	def nextSNRN(self, SN):
		SN = (SN + 1) % 65535
		return SN

	'''
		EFE: Envía un mensaje a otro SUDP y activa un timer, si no hay espacio en la ventana lo guarda en eun queue
	  	REQ: ---
		MOD: AckWindow
	'''

	def dummysendThread(self):
		while True:
			if len(self.AckWindow) < self.MAX_WINDOW_SIZE: #Si tiene campo en la ventana
				if len(self.waiting_queue) > 0: # 
					ip,port,payload = self.waiting_queue.pop(0)
					client = (ip, port)
					#self.SNRN = self.nextSNRN(self.SNRN)
					modified_payload = struct.pack('!bH', 0, self.SNRN) + payload
					print("Sending ",payload," To ",ip,port,modified_payload)
					self.sock.sendto(modified_payload, client)   # Envía!!!
					self.AckWindow.append(PacketStruct(ip, port, modified_payload, self.SNRN, time.time()))

			self.checkTimeStamps()



	def dummySendto(self,payload,ip,port):
		self.waiting_queue.append((ip,port,payload))




	'''
		EFE: Se mantiene a la espera de un mensaje
		REQ: Conexción activa
		MOD: ---
	'''
	# payload, client_address = sock.recvfrom(5000)
	# if int.from_bytes(payload[:1], byteorder='little') == 0:


	def recivefrom(self):
		return self.reciveQueue.get(block=True,timeout=None)
		

	def dummtReceive(self):
		while True:  # matiene la conexión
			payload, client_addr = self.sock.recvfrom(5000)  # Buffer size
			#print("i just receive ",payload," from client ",client_addr)
			if int.from_bytes(payload[:1], byteorder='big') == 0:
				# THIS ISNT GONNA WORK ON FIRST TRY
				sn_received = int.from_bytes(payload[0:2],byteorder='big')
				print("\got SN: %d" % (sn_received))
				sn_to_send = self.nextSNRN(sn_received)
				print("\tsending ACK with SN: %d" % (sn_to_send)) 
				ack_payload = struct.pack('!bH', 1, sn_to_send)
				#print(payload)
				self.sock.sendto(ack_payload, client_addr)
				self.reciveQueue.put(payload)

			else:
				print("got ack for ", client_addr)
				print("ACK Payload: ", payload)
				self.AcksReceived.append(int.from_bytes(payload[1:3],byteorder='big'))




def main():
	port = input()
	port2 = input()
	test = SecureUdp(4,"10.1.138.34",int(port))
	payload = b'hola'
	ip = "10.1.138.34"
	
	for item in range(1):
		test.dummySendto(payload,ip,int(port2))
	
	
	payload = test.recivefrom()
	print("Receive ",payload)


if __name__ == "__main__":
    main()
