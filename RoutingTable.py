class Small_struct:
    def __init__(self, nodo, ip, port):
        self.nodo = nodo
        self.ip = ip
        self.port = port

    def print_data(self):
        print("Nodo(", self.nodo ,") - ip(", self.ip, ") - port(", self.port ,")")

class RoutingTable:
    def __init__(self):
        self.table = [] #[smallStruct_0, smallStruct_1]
        self.constructTable()

    #Metodo que se encarga del paseo del file para crear la tabla de enrutamiento
    def constructTable(self):
        file = open("data.txt", "r")
        content = file.readlines()
        for line in content:
            self.parseLine(line) #Ahora se parsea la linea
        file.close()

    def parseLine(self, line):
        nodo = int(line[0:1]) #nodo
        ip = str(line[2:line.index(":")]) #ip
        port = int(line[line.index(":")+1: len(line)]) #port
        ss = Small_struct(nodo, ip, port)
        self.table.append(ss)

    def printTable(self):
        for x in self.table:
            x.print_data();

    def retrieve_address(self, node): #-> socket::addr
        print("falta implementar")

    #def -forward packet based on routing table si no soy yo se forwardea sino soy yo y se consume

def main():
    rt = RoutingTable()
    rt.printTable()

if __name__ == "__main__":
    main()