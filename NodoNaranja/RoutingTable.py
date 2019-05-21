#Struct that represents each of the nodes
class Small_struct:
    def __init__(self, node, ip, port):
        self.node = node
        self.ip = ip
        self.port = port

    #Metodo que imprime los datos relacionados al nodo mencionado
    def print_data(self):
        print("Node(", self.node ,") - ip(", self.ip, ") - port(", self.port ,")")

    #Getter del nodo
    def getNode(self):
        return self.node

    #Getter de la ip
    def getIp(self):
        return self.ip

    #Getter del port
    def getPort(self):
        return self.port

####################################################################################

class RoutingTable:
    #Constructor
    def __init__(self,routingTableDir):
        self.table = [] #[smallStruct_0, smallStruct_1]
        self.constructTable(routingTableDir)

    #Parsing the data.txt file to create the routing table
    def constructTable(self,routingTableDir):
        
        try:
             file = open(routingTableDir, "r")
             content = file.readlines()
             for index, line in enumerate(content):
                 if index != 0:
                   self.parseLine(line) #Ahora se parsea la linea
             file.close()
        except IOError:
             print("Error: cant find the file")

    #Parsing each of the lines of the file
    def parseLine(self, line):
        node = int(line[0:1]) #nodo
        ip = str(line[2:line.index(":")]) #ip
        port = int(line[line.index(":")+1: len(line)]) #port
        ss = Small_struct(node, ip, port)
        self.table.append(ss)

    #Printing the state of the table
    def printTable(self):
        for x in self.table:
            x.print_data();

    #Returns the tuple of address and port regarding to the argument(node)
    def retrieveAddress(self, node):
        for item in self.table:
            if item.getNode() == node: ##This was a item.getNode() is node
                address = (item.getIp(), item.getPort())
                return address

#def main():
#     #Creando un routing table
#     rt = RoutingTable()
#     rt.printTable()

#     #La siguiente es la dupla
#     result = rt.retrieveAddress(3)
#     print(result[0], " - ", result[1])


# if __name__ == "__main__":
#     main()
