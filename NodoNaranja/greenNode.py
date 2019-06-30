from SecureUDP import SecureUdp
from obPackage import obPackage
import threading
import sys
import queue

class greenNode:

    myID = 0
    myGroupID = 1 #This can be change in order to make greens for others teams. In this case is just for LAMDa team
    fileDataBase = {} #[key = (fileIDByte1,fileIDRest)] = (filename,total Chunks of that file)

    def __init__(self,MyID,BlueIP,BluePort):
        SecureUDP = SecureUdp(10,4) #ventana de 10 con timeout de 2s
        print("GreenNode Listening on ip: %s port %d " %
              (SecureUDP.sock.getsockname()[0], SecureUDP.sock.getsockname()[1]))
        #Creates the Threads
        t = threading.Thread(target=self.inputThread, args=(SecureUDP,))
        t.start()
        
        #Del 64 al 95
        #64 = Nuestro primer verde. VerdeID = 0
        self.myID = MyID
        self.fileIDByte1 = 64 +  self.myID


        #Creates a generic putChunk package
        putChunkPack = obPackage(0)
        putChunkPack.fileIDByte1 = self.fileIDByte1
        putChunkPack.fileIDRest = self.fileIDRest


        #Envia los chunks
        for x in range(4):
            chunk = b'elcapi'
            putChunkPack.chunkPayload = chunk
            putChunkPack.chunkID = x
            putChunkPack.print_data()
            serializedObject = putChunkPack.serialize(0)
            SecureUDP.sendto(serializedObject,BlueIP,BluePort)

        #Creates a generic Exists package
        existsPack = obPackage(2)
        existsPack.fileIDByte1 = self.fileIDByte1
        existsPack.fileIDRest = self.fileIDRest
        serializedObject = existsPack.serialize(2)
        SecureUDP.sendto(serializedObject,BlueIP,BluePort)

    def userInputThread(self,SecureUDP):
        while True:
            userIput = input()
            if userIput == "put":
            
    
    def fileIDGenerator(self):


    def chunkSeparator(self,filename,fileIDByte1,fileIDRest):
        chunkID = 0

    def inputThread(self,SecureUDP):
        while True:
            bytePackage , addr = SecureUDP.recivefrom()
            # print(package)
            Type = int.from_bytes(bytePackage[:1], byteorder='big')
            genericPack = obPackage()
            if Type == 3:
                print("FILE EXIST from ",addr)









def main():
    if len(sys.argv) == 4:
        greenNode(int(sys.argv[1]),sys.argv[2],int(sys.argv[3]))
    else:
        print("Error!! To compile do it like this: python3 blueNode.py MyIP MyPort OtherIP OtherPort")
        exit()

if __name__ == "__main__":
    main()
