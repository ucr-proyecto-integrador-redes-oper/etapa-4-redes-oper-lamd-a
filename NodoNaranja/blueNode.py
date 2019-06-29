from SecureUDP import SecureUdp
from obPackage import obPackage
import threading
import sys
import queue

class blueNode:
    neighborTuple = []# Tuple with (NodeID,IP,PORT,STREE) STREE = When STREE equals 1 it means thats the neighbor with the connection to the root  
    myID = 0
    packageQueue = queue.Queue()

    def __init__(self,MyIP,MyPort,OtherIP,OtherPort):
        SecureUdpOrange = SecureUdp(10,4,MyIP,MyPort) #ventana de 10 con timeout de 2s
        # Creates the Thread
        t = threading.Thread(target=self.inputThread, args=(SecureUdpOrange,))
        t.start()

        obPackagex = obPackage(14)
        serializedObject = obPackagex.serialize(14)
        SecureUdpOrange.sendto(serializedObject,OtherIP,OtherPort)

    def inputThread(self,SecureUdpOrange):
        while True:
            payload , addr = SecureUdpOrange.recivefrom()
            print(payload,addr)
            obPackagex = obPackage()

            if int.from_bytes(payload[:1], byteorder='big') == 15:
                print("Tipo neighbor without address")
                obPackagex.unserialize(payload,15)
                self.neighborTuple.append((obPackagex.neighborID,"0.0.0.0",-1))
                self.myID = obPackagex.nodeID

            elif int.from_bytes(payload[:1], byteorder='big') == 16:
                print("Tipo neighbor with address")
                obPackagex = obPackage()
                obPackagex.unserialize(payload,16)
                self.neighborTuple.append((obPackagex.neighborID,obPackagex.blueAddressIP,obPackagex.blueAddressPort))
                self.myID = obPackagex.nodeID
                helloPack = obPackage(1)
                serializedHelloPack = helloPack.serialize(1)
                SecureUdpOrange.sendto(serializedHelloPack,obPackagex.blueAddressIP,obPackagex.blueAddressPort)

            elif int.from_bytes(payload[:1], byteorder='big') == 17:
                print("Tipo GraphComplete")
                # Creates the Thread
                t = threading.Thread(target=self.logicalThread, args=())
                t.start()

            elif int.from_bytes(payload[:1], byteorder='big') == 1:
                print("Tipo Hello")
                #self.neighborTuple.append((self.myID,addr[0],addr[1]))


    def logicalThread(self):
        while True:
            print(self.neighborTuple)
            self.packageQueue.get(block=True,timeout=None)





def main():
    if len(sys.argv) == 5:
        blueNode(sys.argv[1],int(sys.argv[2]),sys.argv[3],int(sys.argv[4]))
    else:
        print("Error!! To compile do it like this: python3 blueNode.py MyIP MyPort OtherIP OtherPort")
        exit()

if __name__ == "__main__":
    main()
