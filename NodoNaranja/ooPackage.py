import copy, struct

class ooPackage:

    def __init__(self, packetCategory = -1, sn = 0, orangeSource = -1, orangeTarget = -1, communicationType = '*', requestedGraphPosition = -1, blueAddressIP = '999.999.999.999', blueAddressPort = 0000, priority = 0):
        self.packetCategory = packetCategory
        self.sn = sn
        self.orangeSource = orangeSource
        self.orangeTarget = orangeTarget
        self.communicationType = communicationType
        self.requestedGraphPosition = requestedGraphPosition
        self.blueAddressIP = blueAddressIP
        self.blueAddressPort = blueAddressPort
        self.priority = priority

    def print_data(self):
        print(" packetCategory:",self.packetCategory, " sn: ", self.sn, " orangeSource: ", self.orangeSource, " orangeTarget: ", self.orangeTarget, " communicationType: ", self.communicationType, " requestedGraphPosition: ", self.requestedGraphPosition, " blueAddressIP: ", self.blueAddressIP, "blueAddressPort:", self.blueAddressPort, " priority: ", self.priority)

    #returns a bytes object
    def serialize(self):
        bytePacket = struct.pack('bIbbch15phI',self.packetCategory,self.sn,self.orangeSource,self.orangeTarget,self.communicationType.encode(),self.requestedGraphPosition,self.blueAddressIP.encode(),self.blueAddressPort,self.priority)
        return bytePacket

    def unserialize(self, bytePacket):
        processedPacket = struct.unpack('BIBBcH15pHI',bytePacket)

        self.packetCategory = processedPacket[0]
        self.sn = processedPacket[1]
        self.orangeSource = processedPacket[2]
        self.orangeTarget = processedPacket[3]
        self.communicationType = processedPacket[4].decode("utf-8")
        self.requestedGraphPosition = processedPacket[5]
        self.blueAddressIP = processedPacket[6].decode("utf-8")
        self.blueAddressPort = processedPacket[7]
        self.priority = processedPacket[8]
        return self

#----------------------------------------------------------


def main():
    ooPackagex = ooPackage(2,1,3,9,'r',566,'0.0.0.0',8888,1000)
    ooPackagex.print_data()

    serializedObject = ooPackagex.serialize()

    ooPackage2 = ooPackage()
    ooPackage2.unserialize(serializedObject)
    ooPackage2.print_data()

if __name__ == "__main__":
    main()
