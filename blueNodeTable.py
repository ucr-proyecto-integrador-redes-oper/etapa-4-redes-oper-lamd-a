import csv
import socket
 
# Store the nodes
Graph = []
# Diccionary for nodes (key=id content = ip:addr)
nodeMap ={} 

class blueNodeTable():

    #Generates the graph
    def genGraph(self):
        with open('Grafo_Referencia.csv', newline='') as File:  
            reader = csv.reader(File)
            for row in reader:
                #print(row) Test
                Graph.append(row)
        return Graph
    
    #Generates the nodemap
    # x for default 
    # -1 for requested
    def genNodeMap(self, MAX_NODES):
        for i in range(0, MAX_NODES):
            nodeMap[i] = "x"
        return nodeMap
 
    # Write, after the accept and confirm the addr(string)
    def write(self, node, addr):
        nodeMap[node] = addr

    #Return a list with the neig...
    def retrieveNeighbors(self, node):
        return Graph[node]

    #Returns neighbors with their address
    #def retrieveNeighbors(self, node):

    #Returns node addr
    def retrieveAddr(self, node):
        if availableNode():
            return nodeMap[node]
        else:
            return "The requested node isn't available"

'''
    #Check if the node is avilable
    def availableNode(self, node):
        if node in Graph:
            return True
        else:
            return False
'''



if __name__== "__main__":

    tables = blueNodeTable()
    print(tables.genGraph())
    print(tables.genNodeMap(5))