import socket
import threading
import sys
import struct

client_id = 0
packet_number = 1


class Packet:
    def __init__(self, client_id, packet_number, message_size, message_data):
        self.client_id = client_id
        self.packet_number = packet_number
        self.message_size = message_size
        self.message_data = message_data.encode("utf-8")
        header = struct.pack("!III", client_id, packet_number, message_size)

        self.packet_data = header + self.message_data
        self.packet_size = len(self.packet_data)


def receive(socket, signal):
    while signal:
        try:
            data = socket.recv(32)
            print(struct.unpack("!IIIp", data))
        except:
            print("You have been disconnected from the server")
            signal = False
            break


host = input("Host: ")
port = int(input("Port: "))

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    client_id += 1
except:
    print("Could not make connection to the server")
    input("Press enter to quit")
    sys.exit(0)

receiveThread = threading.Thread(target=receive, args=(sock, True))
receiveThread.start()

while True:
    message = input()
    message_packet = Packet(
        client_id, packet_number, message_size=len(message), message_data=message
    )
    sock.sendall(message_packet.packet_data)
    packet_number += 1
