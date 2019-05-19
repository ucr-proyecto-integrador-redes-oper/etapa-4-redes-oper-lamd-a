import csv
import socket
 
# Store the nodes
Graph = []
# Diccionary for nodes (key=id content = ip:addr)
nodeMap ={} 
class blueNodeTable():


    def genGraph():
        with open('Grafo_Referencia.csv', newline='') as File:  
            reader = csv.reader(File)
            for row in reader:
                #print(row) Test
                Graph.append(row)

    def genNodeMap()
    



'''
    #Check if the node is avilable
    def availableNode(self, node):
        if node in Graph:
            return True
        else:
            return False
'''


#if __name__== "__main__":
