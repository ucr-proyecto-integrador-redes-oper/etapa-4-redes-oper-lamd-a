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
    blueSavedChunks = [] #Tuple with (ArchivoID,ChunkID,Chunk). Cant be more than 40
    SecureUdp

    def __init__(self,MyIP,MyPort,OtherIP,OtherPort):
        SecureUDP = SecureUdp(10,4,MyIP,MyPort) #ventana de 10 con timeout de 2s
        # Creates the Threads
        t = threading.Thread(target=self.inputThread, args=(SecureUDP,))
        t.start()

        t2 = threading.Thread(target=self.logicalThread, args=(SecureUDP,))
        t2.start()


        obPackagex = obPackage(14)
        serializedObject = obPackagex.serialize(14)
        SecureUDP.sendto(serializedObject,OtherIP,OtherPort)

    def inputThread(self,SecureUDP):
        while True:
            payload , addr = SecureUDP.recivefrom()
            print(payload)
            self.packageQueue.put((payload,addr))




    def logicalThread(self,SecureUDP):
        while True:
            package = self.packageQueue.get(block=True,timeout=None)
            print(package)
            bytePackage = package[0]
            Type = int.from_bytes(bytePackage[:1], byteorder='big')
            if Type == 0:
                print("(PutChunk) from ",package[1])
                chunkPack = obPackage()
                chunkPack.unserialize(bytePackage,0)
                #If theres less than 40 chunks saved, then save the chunk
                if len(blueSavedChunks) < 40:
                    blueSavedChunks.append(chunkPack.chunk)
                #Otherwise it sends the chunk to the neighbors
                else:
                    #Creates a putChunk package
                    serializedPutChunkPack = chunkPack.serialize(0)
                    for neighbor in neighborTuple:
                        SecureUDP.sendto(serializedPutChunkPack,neighbor[1],neighbor[2])


            elif Type == 1:
                print("(Hello) from ",package[1])
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
                SecureUDP.sendto(serializedHelloPack,obPackagex.blueAddressIP,obPackagex.blueAddressPort)

            elif Type == 17:
                print("(GraphComplete) from ",package[1])






def main():
    if len(sys.argv) == 5:
        blueNode(sys.argv[1],int(sys.argv[2]),sys.argv[3],int(sys.argv[4]))
    else:
        print("Error!! To compile do it like this: python3 blueNode.py MyIP MyPort OtherIP OtherPort")
        exit()

if __name__ == "__main__":
    main()
