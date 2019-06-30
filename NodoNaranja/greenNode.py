from SecureUDP import SecureUdp
from obPackage import obPackage
import threading
import sys , os
import queue

class greenNode:

    myID = 0
    myGroupID = 2 #This can be change in order to make greens for others teams. In this case is just for LAMDa team
    fileDataBase = {} #[key = fileIDRest] = (filename,total Chunks of that file)
    fileIDByte1 = 0
    fileIDRest = 0
    SecureUDP = 0
    BlueIP = ""
    BluePort = 0
    def __init__(self,myGroupID,MyID,BlueIP,BluePort):
        self.SecureUDP = SecureUdp(10,4,True) #ventana de 10 con timeout de 2s
        self.myGroupID = myGroupID
        self.myID = MyID
        self.BlueIP = BlueIP
        self.BluePort = BluePort
        self.fileIDByte1 = self.fileIDByte1Generator()
        if self.fileIDByte1 != -1:
            print("GreenNode Listening on ip: %s port %d " %
                ( self.SecureUDP.sock.getsockname()[0], self.SecureUDP.sock.getsockname()[1]))
            #Creates the Threads
            t = threading.Thread(target=self.inputThread, args=())
            t.start()

            t = threading.Thread(target=self.userInputThread, args=())
            t.start()




        else:
            print("Sorry This GreenNodeID: ",str(self.myID)," is not available for the Group ",str(self.myGroupID))
            os._exit(0)

    def userInputThread(self):
        while True:
            userInput = input()
            if userInput == "1":
                filename = input("Enter path of the file: ")

                self.fileDataBase[self.fileIDRest] = (filename,0)
                print("Your ID for the file ",filename," is: fileIDByte1: ",self.fileIDByte1," fileIDRest: ",self.fileIDRest)
                self.chunkSeparator(filename,self.fileIDByte1,self.fileIDRest)
                self.fileIDRest += 1
            elif userInput == "2": #Check if file Exist
                fileIDByte1 = input("Enter fileIDByte1: ")
                fileIDRest = input("Enter fileIDRest: ")
                #Creates a generic Exists package
                existsPack = obPackage(2)
                existsPack.fileIDByte1 = fileIDByte1
                existsPack.fileIDRest = fileIDRest
                serializedObject = existsPack.serialize(2)
                self.SecureUDP.sendto(serializedObject,BlueIP,BluePort)

                


    def fileIDByte1Generator(self):
        	# 31 verdes por equipo
        # Grupo x = [Grupo*32, (Grupo*32)+31 ]
        # Grupo 1 = 001 [32,63]
        # Grupo 2 = 010 [64,95]
        # Grupo 3 = 011 [96,95]
        # Grupo 4 = 100 [128,159]
        # Grupo 5 = 101 [160,191]
        # Grupo 6 = 110 [192,223]
        fileIDByte1 = (self.myGroupID * 32)
        #Checks if it can create that greenNode
        if (fileIDByte1 + self.myID) > fileIDByte1 + 32:
            return -1
        else:
            return fileIDByte1 + self.myID


    def chunkSeparator(self,filename,fileIDByte1,fileIDRest):
        //chunkID = 0
        #Creates a generic putChunk package
        chunkPacketToSend = obPackage(0)
        chunkPacketToSend.fileIDByte1 = fileIDByte1
        chunkPacketToSend.fileIDRest = fileIDRest
        fileName , totalChunks = self.fileDataBase[fileIDRest]

        fileAsBytes = open(fileName, "rb") # opening for [r]eading as [b]inary

        #Envia los chunks
        for chunkID in range(totalChunks):             
            
            fileSlice = fileAsBytes.read(1024)
            fileAsBytes.seek(1024)
            chunkPacketToSend.chunkPayload = fileSlice
            chunkPacketToSend.chunkID = chunkID
            chunkPacketToSend.print_data()
            serializedObject = chunkPacketToSend.serialize(0)
            self.SecureUDP.sendto(serializedObject,self.BlueIP,self.BluePort)

        print("Testing ",self.fileDataBase[fileIDRest])

    def inputThread(self):
        while True:
            bytePackage , addr = self.SecureUDP.recivefrom()
            # print(package)
            Type = int.from_bytes(bytePackage[:1], byteorder='big')
            genericPack = obPackage()
            if Type == 3:
                print("FILE EXIST from ",addr)
                print("The File ",str(fileIDByte1)," ",str(fileIDRest),"Exist")









def main():
    if len(sys.argv) == 5:
        greenNode(int(sys.argv[1]),int(sys.argv[2]),sys.argv[3],int(sys.argv[4]))
    else:
        print("Error!! To compile do it like this: python3 blueNode.py MyIP MyPort OtherIP OtherPort")
        exit()

if __name__ == "__main__":
    main()
