import math
from screeninfo import get_monitors
import pygame
import time
import random

from pygame.locals import *
pygame.init()

class Admin_archivos:
	def __init__(self):
		self.file_name = "Grafo_Referencia.csv"
		self.nodos_finales = [] #lista de listas

	"""
		Metodo que se encarga de ver el archivo y parser para crear un nodo
	"""

	def tomar_datos(self):
		file = open(str(self.file_name), "r")
		content = file.readlines()
		nodo_str = ""
		index = 0

		for line in content:
			if line[0:1].isdigit():
				line = line[:-1]
				# print(f"Linea ----> ({line})")
				self.nodos_finales.append([])
				nodo_str = ""
				while len(line) > 0:
					letra = line[0]
					if letra >= '0' and letra <= '9':
						nodo_str += letra
					else:
						# print(f"nodo_str = ({nodo_str})")
						nodo_int = int(nodo_str)
						self.nodos_finales[index].append(nodo_int)
						nodo_str = ""
					line = line[1:]
				# print(f"nodo_str = ({nodo_str})")
				nodo_int = int(nodo_str)
				self.nodos_finales[index].append(nodo_int)
				index += 1

		file.close()

	"""
		Metodo que se encarga de imprimir lo que se saco del archivo como enteros
	"""

	def print_result(self):
		print("Estado del grafo con nodos enteros")
		for nodo_padre in self.nodos_finales:
			print(nodo_padre)


##########################################################
##########################################################

class Pantalla:
	def __init__(self):
		self.alto = 0
		self.ancho = 0

		#Toma los valores del ultimo monitor visto
		for m in get_monitors():
			self.definir_valores(str(m))
		# print(f"alto_pantalla ({self.alto}) ancho_pantalla ({self.ancho})")

	"""
	Metodo que se encarga de parsear los valores en string de 
	las dimensiones de las pantallas
	"""	
	def definir_valores(self, dato):
		valor_str = ""
		for letra in dato:
			
			if letra == 'x':
				self.ancho = int(valor_str)
				valor_str = ""
			elif letra == '+':
				self.alto = int(valor_str)
				valor_str = ""
				break

			if letra >= '0' and letra <= '9':
				valor_str += letra


###################################################################
###################################################################

class Nodo:
	def __init__(self, nombre_nodo, x, y):
		self.diff = 30
		self.x = x
		self.y = y
		self.nombre = nombre_nodo
		self.vecinos = []
		self.centro = (y+15, x+15)
		self.color = "azul"

	"""
	Metodo que me dice si el par (x, y) esta dentro del area delimitada por
	la instancia actual de nodo
	"""

	def dentro_area(self, par):
		result = False
		x_par = par[0]
		y_par = par[1]
		
		x_dentro = x_par > (self.x-10) and x_par < (self.x + self.diff + 10)
		y_dentro = y_par > (self.y-10) and y_par < (self.y + self.diff + 10)
		
		if x_dentro and y_dentro:
			result = True
			
		return result

###################################################################
###################################################################

class Graficador:
	black = (0,0,0) #Color de las aristas

	"""
		Constructor de la clase
	"""

	def __init__(self, pantalla):
		self.alto_pygame = round(pantalla.alto * 0.90)
		self.ancho_pygame = round(pantalla.ancho * 0.90)

		self.max_random_x = self.alto_pygame - 30
		self.max_random_y = self.ancho_pygame - 30

		self.mensaje = ""
		self.game_display = pygame.display.set_mode((self.ancho_pygame, self.alto_pygame))
		pygame.display.set_caption("GRUPO LAMDa")
		self.nodo = pygame.image.load('nodo.jpg')
		self.nodo_r = pygame.image.load('nodo_r.jpg')
		self.pixelito = pygame.image.load('background.jpg')
		self.limpiar_pantalla()

	"""
		Metodo que se encarga de dejar la pantalla en blanco
	"""

	def limpiar_pantalla(self):
		for y in range(self.alto_pygame):
			for x in range(self.ancho_pygame): 		
				self.game_display.blit(self.pixelito, (x, y))

	"""
		Metodo que se encarga de graficar de rojo los nodos que se le 
		envian en la lista_nodos
	"""

	def graficar_nodos_rojos(self, lista_nodos):
		for nodo in lista_nodos:
			self.colocar_imagen(nodo.x, nodo.y, nodo.nombre, True)

	"""
		Metodo que se encarga de graficar de azul todos los nodos que se le 
		envian en la lista_nodos
	"""

	def graficar_nodos_azules(self, lista_nodos):
		for nodo in lista_nodos:
			self.colocar_imagen(nodo.x, nodo.y, nodo.nombre)

	"""
		Metodo encargado de colocar una imagen con el nombre dentro de la misma
		es decir que en el centro
	"""	

	def colocar_imagen(self, x, y, nombre, nodo_rojo = False):
		temp_tuple = (y, x)
		
		if nodo_rojo:
			self.game_display.blit(self.nodo_r, temp_tuple)
		else:
			self.game_display.blit(self.nodo, temp_tuple)

		#Colocando el nombre del nodo
		smallText = pygame.font.Font("freesansbold.ttf", 20)
		textSurf, textRect = self.text_objects(nombre, smallText)
		textRect.center = ((y + (30 / 2)), (x + (30 / 2)))
		self.game_display.blit(textSurf, textRect)

		pygame.display.update()
	
	"""
		Metodo encargado de definir valores de texto para pygame
	"""

	def text_objects(self, text, font):
		textSurface = font.render(text, True, self.black)
		return textSurface, textSurface.get_rect()

	"""
		Metodo que se encarga de colocar una imagen representante del grafo
		Con un click se sale del while que ayuda a fijarse en los eventos
	"""

	def graficar(self):
		pygame.display.update()
		stop = False
		while not stop:
			for event in pygame.event.get():
				click = pygame.mouse.get_pressed()
				if event.type == QUIT:
						pygame.quit()
						quit()
				elif click[0] == 1:
					stop = True
					break

	"""
		Metodo que coloca una arista que va de (x1, y1) a (x2, y2)
	"""

	def colocar_arista(self, x1, y1, x2, y2):
		#surface, color, startPoint, endPoint, aristaWidth
		pygame.draw.line(self.game_display, self.black, (x1,y1), (x2, y2), 3)

###################################################################
###################################################################

class Graph: 
	"""
		Constructor de la clase
	"""

	def __init__(self, source=[], target=[], weight=[], directed=True):
		self.porc_alto = 0.85
		self.porc_ancho = 0.85
		self.diff = 30
		self.aristas = [] 
		self.pantalla = Pantalla() #Para sacar las dimensiones de la pantalla actual
		self.graficador = Graficador(self.pantalla)
		self.lista_nodos_archivos = []
		self.admin_archivo = Admin_archivos()
		self.admin_archivo.tomar_datos()
		self.nodos = []
	
	"""
		Agrega nodos en localizaciones especificas
	"""
	
	def agregar_nodo_esp(self, x, y, nombre_nodo):
		nuevo_nodo = Nodo(nombre_nodo, x, y)
		# print(f"{len(self.nodos)} - Nodo listo en ({x} - {y})")
		self.nodos.append(nuevo_nodo)
		self.graficador.colocar_imagen(nuevo_nodo.x, nuevo_nodo.y, nombre_nodo)

	"""
		Agrega nodos en localizaciones random pero valida
	"""

	def agregar_nodo(self, nombre_nodo):
		diferencia = 40

		x = random.randint(0, round(self.graficador.alto_pygame - diferencia))
		y = random.randint(0, round(self.graficador.ancho_pygame - diferencia))
		
		while not self.analisis_esquinas_validas(x, y):
			x = random.randint(0, round(self.graficador.alto_pygame - diferencia))
			y = random.randint(0, round(self.graficador.ancho_pygame - diferencia))

		self.agregar_nodo_esp(x, y, nombre_nodo)

	"""
		Metodo encargado de ver si un nodo puede caer encima de otro ya creado y graficado
	"""
	
	def analisis_esquinas_validas(self, x, y):
		result = True
		
		esquina_superior_izq = (x, y)
		esquina_superior_der = (x, y + self.diff)
		esquina_inferior_izq = (x + self.diff, y)
		esquina_inferior_der = (x + self.diff, y + self.diff)
		
		for nodo in self.nodos:

			validez_esquina_superior_izq = nodo.dentro_area(esquina_superior_izq)
			validez_esquina_superior_der = nodo.dentro_area(esquina_superior_der)
			validez_esquina_inferior_izq = nodo.dentro_area(esquina_inferior_izq)
			validez_esquina_inferior_der = nodo.dentro_area(esquina_inferior_der)

			# print(f"Analizando ({x}, {y})")
			# print(f"esquina_superior_izq ({esquina_superior_izq}) -> {validez_esquina_superior_izq}")
			# print(f"esquina_superior_der ({esquina_superior_der}) -> {validez_esquina_superior_der}")
			# print(f"esquina_inferior_izq ({esquina_inferior_izq}) -> {validez_esquina_inferior_izq}")
			# print(f"esquina_inferior_der ({esquina_inferior_der}) -> {validez_esquina_inferior_der}")

			if validez_esquina_superior_izq or validez_esquina_superior_der or validez_esquina_inferior_izq or validez_esquina_inferior_der:
				result = False
				break
		return result

	"""
		Metodo que imprime la informacion de cada uno de los nodos
	"""

	def print_info_grafo(self):
		for nodo in self.nodos:
			print("Nodo: ", nodo.nombre)
			if len(nodo.vecinos) == 0:
				print("No tiene vecinos")
			else:
				print("Sus vecinos corresponden a:")
			for nombre_vecino in nodo.vecinos:
				print(f"{nombre_vecino}")
			print("-----------------------------------------")


	"""
		Metodo que se encarga de agregar al n1 como vecino del n2 y vicersa
		Tambien grafica una arista entre los nodos
	"""

	def agregar_arista(self, n1, n2):
		contador = 0
		for nodito in self.nodos:
			if nodito.nombre == n2.nombre:
				nodito.vecinos.append(n1.nombre)
				contador += 1
			if nodito.nombre == n1.nombre:
				nodito.vecinos.append(n2.nombre)
				contador += 1
			if contador == 2:
				self.graficador.colocar_arista(n1.y+15, n1.x+15, n2.y+15, n2.x+15)
				self.graficador.colocar_imagen(n1.x, n1.y, n1.nombre)
				self.graficador.colocar_imagen(n2.x, n2.y, n2.nombre)
				pygame.display.update()
				break

	"""
		Metodo encargado de colorear los nodos que se le mandan en la lista como rojos
	"""

	def mostrar_nodos_con_chunks(self, lista_nodos):
		lista_nodos_temp = []

		for num_nodo in lista_nodos:
			for nodo in self.nodos:
				if str(num_nodo) == nodo.nombre:
					lista_nodos_temp.append(nodo)
					break

		# print("Nodos con paquetes")
		# for nodito in lista_nodos_temp:
		# 	print(f"nodo -> {nodito.nombre}")

		self.graficador.graficar_nodos_rojos(lista_nodos_temp)

	"""
		Metodo que se encarga de dejar todos los nodos rojos que hay como azules
	"""

	def convertir_nodos_a_azules(self):
		self.graficador.graficar_nodos_azules(self.lista_nodos_archivos)
		self.lista_nodos_archivos.clear()

	"""
		Metodo que se encarga de usar el arreglo de nodos para crear el grafo a partir del archivo
	"""

	def crear_grafo(self):
		for lista_nodos in self.admin_archivo.nodos_finales:
			padre = str(lista_nodos[0])
			self.agregar_nodo(padre)
			
		for vecinos in self.admin_archivo.nodos_finales:
			papa = -1
			for index, vecino in enumerate(vecinos):
				if index != 0:	
					# print(f"    vecino: ({vecino})")
					self.agregar_arista(self.nodos[papa - 1], self.nodos[vecino - 1])
				else:
					papa = vecino
					# print(f"Papa = ({papa})")

	"""
		Metodo que me refresca la pantalla
	"""

	def refresh(self):
		self.graficador.limpiar_pantalla()
		self.nodos = []
		self.crear_grafo()
		self.graficador.graficar()



###################################################################
###################################################################

# def main ():
# 	grafo = Graph()
# 	list_temp = []

# 	for iteracion in range(10):
		
# 		list_temp.clear()
# 		for nodo in range(10):
# 			nodo_rojo = random.randint(0, 50)
# 			list_temp.append(nodo_rojo)

# 		for nodo in range(50):
# 			grafo.agregar_nodo(str(nodo))

# 		# grafo.graficador.colocar_arista(0,0, 100, 100)
		
# 		#Creando aristas random
# 		for arista in range(10):
# 			n1 = random.randint(0, len(grafo.nodos)-1)
# 			n2 = random.randint(0, len(grafo.nodos)-1)

# 			while n1 == n2:
# 				n1 = random.randint(0, len(grafo.nodos)-1)
# 				n2 = random.randint(0, len(grafo.nodos)-1)
			
# 			#Ahora se hace la arista
# 			nodo_a = grafo.nodos[n1]
# 			nodo_b = grafo.nodos[n2]

# 			# print(f"Arista {arista} de {nodo_a.nombre} -> {nodo_b.nombre}")
# 			grafo.agregar_arista(nodo_a, nodo_b)


# 		grafo.graficar_nodos_con_archivos(list_temp)
# 		time.sleep(2)
# 		grafo.convertir_nodos_a_azules()
# 		# grafo.print_info_grafo()
# 		grafo.graficador.graficar()
		
# 		grafo.graficador.limpiar_pantalla()
# 		del grafo.nodos[:]
# 		print(f"iteracion {iteracion}")

	

# 	# grafo.agregar_nodo_esp(0, 0, "0")
# 	# grafo.agregar_nodo_esp(0, 100, "1")
# 	# grafo.agregar_nodo_esp(100, 0, "2")
# 	# grafo.agregar_nodo_esp(100, 100, "3")
# 	# grafo.graficador.graficar()
	
	
# def main2():
# 	admin_archivo = Admin_archivos()
# 	admin_archivo.tomar_datos()
# 	admin_archivo.print_result()

def main3():

	list_temp = []

	for nodo in range(10):
		nodo_rojo = random.randint(1, 15)
		list_temp.append(nodo_rojo)

	print(f"list_temp = ({list_temp})")
	
	grafo = Graph()
	grafo.crear_grafo()
	grafo.graficador.graficar()
	while True:
		grafo.refresh()
		grafo.mostrar_nodos_con_chunks(list_temp)
		grafo.graficador.graficar()
		

if __name__ == "__main__":
	# main()
	# main2()
	main3()