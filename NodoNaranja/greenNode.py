from SecureUDP import SecureUdp
from obPackage import obPackage
import threading
import sys , os
import queue
import math
import time

class greenNode:

    myID = 0
    myGroupID = 2 #This can be change in order to make greens for others teams. In this case is just for LAMDa team
    fileDataBase = {} #[key = (fileIDByte1 , fileIDRest) ] = (filename,total Chunks of that file)
    fileIDByte1 = 0
    fileIDRest = 0
    SecureUDP = 0
    BlueIP = ""
    BluePort = 0
    existsMap = {} # [key = (fileIDByte1,fileIDRest)] = (TimeStamp,IP,PORT)
    locateMap = {} # [key = (fileIDByte1,fileIDRest)] = (TimeStamp,IP,PORT,ListBlueNodes)
    inputQueue = queue.Queue() # Tuple (pack,addr)

    def __init__(self,myGroupID,MyID,BlueIP,BluePort):
        self.SecureUDP = SecureUdp(100,1,True) #ventana de 10 con timeout de 1s
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

            t2 = threading.Thread(target=self.userInputThread, args=())
            t2.start()

            t3 = threading.Thread(target=self.logicThread, args=())
            t3.start()

        else:
            print("Sorry This GreenNodeID: ",str(self.myID)," is not available for the Group ",str(self.myGroupID))
            os._exit(0)

    def userInputThread(self):
        while True:
            userInput = input()
            if userInput == "1":
                print("Files ",self.fileDataBase)
                # filename = input("Enter path of the file: ")

                # self.fileDataBase[self.fileIDRest] = (filename,0)
                # print("Your ID for the file ",filename," is: fileIDByte1: ",self.fileIDByte1," fileIDRest: ",self.fileIDRest)
                # self.chunkSeparator(filename,self.fileIDByte1,self.fileIDRest)
                # self.fileIDRest += 1
            elif userInput == "2": #Check if file Exist
                print("Going to check if a file exist")
                fileIDByte1 = input("Enter fileIDByte1: ")
                fileIDRest = input("Enter fileIDRest: ")
                #Creates a generic Exists package
                
                TimeStamp = time.time()
                ListBlueNodes = []
                self.locateMap[(int(fileIDByte1),int(fileIDRest))] = (TimeStamp,self.BlueIP,self.BluePort,ListBlueNodes)
                
                existsPack = obPackage(8)
                existsPack.fileIDByte1 = int(fileIDByte1)
                existsPack.fileIDRest = int(fileIDRest)
                serializedObject = existsPack.serialize(8)


                self.SecureUDP.sendto(serializedObject,self.BlueIP,self.BluePort)

                


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
        #chunkID = 0
        #Creates a generic putChunk package
        chunkPacketToSend = obPackage(0)
        chunkPacketToSend.fileIDByte1 = fileIDByte1
        chunkPacketToSend.fileIDRest = fileIDRest

        fd = os.open(filename, os.O_RDWR)
        totalChunks = math.ceil(os.fstat(fd).st_size/1024)
        self.fileDataBase[(fileIDByte1,fileIDRest)] = (filename, totalChunks)

        #Envia los chunks
        for chunkID in range(totalChunks):             
            
            fileSlice = os.read(fd,1024)
            chunkPacketToSend.chunkPayload = fileSlice
            chunkPacketToSend.chunkID = chunkID
            # chunkPacketToSend.print_data()
            serializedObject = chunkPacketToSend.serialize(0)
            self.SecureUDP.sendto(serializedObject,self.BlueIP,self.BluePort)

        os.close(fd)
        print("File: ",filename ,"sent ",self.fileDataBase[(fileIDByte1,fileIDRest)])

    def inputThread(self):
        while True:
            bytePackage , addr = self.SecureUDP.recivefrom()
            # print("re",bytePackage)
            self.inputQueue.put((bytePackage,addr))



    def logicThread(self):
        while True:
            # If the queue is not empty
            if not self.inputQueue.empty():
                # print("IM in")
                inputPack = self.inputQueue.get()
                bytePackage = inputPack[0]
                addr = inputPack[1] 
                # print(inputPack)
                Type = int.from_bytes(bytePackage[:1], byteorder='big')
                genericPack = obPackage()
                if Type == 3:
                    print("(EXIST Resp) from ",addr)
                    genericPack.unserialize(bytePackage,3)
                    print("The File (",str(genericPack.fileIDByte1),str(genericPack.fileIDRest),") Exist")
                    
                    if (genericPack.fileIDByte1,genericPack.fileIDRest) in self.existsMap:
                        print("Enviando1")
                        responseAddr = self.existsMap[(genericPack.fileIDByte1,genericPack.fileIDRest)]
                        test = obPackage(3)
                        test.fileIDByte1 = genericPack.fileIDByte1
                        test.fileIDRest = genericPack.fileIDRest
                        test.print_data()
                        test = genericPack.serialize(3)
                        self.SecureUDP.sendto(test,responseAddr[1],responseAddr[2])
                        del self.existsMap[(genericPack.fileIDByte1,genericPack.fileIDRest)]
                    else:
                        print("Error!!! That file no longer exist")
                elif Type == 20: #Going to recieve a new file
                    genericPack.unserialize(bytePackage,20)
                    print("New File: ",genericPack.fileName)
                    #genericPack.print_data()
                    
                    #Sends the id of the file to the user
                    responseNewFilePack = obPackage(2)
                    responseNewFilePack.fileIDByte1 = self.fileIDByte1
                    responseNewFilePack.fileIDRest = self.fileIDRest
                    byteResponseNewFilePack = responseNewFilePack.serialize(2)
                    self.SecureUDP.sendto(byteResponseNewFilePack,addr[0],addr[1])

                    #Separates the file into chunks
                    self.chunkSeparator(genericPack.fileName,self.fileIDByte1,self.fileIDRest)

                    self.fileIDRest += 1
                elif Type == 2:
                    print("(Exist) from ",addr)
                    existsPack = obPackage(2)
                    existsPack.unserialize(bytePackage,2)
                    TimeStamp = time.time()
                    self.existsMap[(existsPack.fileIDByte1,existsPack.fileIDRest)] = (TimeStamp,addr[0],addr[1])
                    serializedObject = existsPack.serialize(2)
                    self.SecureUDP.sendto(serializedObject,self.BlueIP,self.BluePort)
                elif Type == 8:
                    print("(Locate) from ",addr)
                    locatePack = obPackage(8)
                    locatePack.unserialize(bytePackage,8)
                    TimeStamp = time.time()
                    ListBlueNodes = []
                    self.locateMap[(locatePack.fileIDByte1,locatePack.fileIDRest)] = (TimeStamp,addr[0],addr[1],ListBlueNodes)
                    serializedObject = locatePack.serialize(8)
                    self.SecureUDP.sendto(serializedObject,self.BlueIP,self.BluePort)
                elif Type == 9:
                    print("(Locate Res) from ",addr)
                    locateResPack = obPackage(9)
                    locateResPack.unserialize(bytePackage,9)
                    fileIDByte1 = locateResPack.fileIDByte1
                    fileIDRest = locateResPack.fileIDRest
                    #If theres a request for that FileID
                    if (fileIDByte1,fileIDRest) in self.locateMap:
                        #If the TimeOut is not over
                        if (time.time() - self.locateMap[(fileIDByte1,fileIDRest)][0]) <= 10:
                            #Add the blueNode to the listBlueNodes
                            self.locateMap[(fileIDByte1,fileIDRest)][3].append(str(locateResPack.nodeID))
                
            else:
                #Checks TimeOuts for the exist request. TimeOut is 5s
                for request in list(self.existsMap):
                    if ( time.time() - self.existsMap[request][0]) >= 5:
                        print("self.existsMap[request]")
                        genericPack = obPackage(3)
                        serializedObject = genericPack.serialize(3)
                        self.SecureUDP.sendto(serializedObject,self.existsMap[request][1],self.existsMap[request][2])
                        del self.existsMap[request]

                #Checks TimeOuts for the Locate request. TimeOut is 10s
                for request in list(self.locateMap):
                    if ( time.time() - self.locateMap[request][0]) > 10:
                        print("Sending locateMap for ",request)
                        locateListPack = obPackage(20)
                        locateListPack.fileName = ';'.join(self.locateMap[request][3]) #1;2;...;4  NodeID;NodeID;...;NodeID
                        byteLocateListPack = locateListPack.serialize(20)
                        self.SecureUDP.sendto(byteLocateListPack,self.locateMap[request][1],self.locateMap[request][2])
                        del self.locateMap[request]











def main():
    if len(sys.argv) == 5:
        greenNode(int(sys.argv[1]),int(sys.argv[2]),sys.argv[3],int(sys.argv[4]))
    else:
        print("Error!! To compile do it like this: python3 blueNode.py MyIP MyPort OtherIP OtherPort")
        exit()

if __name__ == "__main__":
    main()
