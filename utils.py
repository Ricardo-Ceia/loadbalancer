import socket

HEADER_SIZE = 4 * 3  # The header is composed of 3 ints (4 bytes each)


def recv_header(conn) -> bytes:
    data = b""
    while len(data) < HEADER_SIZE:
        chunck = conn.recv(HEADER_SIZE - len(data))
        if not chunck:
            raise ConnectionError("Socket closed before reciving enough data")
        data += chunck
    return data


def recv_exact(conn, message_size):
    data = b""
    while len(data) < message_size:
        chunck = conn.recv(message_size - len(data))
        if not chunck:
            raise ConnectionError("Socket closed before reciving enough data")
        data += chunck
    return data
