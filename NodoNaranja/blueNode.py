from SecureUDP import SecureUdp
from obPackage import obPackage
import threading
import sys

def inputThreadOrange(SecureUdpOrange):
    while True:
        payload , addr = SecureUdpOrange.recivefrom()
        print(payload,addr)
        obPackagex = obPackage()
        if int.from_bytes(payload[:1], byteorder='big') == 15:
            print("Tipo yourGraphposition")
            obPackagex.unserialize(payload,15)
            obPackagex.print_data()
        elif int.from_bytes(payload[:1], byteorder='big') == 16:
            print("Tipo yourGraphposition2")
            obPackagex = obPackage()
            obPackagex.unserialize(payload,16)
            obPackagex.print_data()
        elif int.from_bytes(payload[:1], byteorder='big') == 17:
            print("Tipo GraphComplete")






def main():
    if len(sys.argv) == 5:
        SecureUdpOrange = SecureUdp(10,4,sys.argv[1],int(sys.argv[2])) #ventana de 10 con timeout de 2s

        # Creates the Threads
        t = threading.Thread(target=inputThreadOrange, args=(SecureUdpOrange,))
        t.start()

    # testing type 14
        obPackagex = obPackage(14)
        #obPackagex.print_data()
        serializedObject = obPackagex.serialize(14)
        #print(serializedObject)

    # Testing type 15
        # obPackagex = obPackage(15,32766,32766)
        # obPackagex.print_data()
        # serializedObject = obPackagex.serialize(15)
        # print(serializedObject)

    # Testing type 16
        # obPackagex = obPackage(16,7,10,"10.1.135.32",90)
        # obPackagex.print_data()
        # serializedObject = obPackagex.serialize(16)
        # print(serializedObject)


    # testing type 17
        # obPackagex = obPackage(17)
        # obPackagex.print_data()
        # serializedObject = obPackagex.serialize(17)
        # print(serializedObject)

        SecureUdpOrange.sendto(serializedObject,sys.argv[3],int(sys.argv[4]))

        # if int.from_bytes(serializedObject[:1], byteorder='big') == 14:
        #     print("Tipo JoinGraph")
        # elif int.from_bytes(serializedObject[:1], byteorder='big') == 15:
        #     print("Tipo yourGraphposition")
        #     obPackagex.unserialize(serializedObject,15)
        #     obPackagex.print_data()
        # elif int.from_bytes(serializedObject[:1], byteorder='big') == 16:
        #     print("Tipo yourGraphposition2")
        #     obPackagex.unserialize(serializedObject,16)
        #     obPackagex.print_data()
        # elif int.from_bytes(serializedObject[:1], byteorder='big') == 17:
        #     print("Tipo GraphComplete")
    else:
        print("Error!! To compile do it like this: python3 blueNode.py MyIP MyPort OtherIP OtherPort")
        exit()

if __name__ == "__main__":
    main()
