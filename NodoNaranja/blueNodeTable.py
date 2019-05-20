
import csv, socket, random, sys


# REQUESTED_ADDRESS = ('0.0.0.0',-2)
class blueNodeTable:

  def __init__(self,blueGraphDir):
    self.graphOfBlueNodes = {}  #[key = node] = NeighborsAdress
    self.addressesOfBlueNodes = {}
    self.availableBlueNodes = []
    self.EMPTY_ADDRESS = ('0.0.0.0',-1)
    try:
      with open(blueGraphDir, newline='') as File:  
        reader = csv.reader(File)
        for row in reader:
          self.graphOfBlueNodes[int(row[0])] = list(map(int,row[1:]))
          self.availableBlueNodes.append(int(row[0]))
    except IOError:
          print("ErrorOrangeGraph: cant fint the file %s" % (blueGraphDir))
          exit()
        
        
  def printgraphOfBlueNodes(self):         
   for x in self.graphOfBlueNodes:
    print("Im node %d my Neighbors are %s" % (x,self.graphOfBlueNodes[x]) )
    
   for x in self.graphOfBlueNodes[2]:
    print(type(x))
       
            
  def markNodeAsRequested(self, requestedNode):
   # self.addressesOfBlueNodes[requestedNode] = REQUESTED_ADDRESS
   self.availableBlueNodes.remove(requestedNode)
  
  def obtainAvailableNode(self):
      availableNode = random.choice(self.availableBlueNodes)
      return availableNode

  def write(self, nodeToWrite, tupleAddress):
    self.availableBlueNodes.remove(nodeToWrite) #Probably unnecesary, since there will always be a request packet before a write packet
    self.addressesOfBlueNodes[nodeToWrite] = tupleAddress
    
  def nodeHasAddress(self, nodeToCheck):
    return nodeToCheck in self.addressesOfBlueNodes

  def obtainNodeAddress(self, nodeToCheck):
    if self.nodeHasAddress(nodeToCheck):
      resultingAddress = self.addressesOfBlueNodes[nodeToCheck]
    else:
      resultingAddress = self.EMPTY_ADDRESS
    return resultingAddress

  def obtainNodesNeighborsAdressList(self, mainNode):
    listOfNeighbors = self.graphOfBlueNodes[mainNode]
    neighborsAddressList =  []
    
    for neighborNode in listOfNeighbors:
      if self.nodeHasAddress(neighborNode):
        neighborTuple = (neighborNode,) + self.obtainNodeAddress(neighborNode)
        neighborsAddressList.append(neighborTuple)  # (Node IP PORT)
    return neighborsAddressList






if __name__== "__main__":

    myBlueNodeTable = blueNodeTable("Grafo_Referencia.csv")
    myBlueNodeTable.write(5,('125.1.25.134',88885))
    myBlueNodeTable.write(4,('125.1.25.134',88884))
    #myBlueNodeTable.write(9,('125.1.25.134',88889))
    myBlueNodeTable.write(8,('125.1.25.134',88888))
    myBlueNodeTable.markNodeAsRequested(2)
    print(myBlueNodeTable.availableBlueNodes)
    print(myBlueNodeTable.obtainNodesNeighborsAdressList(5))
    print(myBlueNodeTable.obtainAvailableNode())
 
