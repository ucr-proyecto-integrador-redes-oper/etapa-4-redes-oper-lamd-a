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
    packageQueue = queue.Queue() # Tuple with

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
            self.packageQueue.put((payload,addr))




    def logicalThread(self):
        while True:
            package = self.packageQueue.get(block=True,timeout=None)
            bytePackage = package(0)
            Type = int.from_bytes(bytePackage[:1], byteorder='big')
            if Type == 0:
                print("Tipo put chunk")
            elif Type == 1:
                print("Tipo hello")
            elif Type == 1:
                print(Tipo hello)
            elif Type == 1:
                print(Tipo hello)
            elif Type == 1:
                print(Tipo hello)
            elif Type == 1:
                print(Tipo hello)
            elif Type == 1:
                print(Tipo hello)
            elif Type == 1:
                print(Tipo hello)
            elif Type == 15:
                print("Tipo neighbor without address")
                obPackagex.unserialize(payload,15)
                self.neighborTuple.append((obPackagex.neighborID,"0.0.0.0",-1))
                self.myID = obPackagex.nodeID
            elif Type == 16:
                print("Tipo neighbor with address")
                obPackagex = obPackage()
                obPackagex.unserialize(payload,16)
                self.neighborTuple.append((obPackagex.neighborID,obPackagex.blueAddressIP,obPackagex.blueAddressPort))
                self.myID = obPackagex.nodeID
                helloPack = obPackage(1)
                serializedHelloPack = helloPack.serialize(1)
                SecureUdpOrange.sendto(serializedHelloPack,obPackagex.blueAddressIP,obPackagex.blueAddressPort)

            elif Type == 17:
                print("Tipo GraphComplete")
                # Creates the Thread
                t = threading.Thread(target=self.logicalThread, args=())
                t.start()





def main():
    if len(sys.argv) == 5:
        blueNode(sys.argv[1],int(sys.argv[2]),sys.argv[3],int(sys.argv[4]))
    else:
        print("Error!! To compile do it like this: python3 blueNode.py MyIP MyPort OtherIP OtherPort")
        exit()

if __name__ == "__main__":
    main()
