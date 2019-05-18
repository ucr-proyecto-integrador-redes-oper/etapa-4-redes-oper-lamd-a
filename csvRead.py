import csv
 

class nodeTable():

    #Store the nodes
    Graph = []
    
    
    with open('Grafo_Referencia.csv', newline='') as File:  
        reader = csv.reader(File)
        for row in reader:
            #print(row) Test
            Graph.append(row)



    def 
    '''
        print("-------------------------------------")

        print(Graph)

        print("-------------------------------------")

        print(Graph[1][0])
    '''






'''
results = []
with open('Grafo_Referencia.csv') as File:
    reader = csv.DictReader(File)
    for row in reader:
        results.append(row)
print (results)
'''