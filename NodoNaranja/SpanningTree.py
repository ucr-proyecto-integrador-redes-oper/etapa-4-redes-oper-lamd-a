import SecureUDP
from SecureUDP import SecureUDP

import time

#Falta lo que hace marcial

'''
	Método broadcast a vecinos
    	Envía una solicitud Jointree(nodoID) a sus vecinos
    
    Método que reciba del broadcast
'''

class Message:
  def __init__(self):
    self.ip = 1.1.1.1
    self.port = 8080
    self.payload = []

class SpanningTree:
	'''
    	Efe: Crea una instancia de la clase
        Req: nodo azul raiz 
    	Mod: spanning_tree, agregandole el nodo raiz
    '''
    
    def __init__(self, nodo_raiz_id):
    	self.nodo_raiz_id = nodo_raiz_id
    	self.spanning_tree = []
        self.spanning_tree.append(self.nodo_raiz_id)
        self.aristas = [] #Lleno de pares en donde son (nodo_padre, nodo_hijo)
    
    '''
    	Efe: Crea un mensaje
        Req: ---
    	Mod: ---
    '''
    
    def construct_message(self):
      Message msj      
      return msj
    
    
    '''
    	Efe: Se fija si podemos unir el nodo al spanning tree
        Req: un nodo
    	Mod: las aristas, si es que el nodo se puede agregar al spanning tree
    '''
    
  	def can_add_node_to_sTree(self, node):
    	index_vecino_menor = -1
      	SecureUDP secureUDP
        for index, vecino in enumerate(node.vecinos):
      		
            #Se hace la consulta a todos los vecinos
            msj = self.construct_message()
            respuesta = secureUdp.sendto(msj.payload, msj.id, msj.port)
            
            if respuesta.value == 12: #I do
            	if index_vecino_menor == -1: # Primer vecino
              		index_vecino_menor = index
            	elif vecino.id < node.vecinos[index_vecino_menor]:
              		index_vecino_menor = index
        	elif respuesta.value == 18:
              	time.sleep(2)
                
        if index_vecino_menor != -1: # para meter al spanning tree
            return True
        else:
        	return False
    
    '''
    	Efe:  
        Req: 
    	Mod: 
    '''
    
    def add_to_tree(self, padre, hijo):
    	par = [padre, hijo]
    	self.aristas.append(par)
    	self.spanning_tree.append(hijo)
    
    '''
    	Efe: 
        Req: 
    	Mod: 
    '''
    
  	def create_Spanning_Tree(self, nodo_id):
    	SecureUDP secureUDP
        if (self.can_add_node_to_sTree(nodo_id)):
          #Se crea un paquete con id (ido 12, nodo id)
          
    
    
    
'''
	0-> 1, 4, 5
    1-> 0, 2, 3
    2-> 1, 3, 4
    3-> 2, 5
	4-> 0, 2 
    5-> 0, 3
    
    SpanningTree
    0->
    
    
'''    