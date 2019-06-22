import time
import struct
import socket as socket


class PacketStruct:
	def __init__(self, ip=0, port=0, payload=b'', sn=0, timeStamp=0.0):
		self.ip = ip
		self.port = port
		self.payload = payload
		self.sn = sn
		self.timeStamp = timeStamp


class SecureUdp:
	TIMEOUT = 0.2
	TimeStamp = 0
	# Esta es la ventana que muestra el espacio libre
	AckWindow = []
	index_last_sent = 0
	waiting_queue = []
	SNRN = 0
	sock = 0
	AcksReceived = []
	MAX_WINDOW_SIZE = 4

	'''
		EFE: Contruye la clase SecureUdp
		REQ: Se requiere el tamaño de la ventana para llenarlo
		MOD: ---
	'''

	def __init__(self, window_size, ip, port):
		self.window_size = window_size
		# Filling up the window with empty pairs
		for index in range(window_size):
			packet = PacketStruct()  # Default values
			self.AckWindow.append(packet)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket UDP
		self.sock.bind((ip, port))

	'''
		EFE: Checkea el campo de tiempo a ver si ya está en timeout
		REQ: ---
		MOD: Ackwindow
	'''

	def checkTimeStamps(self):  # resuelve todos los problemas, hasta nachos gg izi pici
		to_delete = []
		for item in self.AckWindow:
			if (self.AcksReceived.count(item.sn + 1) > 0):
				to_delete.append(item)  # Haven't received the ack
			elif ((time.time() - item.timeStamp) < self.TIMEOUT):
				self.sock.sendto(item.payload, (item.ip, item.port))
				# resets the timestamp with the current time since we just resend it.
				item.timeStamp = time.time()

		for deleted in to_delete:  # Solo borra lo que hay en todelete
			self.AckWindow.remove(deleted)

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

	def sendto(self, payload, address):
		ip, port = address
		# Si tengo espacio en mi ventana
		if (not len(self.waiting_queue) and len(self.AckWindow) < self.MAX_WINDOW_SIZE):
			client = (ip, port)
			self.SNRN = self.nextSNRN(self.SNRN)
			modified_payload = struct.pack('!bH', 0, self.SNRN) + payload
			self.sock.sendto(modified_payload, client)   # Envía!!!
			self.AckWindow.append(PacketStruct(
				ip, port, modified_payload, self.SNRN, time.time()))
		else:  # Agrego al waiting_queue
			self.waiting_queue.append((ip, port, payload))

	'''
		EFE: Se mantiene a la espera de un mensaje
		REQ: Conexción activa
		MOD: ---
	'''
	# payload, client_address = sock.recvfrom(5000)
	# if int.from_bytes(payload[:1], byteorder='little') == 0:

	def recivefrom(self, ip, port):
		while True:  # matiene la conexión
			payload, client_addr = self.sock.recvfrom(5000)  # Buffer size
			if int.from_bytes(payload[:1], byteorder='little') == 0:
				# THIS ISNT GONNA WORK ON FIRST TRY
				ack_payload = struct.pack('!bH', 1, self.nextSNRN(int.from_bytes(payload[1:3])))
				self.sock.sendto(ack_payload, client_addr)
				return (payload, client_addr)
			else:
				self.AcksReceived.append(int.from_bytes(payload[1:3]))
