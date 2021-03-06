from SecureUDP import SecureUdp
from obPackage import obPackage
import threading
import sys
import queue
import time
import random

class blueNode:
	neighborTuple = {} #[key = NodeID] = (IP,PORT)
	sTreeDadNode = (-1,"0.0.0.0",0) # Tuple with (NodeID,IP,PORT)
	sTreeSonsNodes = [] # Tuple with (NodeID,IP,PORT)
	imInTheSpanningTree = False
	myID = 0
	packageQueue = queue.Queue() # Tuple with (bytePackage,addr). Addr is a tuple with the ip and port 
	chunksStored = 0 #Cant be more than 40
	blueSavedChunks = {} # [key = (fileIDByte1,fileIDRest)] = list [tuples (chunkID,Chunk)].The key helps to find the FileID then list holds all the chunks stored from that fileID
	SecureUDP = 0 
	spanningTreeMsgQueue = queue.Queue() #(Type,nodeID,IP,PORT)
	existsMap = {} # [key = (fileIDByte1,fileIDRest)] = (IP,PORT)
	locateMap = {} # [key = (fileIDByte1,fileIDRest)] = (IP,PORT)
	completeMap = {} # [key = (fileIDByte1,fileIDRest)] = (IP,PORT)
	getMap = {} # [key = (fileIDByte1,fileIDRest)] = (IP,PORT)
	root = 1
	maxChunks = 40

	def __init__(self,orangeIP,orangePort):
		self.SecureUDP = SecureUdp(100,1,True) #ventana de 100 con timeout de 1s
		print("BlueNode Listening on ip: %s port %d " %
			  ( self.SecureUDP.sock.getsockname()[0], self.SecureUDP.sock.getsockname()[1]))
		# Creates the Threads
		t = threading.Thread(target=self.inputThread, args=())
		t.start()

		t2 = threading.Thread(target=self.logicalThread, args=())
		t2.start()

		t2 = threading.Thread(target=self.userInputThread, args=())
		t2.start()

		obPackagex = obPackage(14)
		serializedObject = obPackagex.serialize(14)
		self.SecureUDP.sendto(serializedObject,orangeIP,orangePort)


	def inputThread(self):
		while True:
			payload , addr = self.SecureUDP.recivefrom()
			# print(payload)
			Type = int.from_bytes(payload[:1], byteorder='big')
			if Type == 12 or Type == 18:
				spanningTreePack = obPackage(Type)
				spanningTreePack.unserialize(payload,Type)
				self.spanningTreeMsgQueue.put((spanningTreePack.packetCategory,spanningTreePack.nodeID,addr[0],addr[1]))  
			elif Type == 11: #JoinTree
				print("(JoinTree)")
				joinTreeResponsePack = obPackage()
				if self.imInTheSpanningTree == True:
					joinTreeResponsePack.packetCategory = 12 #IDo pack
					joinTreeResponsePack.nodeID = self.myID
					byteJoinTreeResponsePack = joinTreeResponsePack.serialize(12)
					self.SecureUDP.sendto(byteJoinTreeResponsePack,addr[0],addr[1])
				else:
					joinTreeResponsePack.packetCategory = 18 #IDoNot pack
					joinTreeResponsePack.nodeID = self.myID
					byteJoinTreeResponsePack = joinTreeResponsePack.serialize(18)
					self.SecureUDP.sendto(byteJoinTreeResponsePack,addr[0],addr[1])
			elif Type == 13:
				print("(Daddy)")
				DaddyPack = obPackage(13)
				DaddyPack.unserialize(payload,13)
				self.sTreeSonsNodes.append((DaddyPack.nodeID,addr[0],addr[1]))
			elif Type == 1:
				print("(Hello)")
				helloPack = obPackage(1)
				helloPack.unserialize(payload,1)
				self.neighborTuple[helloPack.nodeID] = (addr[0],addr[1])
			elif Type == 15:
				print("(NeighborNoAddrs)")
				obPackagex = obPackage()
				obPackagex.unserialize(payload,15)
				self.neighborTuple[obPackagex.neighborID] = (-1,-1)
				self.myID = obPackagex.nodeID
			elif Type == 16:
				print("(Neighbor) from ")
				obPackagex = obPackage()
				obPackagex.unserialize(payload,16)
				self.neighborTuple[obPackagex.neighborID] = (obPackagex.blueAddressIP,obPackagex.blueAddressPort)
				self.myID = obPackagex.nodeID
				#Creates the hello pack
				helloPack = obPackage(1)
				helloPack.nodeID = self.myID
				serializedHelloPack = helloPack.serialize(1)
				self.SecureUDP.sendto(serializedHelloPack,obPackagex.blueAddressIP,obPackagex.blueAddressPort)

			elif Type == 8:
				print("(Locate) from ",addr[0],str(addr[1]))
				genericPack = obPackage()
				genericPack.unserialize(payload,8)
				self.locateMap[(genericPack.fileIDByte1,genericPack.fileIDRest)] = (addr[0],addr[1])
				#Checks if I have a chunk of that file
				if (genericPack.fileIDByte1,genericPack.fileIDRest) in self.blueSavedChunks:
					print("I have a chunk")
					responseLocate = obPackage(9)
					responseLocate.fileIDByte1 = genericPack.fileIDByte1
					responseLocate.fileIDRest = genericPack.fileIDRest
					responseLocate.nodeID = self.myID
					byteResponseLocate = responseLocate.serialize(9)
					self.SecureUDP.sendto(byteResponseLocate,addr[0],addr[1])

				# print("I need to ask my spanningTree")
				listNode = self.getSpanningTreeNodes((addr[0],addr[1]))
				#If theres a path to take
				if (len(listNode) != 0):
					for node in listNode:
						#Creates a Exists package
						print("Creando Locate ",node)
						existsPack = obPackage(8)
						existsPack.fileIDByte1 = genericPack.fileIDByte1
						existsPack.fileIDRest = genericPack.fileIDRest
						byteExistsPack = existsPack.serialize(8)
						self.SecureUDP.sendto(byteExistsPack,node[0],node[1])

			elif Type == 9:
				print("(LocateRes) from ",addr[0],str(addr[1]))
				responseLocate = obPackage(9)
				responseLocate.unserialize(payload,9)
				# responseLocate.print_data()
				if (responseLocate.fileIDByte1,responseLocate.fileIDRest) in self.locateMap: #If theres a exist request for that file id
					addrs = self.locateMap[(responseLocate.fileIDByte1,responseLocate.fileIDRest)]
					responseLocate = responseLocate.serialize(9)
					self.SecureUDP.sendto(responseLocate,addrs[0],addrs[1])
				else:
					print("I dont have a exist request for that file")
			elif Type == 6:
				print("(Get) from ",addr[0],str(addr[1]))
				genericPack = obPackage()
				genericPack.unserialize(payload,6)
				self.getMap[(genericPack.fileIDByte1,genericPack.fileIDRest)] = (addr[0],addr[1])
				#Checks if I have a chunk of that file
				if (genericPack.fileIDByte1,genericPack.fileIDRest) in self.blueSavedChunks:
					
					for chunk in self.blueSavedChunks[(genericPack.fileIDByte1,genericPack.fileIDRest)]:
						print("I have a chunk")
						responseGet = obPackage(7)
						responseGet.fileIDByte1 = genericPack.fileIDByte1
						responseGet.fileIDRest = genericPack.fileIDRest
						responseGet.chunkID = chunk[0]
						responseGet.chunkPayload = chunk[1]

						byteResponseGet= responseGet.serialize(7)
						self.SecureUDP.sendto(byteResponseGet,addr[0],addr[1])

				#Asks the neighbors 
				listNode = self.getSpanningTreeNodes((addr[0],addr[1]))
				#If theres a path to take
				if (len(listNode) != 0):
					for node in listNode:
						#Creates a Exists package
						print("Creando Get ",node)
						getPack = obPackage(6)
						getPack.fileIDByte1 = genericPack.fileIDByte1
						getPack.fileIDRest = genericPack.fileIDRest
						byteGetPack = getPack.serialize(6)
						self.SecureUDP.sendto(byteGetPack,node[0],node[1])

			elif Type == 7:
				print("(GetRes) from ",addr[0],str(addr[1]))
				responseGet = obPackage(7)
				responseGet.unserialize(payload,7)
				if (responseGet.fileIDByte1,responseGet.fileIDRest) in self.getMap: #If theres a exist request for that file id
					addrs = self.getMap[(responseGet.fileIDByte1,responseGet.fileIDRest)]
					byteResponseGet = responseGet.serialize(7)
					self.SecureUDP.sendto(byteResponseGet,addrs[0],addrs[1])
				else:
					print("I dont have a exist request for that file")
			
			elif Type == 4: #UNTESTED UNTESTED UNTESTED
				print("(Complete) from", addr)
				genericPack = obPackage(Type)
				genericPack.unserialize(payload,Type)
				self.completeMap[(genericPack.fileIDByte1,genericPack.fileIDRest)] = (addr[0],addr[1]) 
				#Checks if I have a chunk of that file
				for fileIDTuple, chunkList in self.blueSavedChunks.items():
					if fileIDTuple == (genericPack.fileIDByte1,genericPack.fileIDRest):
						for chunkTuple in chunkList:
							responceComplete = obPackage(5)
							responceComplete.packetCategory = 5
							responceComplete.fileIDByte1 = genericPack.fileIDByte1 
							responceComplete.fileIDRest = genericPack.fileIDRest
							responceComplete.chunkID = chunkTuple[0]
							byteresponseComplete = responceComplete.serialize(5)
							self.SecureUDP.sendto(byteresponseComplete,addr[0],addr[1])
				#Sending complete request to the rest of the spanning three
				listNode = self.getSpanningTreeNodes((addr[0],addr[1]))
				# print("Path ",listNode)
				#If theres a path to take
				if len(listNode) != 0:
					for node in listNode:
						bytecompletePack = genericPack.serialize(Type)
						self.SecureUDP.sendto(bytecompletePack, node[0], node[1])

			elif Type == 5: #UNTESTED UNTESTED UNTESTED
				print("(Complete R) from ",addr)
				responseComplete = obPackage(Type)
				responseComplete.unserialize(payload,Type)

				if (responseComplete.fileIDByte1,responseComplete.fileIDRest) in self.completeMap: #If theres a complete request for that file id
					addr = self.completeMap[(responseComplete.fileIDByte1,responseComplete.fileIDRest)]
					#del self.completeMap[(responseComplete.fileIDByte1,responseComplete.fileIDRest)]
					byteresponseComplete = responseComplete.serialize(Type)
					self.SecureUDP.sendto(byteresponseComplete,addr[0],addr[1])
				else:
					print("I dont have a complete request for that file")			
			
			elif Type == 10:
				print("(Delete) from ",addr)
				deletePack = obPackage(Type)
				deletePack.unserialize(payload,Type)

				#If I have that FileID delete all the chunks
				if (deletePack.fileIDByte1,deletePack.fileIDRest) in self.blueSavedChunks:
					totalChunks = len(self.blueSavedChunks[(deletePack.fileIDByte1,deletePack.fileIDRest)])
					self.chunksStored -=  totalChunks
					del self.blueSavedChunks[(deletePack.fileIDByte1,deletePack.fileIDRest)]
				
				#Sending delete request to the rest of the spanning three
				listNode = self.getSpanningTreeNodes((addr[0],addr[1]))
				# print("Path ",listNode)
				#If theres a path to take
				if len(listNode) != 0:
					for node in listNode:
						byteDeletePack = deletePack.serialize(Type)
						self.SecureUDP.sendto(byteDeletePack, node[0], node[1])


			else:
				self.packageQueue.put((payload,addr))


	def userInputThread(self):
		while True:
			user = input()
			if user == '$':
				print("myID ",str(self.myID)," neighbors: ",self.neighborTuple," imInTheSpanningTree:",self.imInTheSpanningTree," sTreeDadNode: ",self.sTreeDadNode,"sTreeSonsNodes ",self.sTreeSonsNodes ," chunksStored: ",self.chunksStored)
			elif user == "%":
				fileIDByte1 = input("Enter fileIDByte1 ")
				fileIDRest = input("Enter fileIDRest ")
				if (int(fileIDByte1),int(fileIDRest)) in self.blueSavedChunks:
					lista = self.blueSavedChunks[(int(fileIDByte1),int(fileIDRest))]
					print("Total chunks: ",str(len(lista)))
					for chunkID in lista:
						print("[",str(chunkID[0]),"] ", end = '')
					print(" ")
				

	def logicalThread(self):
		while True:
			package = self.packageQueue.get(block=True,timeout=None) #(payload,addr)
			# print(package)
			bytePackage = package[0]
			Type = int.from_bytes(bytePackage[:1], byteorder='big')
			genericPack = obPackage()
			if Type == 0:
				print("(PutChunk) from ",package[1])
				chunkPack = obPackage()
				chunkPack.unserialize(bytePackage,0)

				actions = ["save","save&Clone","clone","drop"]
				percentages = [0.80,0,0.20,0] # 80% save 0% save&Clone %20 clone 0% drop
				result = 0
				if self.chunksStored < self.maxChunks:
					result = self.putChunkRandomChoiceGenerator(percentages)
				else:
					percentages = [0,0,1,0] # 0% save 0% save&Clone %100 clone 0% drop
					result = self.putChunkRandomChoiceGenerator(percentages)
				print("Accion ",actions[result])
				if actions[result] == "save":
					#Checks if the key exists
					if (chunkPack.fileIDByte1,chunkPack.fileIDRest) in self.blueSavedChunks:
						#If the key exists then just append the new chunkID and chunkPayload
						self.blueSavedChunks[(chunkPack.fileIDByte1,chunkPack.fileIDRest)].append((chunkPack.chunkID,chunkPack.chunkPayload))
					else:
						#If not then creates a list witht the chunkID and chunkPayload and assign it to the key
						tempList = [(chunkPack.chunkID,chunkPack.chunkPayload)]
						self.blueSavedChunks[(chunkPack.fileIDByte1,chunkPack.fileIDRest)] = tempList

					self.chunksStored += 1
				elif actions[result] == "clone":
					#1 Neighbor 
					randomNeighbor = random.choice(list(self.neighborTuple))
					self.SecureUDP.sendto(bytePackage,self.neighborTuple[randomNeighbor][0],self.neighborTuple[randomNeighbor][1])
					# listNode = self.getSpanningTreeNodes((package[1][0],package[1][1]))
					# print("Path ",listNode)

					#If theres a path to take
					# if len(listNode) != 0:
					# 	serializedPutChunkPack = chunkPack.serialize(0)
					# 	for node in listNode:
					# 		self.SecureUDP.sendto(serializedPutChunkPack,node[0],node[1])
					# totalNeighbors = len(self.neighborTuple)
					# if totalNeighbors > 0:
					#     copyNeighborTuple = self.neighborTuple.copy()
					#     #Picks random how many neighbors are gonna get the chunk 
					#     randomNeighbors = totalNeighbors #random.randrange(1,totalNeighbors+1)
					#     #Picks random one neighbor
					#     for x in range(randomNeighbors):
					#         randomChoiceNeighbor = random.choice(list(copyNeighborTuple))
					#     #     #Creates a putChunk package
					#         serializedPutChunkPack = chunkPack.serialize(0)
					#         # print("Clone to",copyNeighborTuple[randomChoiceNeighbor][0],str(copyNeighborTuple[randomChoiceNeighbor][1]))
					#         self.SecureUDP.sendto(serializedPutChunkPack,copyNeighborTuple[randomChoiceNeighbor][0],copyNeighborTuple[randomChoiceNeighbor][1])
					#         del copyNeighborTuple[randomChoiceNeighbor]

				elif actions[result] == "save&Clone":
					#Checks if the key exists
					if (chunkPack.fileIDByte1,chunkPack.fileIDRest) in self.blueSavedChunks:
						#If the key exists then just append the new chunkID and chunkPayload
						self.blueSavedChunks[(chunkPack.fileIDByte1,chunkPack.fileIDRest)].append((chunkPack.chunkID,chunkPack.chunkPayload))
						
					else:
						#If not then creates a list witht the chunkID and chunkPayload and assign it to the key
						tempList = []
						tempList.append((chunkPack.chunkID,chunkPack.chunkPayload))
						self.blueSavedChunks[(chunkPack.fileIDByte1,chunkPack.fileIDRest)] = tempList
					
					self.chunksStored += 1


					listNode = self.getSpanningTreeNodes((package[1][0],package[1][1]))
					# print("Path ",listNode)
					#If theres a path to take
					if len(listNode) != 0:
						serializedPutChunkPack = chunkPack.serialize(0)
						for node in listNode:
							self.SecureUDP.sendto(serializedPutChunkPack,node[0],node[1])

					# totalNeighbors = len(self.neighborTuple)
					# if totalNeighbors > 0:
					#     copyNeighborTuple = self.neighborTuple.copy()
					#     #Picks random how many neighbors are gonna get the chunk 
					#     randomNeighbors = random.randrange(1,totalNeighbors+1)
					#     #Picks random one neighbor
					#     for x in range(randomNeighbors):
					#         randomChoiceNeighbor = random.choice(list(copyNeighborTuple))
					#         #Creates a putChunk package
					#         serializedPutChunkPack = chunkPack.serialize(0)
					#         # print("Save Clone to",copyNeighborTuple[randomChoiceNeighbor][0],str(copyNeighborTuple[randomChoiceNeighbor][1]))
					#         self.SecureUDP.sendto(serializedPutChunkPack,copyNeighborTuple[randomChoiceNeighbor][0],copyNeighborTuple[randomChoiceNeighbor][1])
					#         del copyNeighborTuple[randomChoiceNeighbor]
				

 
				# #If theres less than 40 chunks saved, then save the chunk
				# if self.chunksStored < self.maxChunks:
				#     #Checks if the key exists
				#     if (chunkPack.fileIDByte1,chunkPack.fileIDRest) in self.blueSavedChunks:
				#         #If the key exists then just append the new chunkID and chunkPayload
				#         self.blueSavedChunks[(chunkPack.fileIDByte1,chunkPack.fileIDRest)].append((chunkPack.chunkID,chunkPack.chunkPayload))
						
				#     else:
				#         #If not then creates a list witht the chunkID and chunkPayload and assign it to the key
				#         tempList = []
				#         tempList.append((chunkPack.chunkID,chunkPack.chunkPayload))
				#         self.blueSavedChunks[(chunkPack.fileIDByte1,chunkPack.fileIDRest)] = tempList

				#     self.chunksStored += 1

				# #Otherwise it sends the chunk to the neighbors
				# else:
				#     #Creates a putChunk package
				#     serializedPutChunkPack = chunkPack.serialize(0)
				#     listNode = self.getSpanningTreeNodes((package[1][0],package[1][1]))
				#     print("Path ",listNode)
				#     #If theres a path to take
				#     if len(listNode) != 0:
				#         for node in listNode:
				#             self.SecureUDP.sendto(serializedPutChunkPack,node[0],node[1])

			elif Type == 2:
				print("(Exist) from ",package[1])
				genericPack.unserialize(bytePackage,2)
				#Checks if I have a chunk of that file
				if (genericPack.fileIDByte1,genericPack.fileIDRest) in self.blueSavedChunks:
					genericPack.packetCategory = 3
					responseExist = genericPack.serialize(3)
					self.SecureUDP.sendto(responseExist,package[1][0],package[1][1])
				else:
					# print("I dont have a chunk. I need to ask my spanningTree")
					listNode = self.getSpanningTreeNodes((package[1][0],package[1][1]))
					# print("Path ",listNode)
					#If theres a path to take
					if len(listNode) != 0:
						self.existsMap[(genericPack.fileIDByte1,genericPack.fileIDRest)] = (package[1][0],package[1][1])
						for node in listNode:
							#Creates a Exists package
							existsPack = obPackage(2)
							existsPack.fileIDByte1 = genericPack.fileIDByte1
							existsPack.fileIDRest = genericPack.fileIDRest
							byteExistsPack = existsPack.serialize(2)
							self.SecureUDP.sendto(byteExistsPack,node[0],node[1])

			elif Type == 3:
				
				print("(Exist R) from ",package[1])
				responseExist = obPackage(3)
				responseExist.unserialize(bytePackage,3)

				if (responseExist.fileIDByte1,responseExist.fileIDRest) in self.existsMap: #If theres a exist request for that file id
					addr = self.existsMap[(responseExist.fileIDByte1,responseExist.fileIDRest)]
					del self.existsMap[(responseExist.fileIDByte1,responseExist.fileIDRest)]
					byteResponseExist = responseExist.serialize(3)
					self.SecureUDP.sendto(byteResponseExist,addr[0],addr[1])
				else:
					print("I dont have a exist request for that file")

			elif Type == 17:
				print("(GraphComplete) from ",package[1])
				print("vecinos ",self.neighborTuple)
				#If im the blueNode 0 then im the root of the spanningTree
				if self.myID == self.root:
					print("Hey im the root")
					self.imInTheSpanningTree = True
				#If not then join the spanningTree 
				else:
					time.sleep(5)
					#ask for daddy
					# if self.root in self.neighborTuple:
					#     addr = self.neighborTuple[1]
					#     self.sTreeDadNode = (self.root,addr[0],addr[1])
					#     self.imInTheSpanningTree = True
					# else:
					self.sTreeDadNode  = self.joinSpanningTree() #(node, IP, PORT)

					print("Im part of the spanning Tree ",self.myID)
					self.imInTheSpanningTree = True
					#Sends the daddyPack
					daddyPackage = obPackage(13)
					daddyPackage.nodeID = self.myID
					bytesDaddyPackage = daddyPackage.serialize(13)
					self.SecureUDP.sendto(bytesDaddyPackage, self.sTreeDadNode[1], self.sTreeDadNode[2])





	def getSpanningTreeNodes(self,addr): #Returns a list with the possible nodes to go from a inicial node in the spanningTree
		listNodes = []
		#Checks if the dadNode is not the one sending the msg
	   # print("Dad ",self.sTreeDadNode[1],str(self.sTreeDadNode[2]))
		if self.myID != self.root:
			if self.sTreeDadNode[0] != -1 and self.sTreeDadNode[1] != addr[0]:
				listNodes.append((self.sTreeDadNode[1],self.sTreeDadNode[2]))
			elif self.sTreeDadNode[0] != -1 and self.sTreeDadNode[2] != addr[1]:
				listNodes.append((self.sTreeDadNode[1],self.sTreeDadNode[2]))
		for node in self.sTreeSonsNodes: #(NodeID,IP,Port)
			#print("Sons ",node[1],str(node[2]))
			if node[1] != addr[0]:  
				listNodes.append((node[1],node[2]))
			elif node[2] != addr[1]:
				listNodes.append((node[1],node[2]))
		return listNodes

	def joinSpanningTree(self):

		# Espera poder ser incluido
		while (True):
			neighborAlive = 0
			for neighbour in self.neighborTuple: #neighborTuple es de la forma (node, IP, PORT)
				print("Vecino ",self.neighborTuple[neighbour])
				if self.neighborTuple[neighbour][0] != -1: #If the neighbor has a address
					# Creo el paquetico de tipo 11
					JoinTreePack = obPackage(11)
					JoinTreePack.nodeID = self.myID
					bytesJoinTreePack = JoinTreePack.serialize(11) 
					print("Sending Join ", self.neighborTuple[neighbour])
					self.SecureUDP.sendto(bytesJoinTreePack, self.neighborTuple[neighbour][0],self.neighborTuple[neighbour][1])
					neighborAlive += 1
			# Saca las respuestas
			responseList = [] #(nodeID,IP,PORT)
			for i in range(neighborAlive):
				response = self.spanningTreeMsgQueue.get(block=True,timeout=None) # se bloquea hasta tener respuesta   (Type,nodeID,IP,PORT)
				print("Receiving ",response)
				if response[0] == 12: # si si hay un IDo, no guarda IDoNot
					responseList.append((response[1],response[2],response[3])) #(nodeID,IP,PORT)

			responseListSize = len(responseList)  

			if responseListSize != 0: # Encontro al menos un vecino
				if responseListSize == 1: # Si solo hay un vecino, se guarda automático
					dad = responseList[0]
					#print("response ",dad)
					return (dad[0],dad[1],dad[2]) #(nodeID,IP,PORT)
				elif responseListSize > 1: # si hay 0 vecinos
					maxNodeID = (99999999,"0.0.0.0",0)
					for candidate in responseList: # Battle to ask for a sugar Daddy
						if candidate[0] < maxNodeID[0]:
							maxNodeID = candidate 
					return maxNodeID
			else:
				time.sleep(5)

	# Returns the index of the percentagesList who won
	def putChunkRandomChoiceGenerator(self,percentagesList):
		cumulativeSum = []
		for x in range(len(percentagesList)):
			cumulativeSum.append(sum(percentagesList[x:]))

		randomNumer = random.random()
		# print(randomNumer)
		size = len(cumulativeSum)
		for x in range(size):
			if x+1 < size and randomNumer <= cumulativeSum[x] and randomNumer > cumulativeSum[x+1]:
				return x
			if x + 1 == size and randomNumer <= cumulativeSum[x] and randomNumer > 0:
				return x




def main():
	if len(sys.argv) == 3:
		blueNode(sys.argv[1],int(sys.argv[2]))
	else:
		print("Error!! To compile do it like this: python3 blueNode.py MyIP MyPort OtherIP OtherPort")
		exit()

if __name__ == "__main__":
	main()
