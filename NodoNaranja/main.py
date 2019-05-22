from orangeNode import orangeNode
import sys



if __name__== "__main__":

	if len(sys.argv) == 4:		
		orange = orangeNode(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),"routingTable.txt", "../Grafo_Referencia.csv")
		orange.run()
	else:
		print("Error: need the ip and port of the server and the number of the orangeNode")
		exit()
