import copy

class Header:

    """
        SN - int 
        sourceNode - int
        destNode - int
        type - char
        rNode - int
        address - something
        priority - int
    """
    def __init__(self, orig=None):
        if(orig is None):
            self.non_copy_constructor()
        else:
            self.copy_constructor(orig)
            

    def non_copy_constructor(self):
        self.sn = -1
        self.sourceNode = -1
        self.destinationNode = -1
        self.type = '*'
        self.requestedNode = -1
        self.address = "*"
        self.priority = -1

    def copy_constructor(self, orig):
        self.sn = orig.sn
        self.sourceNode = orig.sourceNode
        self.destinationNode = orig.destinationNode
        self.type = orig.type
        self.requestedNode = orig.requestedNode
        self.address = orig.address
        self.priority = orig.priority

    def setAll(self, sn, sourceNode, destinationNode, type_n, requestedNode, address, priority):
        self.sn = sn
        self.sourceNode = sourceNode
        self.destinationNode = destinationNode
        self.type = type_n
        self.requestedNode = requestedNode
        self.address = address
        self.priority = priority

    def setSN(self, sn):
        self.sn = sn

    def getSN(self):
        return self.sn

    def getSourceNode(self):
        return self.sourceNode

    def setSourceNode(self, sourceNode):
        self.sourceNode = sourceNode

    def getDestinationNode(self):
        return self.destinationNode

    def setDestinationNode(self, destinationNode):
        self.destinationNode = destinationNode

    def getType(self):
        return self.type

    def setType(self, type):
        self.type = type

    def getRequestedNode(self):
        return self.requestedNode

    def setRequestedNode(self, requestedNode):
        self.requestedNode = requestedNode

    def setAddress(self, addr):
        self.address = addr

    def getAddress(self):
        return self.address

    def setPriority(self, prty):
        self.priority = prty

    def getPriority(self):
        return self.priority

    def print_data(self):
        print("sn: ", self.sn, " sourceNode: ", self.sourceNode, " destinationNode: ", self.destinationNode, " type: ", self.type, " requestedNode: ", self.requestedNode, " address: ", self.address, " priority: ", self.priority)


#----------------------------------------------------------


def main():
    header = Header()
    header.print_data()

    header2 = Header(header)
    header2.print_data()


if __name__ == "__main__":
    main()