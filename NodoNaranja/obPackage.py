import copy, struct, pickle

class obPackage:

    def __init__(self, packetCategory = -1, sn = 0, communicationType = '*', obtainedGraphPosition = -1, blueAddressIP = '999.999.999.999', blueAddressPort = 0000, neighborList = []):
        self.packetCategory = packetCategory
        self.sn = sn
        self.communicationType = communicationType
        self.obtainedGraphPosition = obtainedGraphPosition
        self.blueAddressIP = blueAddressIP
        self.blueAddressPort = blueAddressPort
        self.neighborList = neighborList

    def print_data(self):
        print(" packetCategory:",self.packetCategory, " sn: ", self.sn, " communicationType: ", self.communicationType, " obtainedGraphPosition: ", self.obtainedGraphPosition, " blueAddressIP: ", self.blueAddressIP, "blueAddressPort:", self.blueAddressPort, " neighborList: ", self.neighborList)

    #returns a bytes object
    def serialize(self):
        bytePacket = struct.pack('bIch15ph',self.packetCategory,self.sn,self.communicationType.encode(),self.obtainedGraphPosition,self.blueAddressIP.encode(),self.blueAddressPort)

        bytePacket += pickle.dumps(self.neighborList)
        return bytePacket
    def unserialize(self, bytePacket):
        processedPacket = struct.unpack('bIch15ph',bytePacket[:30])

        self.packetCategory = processedPacket[0]
        self.sn = processedPacket[1]
        self.communicationType = processedPacket[2].decode("utf-8")
        self.obtainedGraphPosition = processedPacket[3]
        self.blueAddressIP = processedPacket[4].decode("utf-8")
        self.blueAddressPort = processedPacket[5]
        self.neighborList = list(pickle.loads(bytePacket[30:]))

#----------------------------------------------------------


def main():

    graphPostion1 = 4
    host1 = '10.1.135.25'
    port1 = 54444
    graphPostion2 = 27
    host2 = '187.127.511.623'
    port2 = 5477
    graphPostion3 = 400
    host3 = '127.0.0.1'
    port3 = 65444

    neighborList = [(graphPostion1,host1,port1),(graphPostion2,host2,port2),(graphPostion3,host3,port3)]
    obPackagex = obPackage(0,1,'r',566,'10.1.127.37',8888,neighborList)
    obPackagex.print_data()

    serializedObject = obPackagex.serialize()

    obPackage2 = obPackage()
    obPackage2.unserialize(serializedObject)
    obPackage2.print_data()

    #the code below can be used to extract only the ip and port from a serializedPacket to send it (by the output thread of the orange node)

    print(struct.calcsize('bIch15ph'))

    result = struct.unpack('15ph',serializedObject[12:30])

    print(result)

if __name__ == "__main__":
    main()
