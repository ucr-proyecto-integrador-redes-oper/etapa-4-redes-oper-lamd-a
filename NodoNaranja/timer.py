import time

class Timer(object):
	stop = -1
	'''
	  EFE: Constrye la clase Timer con begining y duration
	  REQ: ---
	  MOD: ---
	'''   
	
	def __init__(self, duration):
		self.start = self.stop
		self.duration = duration

	'''
	  EFE: Comienza el timer
	  REQ: ---
	  MOD: ---
	'''  
	def Start(self):
		if self.start == self.stop:
			self.start = time.time()

	'''
	  EFE: Detiene el timer
	  REQ: ---
	  MOD: ---
	'''  
	def Stop(self):
		if self.start != self.stop:
			self.start = self.stop

	'''
	  EFE: Retorna true si el timer ha finalizado
	  REQ: ---
	  MOD: ---
	'''  
	def running(self):
		return self.start != self.stop

	'''
	  EFE: Detiene el timer
	  REQ: Haya un timer activo
	  MOD: ---
	'''  
	def timeout(self):
		if not self.running():
			return False
		else:
			return time.time() - self.start >= self.duration