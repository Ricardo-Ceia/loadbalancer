import socket
import threading
import sys
import struct
from utils.utils import *

connections = []
total_connections = 0


class Client(threading.Thread):
    def __init__(self, socket, address, id, name, signal):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.id = id
        self.name = name
        self.signal = signal

    def __str__(self):
        return str(self.id) + " " + str(self.address)

    def run(self):
        while self.signal:
            try:
                header = recv_header(self.socket)
                client_id, packet_number, message_size = struct.unpack("!III", header)

                message_bytes = recv_exact(self.socket, message_size)
                full_data = header + message_bytes

                if message_size == 0:
                    print("Client " + str(self.address) + " disconnected (empty data)")
                    self.signal = False
                    connections.remove(self)
                    break

                header_size = UINT_SIZE * 3
                packet_total_size = header_size + message_size
                print(
                    f"PACKET INFO:packet_size->{packet_total_size} header_size->{header_size}"
                )
                print(
                    f"Client_id->{client_id} || Packet->{packet_number} || message_size->{message_size} || message_data = {message_bytes}"
                )

                for client in connections:
                    if client.id != self.id:
                        try:
                            client.socket.sendall(full_data)
                        except Exception as e:
                            print(f"Error sending to client {client.id}: {e}")
            except Exception as e:
                print("Client " + str(self.address) + " has disconnected: " + str(e))
                self.signal = False
                if self in connections:
                    connections.remove(self)
                break


def newConnections(socket):
    while True:
        try:
            sock, address = socket.accept()
            global total_connections
            print(f"Connection attempt from {address}")
            client = Client(sock, address, total_connections, "Name", True)
            connections.append(client)
            client.start()
            print("New connection at ID " + str(client))
            total_connections += 1
        except Exception as e:
            print(f"Error accepting connection: {e}")
            break


def main():
    try:
        # Get host and port
        host = input("Host: ")
        port = int(input("Port: "))

        # Create new server socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print(f"Attempting to bind to {host}:{port}...")
        sock.bind((host, port))
        sock.listen(5)

        print(f"Server successfully listening on {host}:{port}")
        print("Waiting for connections...")

        # Create new thread to wait for connections
        newConnectionsThread = threading.Thread(target=newConnections, args=(sock,))
        newConnectionsThread.daemon = False
        newConnectionsThread.start()

        # Keep the main thread alive
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("\nServer shutting down...")
            sock.close()
            sys.exit(0)

    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
