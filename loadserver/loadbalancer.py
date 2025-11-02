import socket
import threading
import sys
import struct
from utils.utils import *


LOADBALANCER_PORT = 5001
LOADBALANCER_ADDRESS = 'localhost'

class Client(threading.Thread):
    def __init__(self, socket, address, id, signal):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.id = id
        self.signal = signal

    def __str__(self):
        return str(self.id) + " " + str(self.address)

    def run(self):
        while self.signal:
            try:
                header = recv_header_client(self.socket)
                client_id, packet_number, message_size = struct.unpack("!III", header)

                message_bytes = recv_exact(self.socket, message_size)
                full_data = header + message_bytes

                if message_size == 0:
                    print("Client " + str(self.id) + "disconnected (empty data)")
                    self.signal = False
                    clients.remove(self)
                    break
                header_size = HEADER_SIZE_CLIENT
                packet_total_size = header_size + message_size
                print(
                    print(
                        f"PACKET INFO:packet_size->{packet_total_size} header_size->{header_size}"
                    )
                )
                print(
                    f"Client_id->{client_id} || Client_id->{client_id} || Packet->{packet_number} || message_size->{message_size} || message_data = {message_bytes}"
                )

                server_id = decision(servers)

                if server_id is None:
                    print("[!] No server available, dropping packet")
                    continue

                try:
                    servers[server_id - 1].socket.sendall(full_data)
                except Exception as e:
                    print(f"[X] Failed to foward to server {server_id}")
            except ConnectionError:
                print(f"[X] Client {self.id} disconnected")
            except Exception as e:
                print(f"[X] Client {self.id} error: {e}")

        self.signal = False
        try:
            self.socket.close()
        except:
            pass
        if self in clients:
            clients.remove(self)
        print(f"[-]Client {self.id} connection closed")


class Server(threading.Thread):
    def __init__(self, socket, address, id, cpu_usage, signal):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.id = id
        self.cpu_usage = cpu_usage
        self.signal = signal

    def __str__(self):
        return (
            str(self.id)
            + " "
            + str(self.address)
            + " current cpu_usage"
            + str(self.cpu_usage)
        )

    def run(self):
        while self.signal:
            try:
                header = recv_header_server(self.socket)
                server_id, client_id, packet_type, packet_number, message_size = (
                    struct.unpack("!II?II", header)
                )

                message_bytes = recv_exact(self.socket, message_size)
                full_data = header + message_bytes

                if message_size == 0:
                    print("Server " + str(self.id) + "disconnected (empty data)")
                    self.signal = False
                    servers.remove(self)
                    break
                header_size = HEADER_SIZE_SERVER
                packet_total_size = header_size + message_size
                print(
                    print(
                        f"PACKET INFO:packet_size->{packet_total_size} header_size->{header_size}"
                    )
                )
                print(
                    f"Server_id->{server_id} || Client_id->{client_id} || Packet->{packet_number} || message_size->{message_size} || message_data = {message_bytes}"
                )

                if 0 <= client_id < len(clients):
                    try:
                        clients[client_id - 1].socket.sendall(full_data)
                    except Exception as e:
                        print(f"[x] Error sending to client {client_id}")
                else:
                    print(f"[X] Invalid client id")
            except ConnectionError:
                print(f"[x] Server {self.id} disconnected unexpectedly")
                break
            except Exception as e:
                print(f"[x] Server {self.id} error: {e}")
                break

        self.signal = False
        try:
            self.socket.close()
        except:
            pass
        if self in servers:
            servers.remove(self)
        print(f"[-] Server {self.id} connection closed")


class RecHealthPacket:
    def __init__(self, server_id, cpu_usage):
        self.server_id = server_id
        self.cpu_usage = cpu_usage


servers: list[Server] = []
total_server_connections = 0
clients: list[Client] = []
total_client_connections = 0


def decision(servers: list[Server]) -> int:
    server_with_smallest_cpu_usage = min(servers, key=lambda s: s.cpu_usage)
    return server_with_smallest_cpu_usage.id


def new_client_connection(socket):
    while True:
        try:
            sock, address = socket.accept()
            global total_client_connections
            client = Client(sock, address, total_client_connections, True)
            clients.append(client)
            client.start()
            total_client_connections += 1
        except Exception as e:
            print(f"Error accepting connection: {e}")
            break


def new_server_connection(socket):
    while True:
        try:
            sock, address = socket.accept()
            global total_server_connections
            server = Server(sock, address, total_client_connections, 0, True)
            servers.append(server)
            server.start()
            total_server_connections += 1
        except Exception as e:
            print(f"Error accepting connection: {e}")
            break


def main():
    try:
        sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print(f"Attempting to bind to {LOADBALANCER_ADDRESS}:{LOADBALANCER_PORT}...")
        sock_client.bind(LOADBALANCER_PORT, LOADBALANCER_PORT)
        sock_client.listen(5)
        sock_server.bind((LOADBALANCER_ADDRESS, LOADBALANCER_PORT + 1))
        sock_server.listen(5)
        print(f"Server successfully listening on {LOADBALANCER_ADDRESS}:{LOADBALANCER_PORT}")
        print("Waiting for connections...")

        # Create new thread to wait for connections
        newServerConnectionsThread = threading.Thread(
            target=new_server_connection, args=(sock_server,)
        )
        newClientConnectionsThread = threading.Thread(
            target=new_client_connection, args=(sock_client,)
        )
        newServerConnectionsThread.daemon = False
        newServerConnectionsThread.start()

        newClientConnectionsThread.daemon = False
        newClientConnectionsThread.start()
        # Keep the main thread alive
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("\nServer shutting down...")
            sock_client.close()
            sock_server.close()
            sys.exit(0)

    except Exception as e:
        print(f"LoadBalancer error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
