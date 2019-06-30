from SecureUDP import SecureUdp
from obPackage import obPackage
import threading
import sys
import queue

class blueNode:
    neighborTuple = []# Tuple with (NodeID,IP,PORT)
    sTreeDadNode = -1
    sTreeSonsNodes = []
    myID = 0
    packageQueue = queue.Queue() # Tuple with (bytePackage,addr). Addr is a tuple with the ip and port 
    chunksStored = 0 #Cant be more than 40
    blueSavedChunks = {} # [key = (fileIDByte1,fileIDRest)] = tuples (chunkID,Chunk).The key helps to find the FileID then list holds all the chunks stored from that fileID
    SecureUDP = 0
    def __init__(self,orangeIP,orangePort):
        self.SecureUDP = SecureUdp(10,4,False) #ventana de 10 con timeout de 2s
        print("BlueNode Listening on ip: %s port %d " %
              ( self.SecureUDP.sock.getsockname()[0], self.SecureUDP.sock.getsockname()[1]))
        # Creates the Threads
        t = threading.Thread(target=self.inputThread, args=())
        t.start()

        t2 = threading.Thread(target=self.logicalThread, args=())
        t2.start()

        t2 = threading.Thread(target=self.userInputThread, args=())
        t2.start()

        obPackagex = obPackage(14)
        serializedObject = obPackagex.serialize(14)
        self.SecureUDP.sendto(serializedObject,orangeIP,orangePort)

    def inputThread(self):
        while True:
            payload , addr = self.SecureUDP.recivefrom()
            # print(payload)
            self.packageQueue.put((payload,addr))


    def userInputThread(self):
        while True:
            user = input()
            if user == '$':
                print("myID ",str(self.myID)," neighbors ",self.neighborTuple, " chunksStored: ",self.chunksStored , " blueSavedChunks: ",self.blueSavedChunks)

    def logicalThread(self):
        while True:
            package = self.packageQueue.get(block=True,timeout=None)
            # print(package)
            bytePackage = package[0]
            Type = int.from_bytes(bytePackage[:1], byteorder='big')
            genericPack = obPackage()
            if Type == 0:
                print("(PutChunk) from ",package[1])
                chunkPack = obPackage()
                chunkPack.unserialize(bytePackage,0)
                #chunkPack.print_data()
                #If theres less than 40 chunks saved, then save the chunk
                if self.chunksStored < 40:
                    #Checks if the key exists
                    if (chunkPack.fileIDByte1,chunkPack.fileIDRest) in self.blueSavedChunks:
                        #If the key exists then just append the new chunkID and chunkPayload
                        self.blueSavedChunks[(chunkPack.fileIDByte1,chunkPack.fileIDRest)].append((chunkPack.chunkID,chunkPack.chunkPayload))
                        
                    else:
                        #If not then creates a list witht the chunkID and chunkPayload and assign it to the key
                        tempList = []
                        tempList.append((chunkPack.chunkID,chunkPack.chunkPayload))
                        self.blueSavedChunks[(chunkPack.fileIDByte1,chunkPack.fileIDRest)] = tempList

                    self.chunksStored += 1

                #Otherwise it sends the chunk to the neighbors
                else:
                    #Creates a putChunk package
                    serializedPutChunkPack = chunkPack.serialize(0)
                    for neighbor in self.neighborTuple:
                        self.SecureUDP.sendto(serializedPutChunkPack,neighbor[1],neighbor[2])


            elif Type == 1:
                print("(Hello) from ",package[1])
            elif Type == 2:
                print("(Exist) from ",package[1])
                genericPack.unserialize(bytePackage,2)
                #Checks if I have a chunk of that file
                if (genericPack.fileIDByte1,genericPack.fileIDRest) in self.blueSavedChunks:
                    genericPack.packetCategory = 3
                    responseExist = genericPack.serialize(3)
                    self.SecureUDP.sendto(responseExist,package[1][0],package[1][1])
                
            elif Type == 15:
                print("(NeighborNoAddrs) from ",package[1])
                obPackagex = obPackage()
                obPackagex.unserialize(bytePackage,15)
                self.neighborTuple.append((obPackagex.neighborID,"0.0.0.0",-1))
                self.myID = obPackagex.nodeID
            elif Type == 16:
                print("(Neighbor) from ",package[1])
                obPackagex = obPackage()
                obPackagex.unserialize(bytePackage,16)
                self.neighborTuple.append((obPackagex.neighborID,obPackagex.blueAddressIP,obPackagex.blueAddressPort))
                self.myID = obPackagex.nodeID
                helloPack = obPackage(1)
                serializedHelloPack = helloPack.serialize(1)
                self.SecureUDP.sendto(serializedHelloPack,obPackagex.blueAddressIP,obPackagex.blueAddressPort)

            elif Type == 17:
                print("(GraphComplete) from ",package[1])
                print("vecinos ",self.neighborTuple)






def main():
    if len(sys.argv) == 3:
        blueNode(sys.argv[1],int(sys.argv[2]))
    else:
        print("Error!! To compile do it like this: python3 blueNode.py MyIP MyPort OtherIP OtherPort")
        exit()

if __name__ == "__main__":
    main()
