import socket
# import threading
import binascii
import json
import datetime

port = 3000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('192.168.100.6', port))


def decodethis(data,imei):
    IMEILength = int(imei[0:4], 16)
    IMEILength = str(IMEILength)
    IMEI = int(binascii.unhexlify(imei[4:34]))
    IMEI = str(IMEI)

    tcpHeader = int(data[0:8], 16)

    if (tcpHeader == 0):
        codec = int(data[16:18], 16)

        if (codec == 8):

            DataLength = int(data[8:16], 16)
            record1 = int(data[18:20], 16)

            i = 0
            Dicts = []
            shift = int(((DataLength-3)*2)/record1)
            while(i<record1):
                timestamp = int(data[20:36], 16)
                date_time = datetime.datetime.fromtimestamp(timestamp / 1000)

                priority = int(data[36+(shift*i):38+(shift*i)], 16)

                longitude = int(data[38+(shift*i):46+(shift*i)], 16)/10**7
                latitude = int(data[46+(shift*i):54+(shift*i)], 16)/10**7

                altitude = int(data[54+(shift*i):58+(shift*i)], 16)

                angle = int(data[58+(shift*i):62+(shift*i)], 16)
                satellites = int(data[62+(shift*i):64+(shift*i)], 16)
                speed = int(data[64+(shift*i):68+(shift*i)], 16)

    #i/o element here later

                record2 = int(data[-10:-8:1], 16)
                crc_16 = int(data[-8::1], 16)
                crc_16 = str(crc_16)

                if(record1 == record2):
                    record = int(data[18:20], 16)
                    record_check_is_good = True
                else:
                    print('something wrong in checking record')
                    record = int(data[18:20], 16).to_bytes(4, byteorder = 'big')
                    record_check_is_good = False

                print("\nDataLength: " + str(DataLength) + "\ncodec: " + str(codec) + "\nrecord: " + str( record) + '\ntimestamp: ' + str(timestamp) + '\npriority: ' + str(priority) + "\nlongitude: " + str(longitude) + "\nlatitude: " + str(latitude) + "\naltitude: " + str(altitude) + "\nangle: " + str(angle) + "\nsatellites: " + str(satellites) + "\nspeed: " + str(speed) + "\ncrc-16: " + str(crc_16))

                i = i + 1
                Dict = {
                    "num":i,
                    "IMEILength": str(int(IMEILength)),
                    "IMEI": str(IMEI),
                    "DataLength": str(DataLength),
                    "codec": str(codec),
                    "record": str(record),
                    "record_check_is_good": record_check_is_good,
                    "timestamp": str(timestamp),
                    "Date_time": str(date_time),
                    "priority": str(priority),
                    "longitude": str(longitude),
                    "latitude": str(latitude),
                    "altitude": str(altitude),
                    "angle": str(angle),
                    "satellites": str(satellites),
                    "speed": str(speed),
                    "crc-16": str(crc_16)
                }
                # i = i + 1
                # Dicts["record"+str(i)]=Dict
                Dicts.append(Dict)


            with open('TCP.json', 'w', encoding='utf-8') as f:
                json.dump(Dicts, f, ensure_ascii=False, indent=4,)

            return record.to_bytes(4, byteorder = 'big'),"breck"

        else:
            print("not codec 8")
            return "0000","breck"

    else:
        print("not tcp")
        return "0000","breck"


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True

    while connected:

        imei = binascii.hexlify(conn.recv(1024))
        print(str(imei))

        try:

            message = '\x01'

            message = message.encode('utf-8')

            conn.send(message)
            print(f'this is server response: ', message)

        except:

            print("Error sending reply. Maybe it's not our device")

        try:

            data = conn.recv(2048)

            recieved = binascii.hexlify(data)

            #print stream data
            print(str(recieved))

            response, BP = decodethis(recieved,imei)
            print(f'this is server response: ',response)

            conn.send(response)
            if(BP=="breck"):
                break
        except socket.error:

            print("Error Occured.")

            break

    conn.close()
    print('\r\n-------------------------------------------------------------------------------------------')

def start():
    s.listen()

    print(" Server is listening ...")

    while True:
        conn, addr = s.accept()

        handle_client(conn,addr)
        # thread = threading.Thread(target=handle_client, args=(conn, addr))
        # thread.start()

        # print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

print("[STARTING] server is starting...")

start()