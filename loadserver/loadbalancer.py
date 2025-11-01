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

    def __str__(self):
        return str(self.id) + " " + str(self.address)

    def run(self):
        pass


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
        pass


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
        host = input("Host: ")
        port = int(input("Port: "))

        sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print(f"Attempting to bind to {host}:{port}...")
        sock_client.bind((host, port))
        sock_client.listen(5)
        sock_server.bind((host, port + 1))
        sock_server.listen(5)
        print(f"Server successfully listening on {host}:{port}")
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
