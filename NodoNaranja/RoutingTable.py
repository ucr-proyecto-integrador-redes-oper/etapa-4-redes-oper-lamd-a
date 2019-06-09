# Struct that represents each of the nodes
class Small_struct:
    """
        Efe: Creates an instance of the class with 3 attributes (node ip and port)
        Req: All the three attributes and having node and port as integers and ip as a string
        Mod: ---
    """

    def __init__(self, node, ip, port):
        self.node = node
        self.ip = ip
        self.port = port

    """
        Efe: Print the values of the attributes
        Req: ---
        Mod: ---
    """

    def print_data(self):
        print("Node (", str(self.node), ") - ip(",
              self.ip, ") - port(", str(self.port), ")")

####################################################################################


class RoutingTable:
    """
        Efe: Creates an instance of the routing table
        Req: routingTableDir = complete directory and name of the file used to create the routing table
        Mod: The instance called table which is a list of the information pero node
    """

    def __init__(self, routingTableDir):
        self.table = []  # [smallStruct_0, smallStruct_1]
        self.constructTable(routingTableDir)

    """
        Efe: Open the file of the nodes and begin the parse of it
        Req: The complete directory and name of the file to parse
        Mod: The list of instances representing each of the nodes
    """

    def constructTable(self, routingTableDir):

        try:
            file = open(routingTableDir, "r")
            content = file.readlines()
            for index, line in enumerate(content):
                if index != 0:
                    self.parseLine(line)  # Ahora se parsea la linea
            file.close()
        except IOError:
            print("Error: cant find the file")

    """
        Efe: parse each line of the file
        Req: one line of the file
        Mod: ---
    """
    def parseLine(self, line):
        node = int(line[0:1])  # nodo
        ip = str(line[2:line.index(":")])  # ip
        port = int(line[line.index(":")+1: len(line)])  # port
        ss = Small_struct(node, ip, port)
        self.table.append(ss)

    """
        Efe: Print the details of each of the instances stored in the table list
        Req: ---
        Mod: ---
    """
    def printTable(self):
        for x in self.table:
            x.print_data()

    """
        Efe: Retrieve information of one of the nodes stored in the table list
        Req: a valid node
        Mod: ---
    """
    def retrieveAddress(self, node):
        for item in self.table:
            if item.getNode() == node:  # This was a item.getNode() is node
                address = (item.getIp(), item.getPort())
                return address

# def main():
#     #Creando un routing table
#     rt = RoutingTable()
#     rt.printTable()

#     #La siguiente es la dupla
#     result = rt.retrieveAddress(3)
#     print(result[0], " - ", result[1])


# if __name__ == "__main__":
#     main()
