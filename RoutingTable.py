#Estructura que es referencia de cada uno de los nodos
class Small_struct:
    def __init__(self, nodo, ip, port):
        self.nodo = nodo
        self.ip = ip
        self.port = port

    #Metodo que imprime los datos relacionados al nodo mencionado
    def print_data(self):
        print("Nodo(", self.nodo ,") - ip(", self.ip, ") - port(", self.port ,")")

    #Getter del nodo
    def getNodo(self):
        return self.nodo

    #Getter de la ip
    def getIp(self):
        return self.ip

    #Getter del port
    def getPort(self):
        return self.port

####################################################################################

class RoutingTable:
    #Constructor
    def __init__(self):
        self.table = [] #[smallStruct_0, smallStruct_1]
        self.constructTable()

    #Metodo que se encarga del parseo del file para crear la tabla de enrutamiento
    def constructTable(self):
        file = open("data.txt", "r")
        content = file.readlines()
        for index, line in enumerate(content):
            if index != 0:
                self.parseLine(line) #Ahora se parsea la linea
        file.close()

    #Parseo de cada una de las lineas que representa un nodo y guardado en la tabla
    def parseLine(self, line):
        nodo = int(line[0:1]) #nodo
        ip = str(line[2:line.index(":")]) #ip
        port = int(line[line.index(":")+1: len(line)]) #port
        ss = Small_struct(nodo, ip, port)
        self.table.append(ss)

    #Metodo de impresion del estado de la tabla
    def printTable(self):
        for x in self.table:
            x.print_data();

    #Devuelve una dupla del address y el puerto del node que se manda como argumento
    def retrieveAddress(self, node):
        for item in self.table:
            if item.getNodo() is node:
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