import copy, struct, pickle

class obPackage:

    '''
        EFE: Consturye la clase y sus atributos por defecto
        REQ: ---
        MOD: ---
    '''                                           
    def __init__(self, packetCategory = -1, nodeID = -1, neighborID = -1, blueAddressIP = '999.999.999.999', blueAddressPort = 0000, fileIDByte1 = 0, fileIDRest = 0, chunkID = 0, chunkPayload = b'0',filename=""):
        # Todos los espacios del header
        self.packetCategory = packetCategory
        self.nodeID = nodeID
        self.neighborID = neighborID
        self.blueAddressIP = blueAddressIP
        self.blueAddressPort = blueAddressPort
        self.fileIDByte1 = fileIDByte1
        self.fileIDRest = fileIDRest
        self.chunkID = chunkID
        self.chunkPayload = chunkPayload
        self.fileName = filename
        

    '''
        EFE: Imprime la info del paquete
        REQ: ---
        MOD: ---
    '''
    def print_data(self):
        print(" packetCategory:",self.packetCategory, " nodeId:",self.nodeID ," neighborID:",self.neighborID," blueAddressIP: ", self.blueAddressIP, 
        "blueAddressPort:", self.blueAddressPort,"chunkPayload: ",self.chunkPayload," fileIDByte1: ",self.fileIDByte1," fileIDRest: ",self.fileIDRest,
        " chunkID: ",self.chunkID,"fileName: ",self.fileName)
    '''
        EFE: Serializa el paquete
        REQ: ---
        MOD: bytePacket
    '''
    def serialize(self,tipo):
        #Tipo joinGraph
        if (tipo == 0 or tipo == 7): #chunk
            bytePacket = struct.pack('!bBHI',self.packetCategory,self.fileIDByte1,self.fileIDRest,self.chunkID)
            bytePacket += self.chunkPayload
        elif tipo == 1: #hello
            bytePacket = struct.pack('!bH',self.packetCategory,self.nodeID)
        elif (tipo == 2 or tipo == 3 or tipo == 4 or tipo == 6 or tipo == 8 or tipo == 10): #exists, exists r, complete, get, locate, delete
            bytePacket = struct.pack('!bBH',self.packetCategory,self.fileIDByte1,self.fileIDRest)
        elif tipo == 5: #complete reply
            bytePacket = struct.pack('!bBHI',self.packetCategory,self.fileIDByte1,self.fileIDRest,self.chunkID)
        elif tipo == 9: #locate reply
            bytePacket = struct.pack('!bBHH',self.packetCategory,self.fileIDByte1,self.fileIDRest,self.nodeID)
        elif (tipo == 11 or tipo == 12 or tipo == 18 or tipo == 13): #join tree, join tree r (i do), join tree r (i do not), daddy
            bytePacket = struct.pack('!bH',self.packetCategory,self.nodeID)
        elif tipo == 14: #join graph
            bytePacket = struct.pack('!b',self.packetCategory)
        elif tipo == 15: #yourGraphPosition
            bytePacket = struct.pack('!bHH',self.packetCategory,self.nodeID,self.neighborID)
        elif tipo == 16: #yourGraphPosition
            ipSplit = self.blueAddressIP.split(".") # Esto es para separar el ip en 4 bytes y mandarlo
            bytePacket = struct.pack('!bHHBBBBH',self.packetCategory,self.nodeID,self.neighborID,int(ipSplit[0]),int(ipSplit[1]),int(ipSplit[2]),int(ipSplit[3]),self.blueAddressPort)
        elif tipo == 17: #graphComplete
            bytePacket = struct.pack('!b',self.packetCategory)
        elif tipo == 20: #dummyGreen to Green put Chunk
            bytePacket = struct.pack('!bI',self.packetCategory,self.chunkID)
            bytePacket += self.fileName.encode(encoding='UTF-8',errors='replace')

        return bytePacket

    '''
        EFE: Deserializa el paquete entrante
        REQ: Paquete serializado
        MOD: ---
    '''
    def unserialize(self, bytePacket,tipo):
        if (tipo == 0 or tipo == 7): #main packet, chunk
            processedPacket = struct.unpack('!bBHI',bytePacket[:struct.calcsize('!bBHI')])
            self.packetCategory = processedPacket[0]
            self.fileIDByte1 = processedPacket[1]
            self.fileIDRest = processedPacket[2]
            self.chunkID = processedPacket[3]
            self.chunkPayload = bytePacket[struct.calcsize('!bBHI'):]

        elif tipo == 1: #hello
            processedPacket = struct.unpack('!bH', bytePacket)
            self.packetCategory = processedPacket[0]
            self.nodeID = processedPacket[1]

        elif (tipo == 2 or tipo == 3 or tipo == 4 or tipo == 6 or tipo == 8 or tipo == 10): #exists, exists r, complete, get, locate, delete
            processedPacket = struct.unpack('!bBH', bytePacket)
            self.packetCategory = processedPacket[0]
            self.fileIDByte1 = processedPacket[1]
            self.fileIDRest = processedPacket[2]

        elif tipo == 5: #complete reply
            processedPacket = struct.unpack('!bBHI', bytePacket)
            self.packetCategory = processedPacket[0]
            self.fileIDByte1 = processedPacket[1]
            self.fileIDRest = processedPacket[2]
            self.chunkID = processedPacket[3]

        elif tipo == 9: #locate reply
            processedPacket = struct.unpack('!bBHH', bytePacket)
            self.packetCategory = processedPacket[0]
            self.fileIDByte1 = processedPacket[1]
            self.fileIDRest = processedPacket[2]
            self.nodeID = processedPacket[3]

        elif (tipo == 11 or tipo == 12 or tipo == 18 or tipo == 13): #join tree, join tree r (i do), join tree r (i do not), daddy
            processedPacket = struct.unpack('!bH', bytePacket)
            self.packetCategory = processedPacket[0]
            self.nodeID = processedPacket[1]

        elif tipo == 14: #join graph
            processedPacket = struct.unpack('!b', bytePacket)
            self.packetCategory = processedPacket[0]
            

        elif tipo == 15:
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

        elif tipo == 17: #graphComplete
            processedPacket = struct.pack('!b', bytePacket)
            self.packetCategory = processedPacket[0]
        elif tipo == 20:
            processedPacket = struct.unpack('!bI',bytePacket[:struct.calcsize('!bI')])
            self.packetCategory = processedPacket[0]
            self.chunkID = processedPacket[1]
            self.fileName = bytePacket[struct.calcsize('!bI'):].decode("utf-8")

#----------------------------------------------------------


def main():
    filename = "diego.png"
    obPackagex = obPackage(20)
    obPackagex.fileName = filename
    obPackagex.chunkID = 983
    obPackagex.print_data()
    
    serializedObject = obPackagex.serialize(20)
    print(serializedObject)

    obPackagex2 = obPackage(20)
    obPackagex2.unserialize(serializedObject,20)
    obPackagex2.print_data()



if __name__ == "__main__":
    main()
