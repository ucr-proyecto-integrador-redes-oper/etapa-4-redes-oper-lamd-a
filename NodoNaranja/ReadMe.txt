To install pygame and see the graph you need to open a terminal and run:
	sudo apt update
	sudo apt install python3-pip
	pip3 --version
	python3 -m pip install -U pygame --user
	python3 -m pygame.examples.aliens #If aliens game work you already have pygame installed

	python3 Grafo.py

To compile OrangeNode.py:
	pyhton3 orangeNode.py MyPORT MyOrangeNodeID
Example:
	pyhton3 orangeNode.py 8765 1

The program generates 3 files input.out, output.out and logicalThread.out. For debuging 

To compile blueNode.py:
	pyhton3 blueNode.py OrangeIP OrangeBluePort
Example:
	pyhton3 blueNode.py 10.1.137.34 9012

To generate multiple blueNodes:
	./blueNodeGeneratorScript.h OrangeIP OrangeBluePort
Example:
	./blueNodeGeneratorScript.h 10.2.137.32 9012

To compile greenNode.py:
	pyhton3 greenNode.py myGroupID MyID BlueIP BluePort
Example:
	pyhton3 greenNode.py 1 0 0.0.0.0 9675