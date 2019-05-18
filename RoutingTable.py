import configparser

class RoutingTable:
    def __init__(self, file):
        self.table = [] #["a", "1.1.1.1", 8888, .......]
        self.constructTable(file)

    #Metodo que se encarga del paseo del file para crear la tabla de enrutamiento
    def constructTable(self, file):
        config.read()
