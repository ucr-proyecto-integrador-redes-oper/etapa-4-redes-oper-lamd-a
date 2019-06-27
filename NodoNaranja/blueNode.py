from SecureUDP import SecureUdp
from obPackage import obPackage


def main():

    secureUDP = SecureUdp(100,4,"0.0.0.0",6555) #ventana de 100 con timeout de 4s

# testing type 14
    # obPackagex = obPackage(14)
    # obPackagex.print_data()
    # serializedObject = obPackagex.serialize(14)
    # print(serializedObject)

# Testing type 15
    # obPackagex = obPackage(15,32766,32766)
    # obPackagex.print_data()
    # serializedObject = obPackagex.serialize(15)
    # print(serializedObject)

# Testing type 16
#     obPackagex = obPackage(16,7,10,"10.1.135.32",90)
#     obPackagex.print_data()
#     serializedObject = obPackagex.serialize(16)
#     print(serializedObject)


# testing type 17
    obPackagex = obPackage(17)
    obPackagex.print_data()
    serializedObject = obPackagex.serialize(17)
    print(serializedObject)


    if int.from_bytes(serializedObject[:1], byteorder='big') == 14:
        print("Tipo JoinGraph")
    elif int.from_bytes(serializedObject[:1], byteorder='big') == 15:
        print("Tipo yourGraphposition")
        obPackagex.unserialize(serializedObject,15)
        obPackagex.print_data()
    elif int.from_bytes(serializedObject[:1], byteorder='big') == 16:
        print("Tipo yourGraphposition2")
        obPackagex.unserialize(serializedObject,16)
        obPackagex.print_data()
    elif int.from_bytes(serializedObject[:1], byteorder='big') == 17:
        print("Tipo GraphComplete")

if __name__ == "__main__":
    main()
