# from tkinter.filedialog import askopenfilename
# filename = askopenfilename()
# print(filename)



from tkinter import filedialog
from tkinter import *
from SecureUDP import SecureUdp
from obPackage import obPackage
import os
import math
from tkinter import messagebox

rowIndex = 1
filesList = [] #Tuple (filename, FileID)
SecureUDP = SecureUDP = SecureUdp(10,4,True)

filename = "hola.png"


def putFileLogic(fatherWindow,entry1,entry2):
	global rowIndex
	global  filesList
	global filename
	fatherWindow.grab_set()
	rowIndex +=1
	print("Name ",filename)
	fd = os.open(filename, os.O_RDWR)
	totalChunks = math.ceil(os.fstat(fd).st_size/1024)

	ip = entry1.get()
	port = int(entry2.get())

	newFilePack = obPackage(20)
	newFilePack.fileName = filename
	newFilePack.chunkID = totalChunks
	byteNewFilePack = newFilePack.serialize(20)
	SecureUDP.sendto(byteNewFilePack,ip,int(port))
	bytePackage , addr = SecureUDP.recivefrom()



	FileAdrrPack = obPackage()
	FileAdrrPack.unserialize(bytePackage,2)
	fileID = ( FileAdrrPack.fileIDByte1 , FileAdrrPack.fileIDRest)
	filesList.append((filename,fileID))

	chunkPacketToSend = obPackage(0)
	chunkPacketToSend.fileIDByte1 = fileID[0]
	chunkPacketToSend.fileIDRest = fileID[1]
	#Envia los chunks
	for chunkID in range(totalChunks):             
		fileSlice = os.read(fd,1024)
		chunkPacketToSend.chunkPayload = fileSlice
		chunkPacketToSend.chunkID = chunkID
		# chunkPacketToSend.print_data()
		serializedObject = chunkPacketToSend.serialize(0)
		SecureUDP.sendto(serializedObject,ip,int(port))

	os.close(fd)

	lbl1 = Label(master=fatherWindow,text="File Successfully transferred your key: ")
	lbl1.grid(row=3, column=1)
	lbl1 = Label(master=fatherWindow,text=fileID)
	lbl1.grid(row=4, column=1)

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
	slave.title("PutFileBox")
	slave.geometry("600x200")

	filename = filedialog.askopenfilename()
	



	lbl1 = Label(master=slave,text="File: ")
	lbl1.grid(row=0, column=0)

	lbl1 = Label(master=slave,text=filename)
	lbl1.grid(row=0, column=1)

	lbl1 = Label(master=slave,text="Insert IP: ")
	lbl1.grid(row=1, column=0)
	entry1 = Entry(slave)
	entry1.grid(row=1,column=1)

	lbl2 = Label(master=slave,text="Insert Port: ")
	lbl2.grid(row=2, column=0)
	entry2 = Entry(slave)
	entry2.grid(row=2,column=1)

	button1 = Button(slave,text="Done",command=lambda: putFileLogic(slave,entry1,entry2))
	button1.grid(row=3,column=0)

	button1 = Button(slave,text="Back",command=lambda: goBack(slave,fatherWindow))
	button1.grid(row=6,column=0)

	addFileButton = Button(slave,text="Add a new file",command=lambda: addNewFile(slave))
	addFileButton.grid(row=7,column=0)



def printAddr(window,ip,port):
	window.withdraw()
	print(type(ip.get()))
	print(type(port.get()))
	window.deiconify()



def goBack(myWindow,fatherWindow):
	fatherWindow.deiconify()
	myWindow.destroy()



def exits(window):
	window.withdraw()
	slave = Tk()
	slave.title("ExistBox")
	slave.geometry("300x100")
	
	lbl1 = Label(master=slave,text="Insert IP: ")
	lbl1.grid(row=0, column=0)
	entry1 = Entry(slave)
	entry1.grid(row=0,column=1)

	lbl2 = Label(master=slave,text="Insert Port: ")
	lbl2.grid(row=1, column=0)
	entry2 = Entry(slave)
	entry2.grid(row=1,column=1)

	button1 = Button(slave,text="Done",command=lambda: printAddr(slave,entry1,entry2))
	button1.grid(row=2,column=0)

	button1 = Button(slave,text="Back",command=lambda: goBack(slave,window))
	button1.grid(row=3,column=0)




def fileList():
	global  filesList
	fileListWindow = Tk()
	fileListWindow.title("List of files")
	for x in range(len(filesList)):
		lbl2 = Label(master=fileListWindow,text=filesList[x])
		lbl2.grid(row=x, column=0)



root = Tk()

root.title("LAMDa Green")
root.geometry("300x100")
button2 = Button(text="SeeFiles", command=fileList)
# button2.pack(anchor=W)          #row=0, column=3)
button2.grid(row=0, column=0)
button2 = Button(text="PutFile", command=lambda: putFile(root))
button2.grid(row=1, column=0)
button2 = Button(text="Exist", command=lambda: exits(root))
# button2.pack(anchor=W)#row=0, column=6)
button2.grid(row=2,column=0)

root.mainloop()

