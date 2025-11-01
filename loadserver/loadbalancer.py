import socket
import threading
import sys

from server.server import total_connections


class Client(threading.Thread):
    def __init__(self, socket, address, id, signal):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.id = id
        self.signal = signal


class Server(threading.Thread):
    def __init__(self, socket, address, id, cpu_usage, signal):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.id = id
        self.cpu_usage = cpu_usage
        self.signal = signal


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


def accept_client_connection(socket):
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


def accept_server_connection(socket):
    while True:
        try:
            sock, address = socket.accept()
            global total_client_connections
            server = Server(sock, address, total_client_connections, 0, True)
            servers.append(server)
            server.start()
            total_client_connections += 1
        except Exception as e:
            print(f"Error accepting connection: {e}")
            break
