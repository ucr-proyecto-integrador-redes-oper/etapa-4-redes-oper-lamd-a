# from tkinter.filedialog import askopenfilename
# filename = askopenfilename()
# print(filename)

from tkinter import filedialog
from tkinter import *
import tkinter
from SecureUDP import SecureUdp
from obPackage import obPackage
import os
import math
from tkinter import messagebox
import PIL 
import PIL.Image
import PIL.ImageTk
#import pygame
#import wave
import playsound
from Grafo import Graph


rowIndex = 1
filesList = [] #Tuple (filename, FileID)
SecureUDP = SecureUDP = SecureUdp(10,4,True)

filename = "hola.png"


def putFileLogic(fatherWindow,entry1,entry2):
	global rowIndex
	global filesList
	global filename
	fatherWindow.grab_set()
	rowIndex +=1
	print("Name ",filename)

	ip = SecureUDP.sock.getsockname()[0]
	port = int(entry2.get())

	newFilePack = obPackage(20)
	newFilePack.fileName = filename
	byteNewFilePack = newFilePack.serialize(20)
	SecureUDP.sendto(byteNewFilePack,ip,int(port))
	bytePackage , addr = SecureUDP.recivefrom()

	FileAdrrPack = obPackage()
	FileAdrrPack.unserialize(bytePackage,2)
	fileID = ( FileAdrrPack.fileIDByte1 , FileAdrrPack.fileIDRest)
	filesList.append((filename,fileID))

	lbl1 = Label(master=fatherWindow,text="File Successfully transferred your key: ", font=("Helvetica", 14))
	lbl1.place(relx = 0.10, rely = 0.50)
	lbl1 = Label(master=fatherWindow,text=fileID, font=("Helvetica", 14))
	lbl1.place(relx = 0.55, rely = 0.50)

	print(filename,str(rowIndex))
	fatherWindow.grab_release()
	
def addNewFile(fatherWindow):
	global filename
	fatherWindow.grab_set()
	filename = filedialog.askopenfilename()
	lbl1 = Label(master=fatherWindow,text=filename)
	lbl1.grid(row=0, column=1)
	fatherWindow.grab_release()


def putFile(fatherWindow):
	global filename
	fatherWindow.withdraw()
	slave = Tk()
	slave.title("Put")
	slave.geometry("700x200")

	filename = filedialog.askopenfilename()
	
	lbl1 = Label(master=slave,text="File: ", font=("Helvetica", 14)) #master, text="Diseño de Software", width=20, fg="white",bg="#000000", font=("Helvetica", 24, 'bold')
	lbl1.grid(row=0, column=0)

	lbl1 = Label(master=slave,text=filename, font=("Helvetica", 12))
	lbl1.grid(row=0, column=1)

	lbl1 = Label(master=slave,text="Insert IP: ", font=("Helvetica", 14))
	lbl1.grid(row=1, column=0)
	entry1 = Label(master=slave,text=SecureUDP.sock.getsockname()[0],  font=("Helvetica", 14))
	entry1.grid(row=1,column=1)

	lbl2 = Label(master=slave,text="Insert Port: ", font=("Helvetica", 14))
	lbl2.grid(row=2, column=0)
	entry2 = Entry(slave)
	entry2.grid(row=2,column=1)

	button1 = Button(slave,text="Done", bd = 3, width=10, font = ("Helvetica", 14), command=lambda: putFileLogic(slave,entry1,entry2))
	#button1.grid(row=3,column=0) button2.place(relx = 0.01, rely =  0.40)
	button1.place(relx = 0.10, rely = 0.75)

	button1 = Button(slave,text="Back", bd = 3, width=10, font = ("Helvetica", 14), command=lambda: goBack(slave,fatherWindow))
	#button1.grid(row=3,column=1)
	button1.place(relx = 0.35, rely = 0.75)

	addFileButton = Button(slave,text="NewFile", bd = 3, width=7, font = ("Helvetica", 14), command=lambda: addNewFile(slave))
	#addFileButton.grid(row=3,column=2)
	addFileButton.place(relx = 0.60, rely = 0.75)


def goBack(myWindow,fatherWindow):
	fatherWindow.deiconify()
	myWindow.destroy()

#-------------------------------Exist-----------------------------------------------
def SendExist(window,ip,port,fileIDByte1,fileIDRest):
	window.grab_set()
	existsPack = obPackage(2) #Tipo 2
	existsPack.fileIDByte1 = int(fileIDByte1.get())
	existsPack.fileIDRest = int(fileIDRest.get())

	clear = Label(master=window,text="                                               ", font = ("Helvetica", 14))
	clear.place(relx = 0.10, rely = 0.55)

	label1 = Label(master=window,text="Looking for the file", font=("Helvetica", 14))
	label1.place(relx = 0.10, rely = 0.55)

	greenIP = ip.get()
	greenPort = int(port.get())
	byteExistPack = existsPack.serialize(2)
	SecureUDP.sendto(byteExistPack,greenIP,greenPort)

	bytePackage , addr = SecureUDP.recivefrom()
	responsePack = obPackage(3)

	clear = Label(master=window,text="                                               ", font = ("Helvetica", 14))
	clear.place(relx = 0.10, rely = 0.55)
	
	responsePack.unserialize(bytePackage,3)
	if responsePack.fileIDByte1 == 0:
		label1 = Label(master=window,text="FILE NOT found!!!!", font=("Helvetica", 14))
		label1.place(relx = 0.10, rely = 0.55)
	else:
		label1 = Label(master=window,text="FILE FOUND!!!!", font=("Helvetica", 14))
		label1.place(relx = 0.10, rely = 0.55)
	window.grab_release()

def exits(window):
	window.withdraw()
	slave = Tk()
	slave.title("Exist")
	slave.geometry("500x200")

	
	lbl1 = Label(master=slave,text="Insert IP: ", font=("Helvetica", 14))
	lbl1.grid(row=0, column=0)
	entry1 = Entry(slave)
	entry1.grid(row=0,column=1)

	lbl2 = Label(master=slave,text="Insert Port: ", font=("Helvetica", 14))
	lbl2.grid(row=1, column=0)
	entry2 = Entry(slave)
	entry2.grid(row=1,column=1)

	lbl3 = Label(master=slave,text="First Number File ID: ", font=("Helvetica", 14))
	lbl3.grid(row=2, column=0)
	entry3 = Entry(slave)
	entry3.grid(row=2,column=1)

	lbl4 = Label(master=slave,text="Second Number File ID: ", font=("Helvetica", 14))
	lbl4.grid(row=3, column=0)
	entry4 = Entry(slave)
	entry4.grid(row=3,column=1)

	button1 = Button(slave,text="Done", bd = 3, width=10, font = ("Helvetica", 14), command=lambda: SendExist(slave,entry1,entry2,entry3,entry4))
	#button1.grid(row=4,column=0)
	button1.place(relx = 0.10, rely = 0.75)

	button1 = Button(slave,text="Back", bd = 3, width=10, font = ("Helvetica", 14), command=lambda: goBack(slave,window))
	#button1.grid(row=5,column=0)
	button1.place(relx = 0.40, rely = 0.75)
#-------------------------------Exist-----------------------------------------------

#-------------------------------Delete-----------------------------------------------
def SendDelete(window,ip,port,fileIDByte1,fileIDRest):
	window.withdraw()
	deletePack = obPackage(10) #Tipo 10
	deletePack.fileIDByte1 = int(fileIDByte1.get())
	deletePack.fileIDRest = int(fileIDRest.get())

	greenIP = ip.get()
	greenPort = int(port.get())
	byteDeletePack = deletePack.serialize(10)
	SecureUDP.sendto(byteDeletePack,greenIP,greenPort)

	label1 = Label(master=window,text="FILE DELETED!!!!", font=("Helvetica", 14))
	label1.place(relx = 0.10, rely = 0.55)

	window.deiconify()

def delete(window):
	window.withdraw()
	slave = Tk()
	slave.title("Delete")
	slave.geometry("400x200")
	
	lbl1 = Label(master=slave,text="Insert IP: ", font=("Helvetica", 14))
	lbl1.grid(row=0, column=0)
	entry1 = Entry(slave)
	entry1.grid(row=0,column=1)

	lbl2 = Label(master=slave,text="Insert Port: ", font=("Helvetica", 14))
	lbl2.grid(row=1, column=0)
	entry2 = Entry(slave)
	entry2.grid(row=1,column=1)

	lbl3 = Label(master=slave,text="First Number File ID: ", font=("Helvetica", 14))
	lbl3.grid(row=2, column=0)
	entry3 = Entry(slave)
	entry3.grid(row=2,column=1)

	lbl4 = Label(master=slave,text="Second Number File ID: ", font=("Helvetica", 14))
	lbl4.grid(row=3, column=0)
	entry4 = Entry(slave)
	entry4.grid(row=3,column=1)

	button1 = Button(slave,text="Done", bd = 3, width=10, font = ("Helvetica", 14), command=lambda: SendDelete(slave,entry1,entry2,entry3,entry4))
	button1.place(relx = 0.10, rely = 0.75)

	button1 = Button(slave,text="Back", bd = 3, width=10, font = ("Helvetica", 14), command=lambda: goBack(slave,window))
	button1.place(relx = 0.40, rely = 0.75)
#-------------------------------Delete-----------------------------------------------

#-------------------------------Complete-----------------------------------------------
def complete(window):
	window.withdraw()
	slave = Tk()
	slave.title("Complete")
	slave.geometry("500x200")
	
	lbl1 = Label(master=slave,text="Insert IP: ", font=("Helvetica", 14))
	lbl1.grid(row=0, column=0)
	entry1 = Entry(slave)
	entry1.grid(row=0,column=1)

	lbl2 = Label(master=slave,text="Insert Port: ", font=("Helvetica", 14))
	lbl2.grid(row=1, column=0)
	entry2 = Entry(slave)
	entry2.grid(row=1,column=1)

	lbl3 = Label(master=slave,text="First Number File ID: ", font=("Helvetica", 14))
	lbl3.grid(row=2, column=0)
	entry3 = Entry(slave)
	entry3.grid(row=2,column=1)

	lbl4 = Label(master=slave,text="Second Number File ID: ", font=("Helvetica", 14))
	lbl4.grid(row=3, column=0)
	entry4 = Entry(slave)
	entry4.grid(row=3,column=1)

	button1 = Button(slave,text="Done", bd = 3, width=10, font = ("Helvetica", 14), command=lambda: sendComplete(slave,entry1,entry2,entry3,entry4))
	button1.place(relx = 0.10, rely = 0.75)

	button1 = Button(slave,text="Back", bd = 3, width=10, font = ("Helvetica", 14), command=lambda: goBack(slave,window))
	button1.place(relx = 0.40, rely = 0.75)

def sendComplete(window,ip,port,fileIDByte1,fileIDRest):
	window.grab_set()
	completePack = obPackage(4) #Tipe 4
	completePack.fileIDByte1 = int(fileIDByte1.get())
	completePack.fileIDRest = int(fileIDRest.get())

	clear = Label(master=window,text="                                               ", font = ("Helvetica", 14))
	clear.place(relx = 0.10, rely = 0.55)

	label1 = Label(master=window,text="Looking for the file", font=("Helvetica", 14))
	label1.place(relx = 0.10, rely = 0.55)

	greenIP = ip.get()
	greenPort = int(port.get())
	byteCompletePack = completePack.serialize(4)
	SecureUDP.sendto(byteCompletePack,greenIP,greenPort)

	bytePackage , addr = SecureUDP.recivefrom()
	responsePack = obPackage(5)

	clear = Label(master=window,text="                                               ", font = ("Helvetica", 14))
	clear.place(relx = 0.10, rely = 0.55)
	
	responsePack.unserialize(bytePackage,5)
	if responsePack.chunkID == 0:
		label1 = Label(master=window,text="FILE NOT COMPLETE!!!!", font=("Helvetica", 14))
		label1.place(relx = 0.10, rely = 0.55)
	else:
		label1 = Label(master=window,text="FILE COMPLETE!!!!", font=("Helvetica", 14))
		label1.place(relx = 0.10, rely = 0.55)
	window.grab_release()
#-------------------------------Complete-----------------------------------------------

#-------------------------------Locate-----------------------------------------------
def locate(window):
	window.withdraw()
	slave = Tk()
	slave.title("Locate")
	slave.geometry("500x200")
	
	lbl1 = Label(master=slave,text="Insert IP: ", font=("Helvetica", 14))
	lbl1.grid(row=0, column=0)
	entry1 = Entry(slave)
	entry1.grid(row=0,column=1)

	lbl2 = Label(master=slave,text="Insert Port: ", font=("Helvetica", 14))
	lbl2.grid(row=1, column=0)
	entry2 = Entry(slave)
	entry2.grid(row=1,column=1)

	lbl3 = Label(master=slave,text="First Number File ID: ", font=("Helvetica", 14))
	lbl3.grid(row=2, column=0)
	entry3 = Entry(slave)
	entry3.grid(row=2,column=1)

	lbl4 = Label(master=slave,text="Second Number File ID: ", font=("Helvetica", 14))
	lbl4.grid(row=3, column=0)
	entry4 = Entry(slave)
	entry4.grid(row=3,column=1)

	button1 = Button(slave,text="Done", bd = 3, width=10, font = ("Helvetica", 14), command=lambda: sendLocate(slave,entry1,entry2,entry3,entry4))
	button1.place(relx = 0.10, rely = 0.75)

	button1 = Button(slave,text="Back", bd = 3, width=10, font = ("Helvetica", 14), command=lambda: goBack(slave,window))
	button1.place(relx = 0.40, rely = 0.75)

def sendLocate(window,ip,port,fileIDByte1,fileIDRest):
	window.grab_set()
	locatePack = obPackage(8) #Tipe 8
	locatePack.fileIDByte1 = int(fileIDByte1.get())
	locatePack.fileIDRest = int(fileIDRest.get())

	clear = Label(master=window,text="                                               ", font = ("Helvetica", 14))
	clear.place(relx = 0.10, rely = 0.55)

	label1 = Label(master=window,text="Looking for the file", font=("Helvetica", 14))
	label1.place(relx = 0.10, rely = 0.55)

	greenIP = ip.get()
	greenPort = int(port.get())
	byteLocatePack = locatePack.serialize(8)
	SecureUDP.sendto(byteLocatePack,greenIP,greenPort)

	bytePackage , addr = SecureUDP.recivefrom()
	responsePack = obPackage(20)

	clear = Label(master=window,text="                                               ", font = ("Helvetica", 14))
	clear.place(relx = 0.10, rely = 0.55)
	
	responsePack.unserialize(bytePackage,20)
	if len(responsePack.fileName) == 0:
		label1 = Label(master=window,text="FILE CAN NOT BE LOCATE!!!!", font=("Helvetica", 14))
		label1.place(relx = 0.10, rely = 0.55)
	else:
		label1 = Label(master=window,text="FILE LOCATED!!!!", font=("Helvetica", 14))
		print(responsePack.fileName)
		lista = responsePack.fileName.split(sep=';')
		for num in range (len(lista)):
			temp = lista[num]
			lista[num] = int(temp)
		
		grafo = Graph()
		grafo.crear_grafo()
		grafo.mostrar_nodos_con_chunks(lista)

		label1.place(relx = 0.10, rely = 0.50)
	window.grab_release()

#-------------------------------Locate-----------------------------------------------

#-------------------------------GET-----------------------------------------------
def get(window):
	window.withdraw()
	slave = Tk()
	slave.title("Get")
	slave.geometry("500x200")
	
	lbl1 = Label(master=slave,text="Insert IP: ", font=("Helvetica", 14))
	lbl1.grid(row=0, column=0)
	entry1 = Entry(slave)
	entry1.grid(row=0,column=1)

	lbl2 = Label(master=slave,text="Insert Port: ", font=("Helvetica", 14))
	lbl2.grid(row=1, column=0)
	entry2 = Entry(slave)
	entry2.grid(row=1,column=1)

	lbl3 = Label(master=slave,text="First Number File ID: ", font=("Helvetica", 14))
	lbl3.grid(row=2, column=0)
	entry3 = Entry(slave)
	entry3.grid(row=2,column=1)

	lbl4 = Label(master=slave,text="Second Number File ID: ", font=("Helvetica", 14))
	lbl4.grid(row=3, column=0)
	entry4 = Entry(slave)
	entry4.grid(row=3,column=1)

	lbl5 = Label(master=slave,text="Filename: ", font=("Helvetica", 14))
	lbl5.grid(row=4, column=0)
	entry5 = Entry(slave)
	entry5.grid(row=4,column=1)

	button1 = Button(slave,text="Done", bd = 3, width=10, font = ("Helvetica", 14), command=lambda: sendGet(slave,entry1,entry2,entry3,entry4,entry5))
	button1.place(relx = 0.10, rely = 0.75)

	button1 = Button(slave,text="Back", bd = 3, width=10, font = ("Helvetica", 14), command=lambda: goBack(slave,window))
	button1.place(relx = 0.40, rely = 0.75)

def sendGet(window,ip,port,fileIDByte1,fileIDRest,filename):
	window.grab_set()


	clear = Label(master=window,text="                                               ", font = ("Helvetica", 14))
	clear.place(relx = 0.10, rely = 0.55)

	label1 = Label(master=window,text="Looking for the file", font=("Helvetica", 14))
	label1.place(relx = 0.10, rely = 0.55)

	greenIP = ip.get()
	greenPort = int(port.get())
	getPack = obPackage(21)

	getPack.fileIDByte1 = int(fileIDByte1.get())
	getPack.fileIDRest = int(fileIDRest.get())
	getPack.fileName = filename.get()

	byteGetPack = getPack.serialize(21)
	SecureUDP.sendto(byteGetPack,greenIP,greenPort)

	bytePackage , addr = SecureUDP.recivefrom()
	responsePack = obPackage(21)

	clear = Label(master=window,text="                                               ", font = ("Helvetica", 14))
	clear.place(relx = 0.10, rely = 0.55)
	
	responsePack.unserialize(bytePackage,21)
	if responsePack.fileIDByte1 == 0:
		label1 = Label(master=window,text="UNABLE TO RETRIEVE FILE!!!!", font=("Helvetica", 14))
		label1.place(relx = 0.10, rely = 0.55)
	else:
		label1 = Label(master=window,text="FILE RETRIEVED!!!!", font=("Helvetica", 14))
		label1.place(relx = 0.10, rely = 0.55)

		lbl1 = Label(master=window,text=responsePack.fileName)
		lbl1.place(relx = 0.10, rely = 0.55)

	window.grab_release()

#-------------------------------GET-----------------------------------------------

def fileList():
	global  filesList
	fileListWindow = Tk()
	fileListWindow.title("List of files")
	for x in range(len(filesList)):
		lbl2 = Label(master=fileListWindow,text=filesList[x])
		lbl2.grid(row=x, column=0)

def play():
	playsound.playsound("/home/akka/Downloads/jugo.mp3")


def showGraph():
	grafo = Graph()
	grafo.crear_grafo()
	grafo.graficador.graficar()
	print("Salimos de show graph()")


root = Tk()

root.title("Green Node")
root.geometry("500x300")


im2 = PIL.Image.open('images/back.jpg') # buscar otra imagen
icon = PIL.ImageTk.PhotoImage(im2)
icon.image = icon 

label = Label(root, image = icon)
label.pack()

group = Label(root, text="LAMDa", fg="black", font=("Helvetica", 24, 'bold'))
group.place(relx=0.45, rely=0.06)

button = Button(text="SeeFiles", bd = 3, font = ("Helvetica", 16),command=fileList)
#button.grid(row=0, column=0) # Lo pone en una pos
button.place(relx = 0.01, rely =  0.05)

button1 = Button(text="Exist",fg="green", bd = 3, width=10, font = ("Helvetica", 16), command=lambda: exits(root))
#button1.grid(row=1, column=0)
button1.place(relx = 0.33, rely =  0.70)

button2 = Button(text="Put", fg="green", bd = 3,  width=10, font = ("Helvetica", 16),command=lambda: putFile(root))
#button2.grid(row=5,column=0)
button2.place(relx = 0.01, rely =  0.40)

button3 = Button(text="Delete", fg="green", bd = 3, width=10, font = ("Helvetica", 16),command=lambda: delete(root))
#button3.grid(row=5, column=1)
button3.place(relx = 0.01, rely =  0.70)

button4 = Button(text="Complete", fg="green", bd = 3, width=10, font = ("Helvetica", 16),command=lambda: complete(root))
button4.place(relx = 0.01, rely =  0.55)

button5 = Button(text="Get", fg="green", bd = 3, width=10, font = ("Helvetica", 16),command=lambda: get(root))
button5.place(relx = 0.33, rely =  0.40)

button6 = Button(text="Locate", fg="green", bd = 3, width=10, font = ("Helvetica", 16),command=lambda: locate(root))
button6.place(relx = 0.33, rely =  0.55)

#button6 = Button(text="NEPE2", fg="green", bd = 3, width=10, font = ("Helvetica", 16),command=lambda: delete(root))
#button6.place(relx = 0.33, rely =  0.70)

button7 = Button(text="Show Graph", fg="red", bd = 3, font = ("Helvetica", 12),command=lambda: showGraph()) # Este es el raro
button7.place(relx = 0.70, rely =  0.10)

quitBottom = Button(text="QUIT", fg="red", bd = 3, font = ("Helvetica", 16), command=lambda: root.destroy())
#quitBottom.grid(row = 7, column = 3)
quitBottom.place(relx = 0.70, rely =  0.80)


root.mainloop()
