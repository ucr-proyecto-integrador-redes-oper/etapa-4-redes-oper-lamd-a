from orangeNode import orangeNode


if __name__== "__main__":

	orange = orangeNode('0.0.0.0',8888,2,"routingTable.txt", "../Grafo_Referencia.csv")
	orange.run()
