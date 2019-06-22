class PacketStruct:
	def __init__(self, ip = 0, port = 0, payload = b'', sn = 0, timeStamp = 0.0):
		self.ip = ip
		self.port = port
		self.payload = payload
		self.sn = sn
		self.timeStamp = timeStamp

