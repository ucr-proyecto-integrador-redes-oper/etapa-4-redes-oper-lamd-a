import csv
import socket
import random
import sys

# REQUESTED_ADDRESS = ('0.0.0.0',-2)

class blueNodeTable:
	'''
		EFE: Construye la tabla de azules con una empty_address.
		REQ: ---
		MOD: ---
	'''
	def __init__(self, blueGraphDir):
		self.graphOfBlueNodes = {}  # [key = node] = NeighborsAdress
		self.addressesOfBlueNodes = {} # [key = node] = NodeAdress
		self.availableBlueNodes = [] # Lista de nodos
		self.EMPTY_ADDRESS = ('0.0.0.0', -1)
		try:
			with open(blueGraphDir, newline='') as File:
				reader = csv.reader(File)
				for row in reader:
					self.graphOfBlueNodes[int(row[0])] = list(map(int, row[1:]))
					self.availableBlueNodes.append(int(row[0]))
		except IOError:
			print("ErrorOrangeGraph: cant fint the file %s" % (blueGraphDir))
			exit()

	'''
		EFE: Imprime el grafo
		REQ: Grafo inicializado
		MOD: ---
	'''
	def printgraphOfBlueNodes(self):
		for x in self.graphOfBlueNodes:
			print("Im node %d my Neighbors are %s" % (x, self.graphOfBlueNodes[x]))
		for x in self.graphOfBlueNodes[2]:
			print(type(x))
	
	'''
		EFE: Marca un nodo como solicitado para que no pueda ser escrito por otros
		REQ: El nodo tiene que existir
		MOD: availableBlueNodes
	'''
	def markNodeAsRequested(self, requestedNode):
			# self.addressesOfBlueNodes[requestedNode] = REQUESTED_ADDRESS
		try:
			self.availableBlueNodes.remove(requestedNode)
		except ValueError:
			print("node %d already removed" % (requestedNode))

	'''
		EFE: Devuelve una lista con los nodos disponibles
		REQ: Grafo inicializado
		MOD: availableBlueNodes
	'''
	def obtainAvailableNode(self):
		try:
			availableNode = random.choice(self.availableBlueNodes)
			return self.availableBlueNodes[availableNode]
		except IndexError:
			return -1

	'''
		EFE: Escribe definitivamente que el nodo ya está inicializado
		REQ: El nodo debe estar markNodeAsRequested
		MOD: addressesOfBlueNodes
	'''
	def write(self, nodeToWrite, tupleAddress):
			# self.availableBlueNodes.remove(nodeToWrite) #Probably unnecesary, since there will always be a request packet before a write packet
		self.addressesOfBlueNodes[nodeToWrite] = tupleAddress

	'''
		EFE: Retorna si el nodo solicitado ya tiene una adress asignada
		REQ: Que el nodo exista
		MOD: ---
	'''
	def nodeHasAddress(self, nodeToCheck):
		return nodeToCheck in self.addressesOfBlueNodes

	'''
		EFE: Retorna el adress del nodo solicitado
		REQ: ---
		MOD: ---
	'''
	def obtainNodeAddress(self, nodeToCheck):
		if self.nodeHasAddress(nodeToCheck):
			resultingAddress = self.addressesOfBlueNodes[nodeToCheck]
		else:
			resultingAddress = self.EMPTY_ADDRESS
		return resultingAddress

	'''
		EFE: Retorna una lista con todos los vecinos disponibles
		REQ: El nodo debe existir
		MOD: ---
	'''
	def obtainNodesNeighborsAdressList(self, mainNode):
		listOfNeighbors = self.graphOfBlueNodes[mainNode]
		neighborsAddressList = []

		for neighborNode in listOfNeighbors:
			if self.nodeHasAddress(neighborNode):
				neighborTuple = (neighborNode,) + \
					self.obtainNodeAddress(neighborNode)
				neighborsAddressList.append(
					neighborTuple)  # (Node IP PORT)
		return neighborsAddressList


if __name__ == "__main__":

    myBlueNodeTable = blueNodeTable("Grafo_Referencia.csv")
    myBlueNodeTable.write(5, ('125.1.25.134', 88885))
    myBlueNodeTable.write(4, ('125.1.25.134', 88884))
    # myBlueNodeTable.write(9,('125.1.25.134',88889))
    myBlueNodeTable.write(8, ('125.1.25.134', 88888))
    myBlueNodeTable.markNodeAsRequested(2)
    print(myBlueNodeTable.availableBlueNodes)
    print(myBlueNodeTable.obtainNodesNeighborsAdressList(5))
    print(myBlueNodeTable.obtainAvailableNode())
