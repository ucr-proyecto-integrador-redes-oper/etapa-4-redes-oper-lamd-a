import copy, struct, pickle

class obPackage:

    '''
        EFE: Consturye la clase y sus atributos por defecto
        REQ: ---
        MOD: ---
    '''                                           
    def __init__(self, packetCategory = -1, nodeID = -1, neighborID = -1, blueAddressIP = '999.999.999.999', blueAddressPort = 0000 ):
        # Todos los espacios del header
        self.packetCategory = packetCategory
        self.nodeID = nodeID
        self.neighborID = neighborID
        self.blueAddressIP = blueAddressIP
        self.blueAddressPort = blueAddressPort
        

    '''
        EFE: Imprime la info del paquete
        REQ: ---
        MOD: ---
    '''
    def print_data(self):
        print(" packetCategory:",self.packetCategory, " nodeId:",self.nodeID ," neighborID:",self.neighborID," blueAddressIP: ", self.blueAddressIP, "blueAddressPort:", self.blueAddressPort)
    '''
        EFE: Serializa el paquete
        REQ: ---
        MOD: bytePacket
    '''
    def serialize(self,tipo):
        #Tipo joinGraph
        if tipo == 14:
            bytePacket = struct.pack('!b',self.packetCategory)
        elif tipo == 15:
            bytePacket = struct.pack('!bHH',self.packetCategory,self.nodeID,self.neighborID)
        elif tipo == 16:
            ipSplit = self.blueAddressIP.split(".") # Esto es para separar el ip en 4 bytes y mandarlo
            bytePacket = struct.pack('!bHHBBBBH',self.packetCategory,self.nodeID,self.neighborID,int(ipSplit[0]),int(ipSplit[1]),int(ipSplit[2]),int(ipSplit[3]),self.blueAddressPort)
        elif tipo == 17:
            bytePacket = struct.pack('!b',self.packetCategory)
        elif tipo == 1:
            bytePacket = struct.pack('!b',self.packetCategory)
        return bytePacket

    '''
        EFE: Deserializa el paquete entrante
        REQ: Paquete serializado
        MOD: ---
    '''
    def unserialize(self, bytePacket,tipo):

        if tipo == 15:
            processedPacket = struct.unpack('!bHH',bytePacket)
            self.packetCategory = processedPacket[0]
            self.nodeID = processedPacket[1]
            self.neighborID = processedPacket[2]
        elif tipo == 16:
            processedPacket = struct.unpack('!bHHBBBBH',bytePacket)
            self.packetCategory = processedPacket[0]
            self.nodeID = processedPacket[1]
            self.neighborID = processedPacket[2]
            
            #Reconstruye el ip. Dado que esta repartido en 4 bytes
            ip = ""
            for x in range(4):
                ip = ip + str(processedPacket[x+3])
                if x < 3:
                    ip = ip + "."
            self.blueAddressIP = ip
            self.blueAddressPort = processedPacket[7]
#----------------------------------------------------------


def main():

# testing type 14
    # obPackagex = obPackage(14)
    # obPackagex.print_data()
    # serializedObject = obPackagex.serialize(14)
    # print(serializedObject)

# Testing type 15
    # obPackagex = obPackage(15,32766,32766)
    # obPackagex.print_data()
    # serializedObject = obPackagex.serialize(15)
    # print(serializedObject)

# Testing type 16
#     obPackagex = obPackage(16,7,10,"10.1.135.32",90)
#     obPackagex.print_data()
#     serializedObject = obPackagex.serialize(16)
#     print(serializedObject)


# testing type 17
    obPackagex = obPackage(17)
    obPackagex.print_data()
    serializedObject = obPackagex.serialize(17)
    print(serializedObject)


    if int.from_bytes(serializedObject[:1], byteorder='big') == 14:
        print("Tipo JoinGraph")
    elif int.from_bytes(serializedObject[:1], byteorder='big') == 15:
        print("Tipo yourGraphposition")
        obPackagex.unserialize(serializedObject,15)
        obPackagex.print_data()
    elif int.from_bytes(serializedObject[:1], byteorder='big') == 16:
        print("Tipo yourGraphposition2")
        obPackagex.unserialize(serializedObject,16)
        obPackagex.print_data()
    elif int.from_bytes(serializedObject[:1], byteorder='big') == 17:
        print("Tipo GraphComplete")

if __name__ == "__main__":
    main()
