import csv
import socket
 
# Store the nodes
Graph = []
# Diccionary for nodes (key=id content = ip:addr)
nodeMap ={} 

class blueNodeTable():

#-----------------------Could be in the __init__-------------------------
    #Generates the graph
    def genGraph(self):
        with open('Grafo_Referencia.csv', newline='') as File:  
            reader = csv.reader(File)
            for row in reader:
                Graph.append(row)
        return Graph
    
    #Generates the nodemap
    # x for default 
    # -1 for requested
    def genNodeMap(self, MAX_NODES): # To be changed
        for i in range(0, MAX_NODES):
            nodeMap[i] = "x"
        return nodeMap
#-----------------------Could be in the __init__-------------------------
 
    # Write, after the accept and confirm the addr(string)
    def write(self, node, addr):
        nodeMap[node] = addr

    #Return a list with the neig...
    def retrieveNeighbors(self, node):
        return Graph[node]

    #Returns neighbors with their address
    #def retrieveNeighbors(self, node):

    #Check if the node is avilable
    def availableNode(self, node):
        if nodeMap[node] == "x" or nodeMap[node] == "-1": #Default
            return False
        else:
            return True

    #Returns node addr
    def retrieveAddr(self, node):
        if self.availableNode(node): #It's free!!
            return nodeMap[node]
        else:
            return -1

    def markAsRequested(self, node):
        nodeMap[node] = "-1"


if __name__== "__main__":

    tables = blueNodeTable()
    tables.genGraph()
    tables.genNodeMap(15)

    tables.write(1, "nodo 1")
    tables.write(2, "nodo 2")
    tables.write(3, "nodo 3")
    tables.write(4, "nodo 4")
    tables.write(5, "nodo 5")
    tables.write(6, "nodo 6")
    tables.write(7, "nodo 7")

    print(tables.retrieveNeighbors(0))

    print(tables.availableNode(1))
    print(tables.availableNode(9))

    tables.markAsRequested(2)
    tables.markAsRequested(10)

    print(tables.retrieveAddr(1))
    print(tables.retrieveAddr(2))
    print(tables.retrieveAddr(3))
    print(tables.retrieveAddr(9))
    print(tables.retrieveAddr(10))