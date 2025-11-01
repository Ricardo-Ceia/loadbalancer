from pickletools import uint1
import socket

#'Standart Size' of values used on the Header ref:(https://docs.python.org/3/library/struct.html)
UINT_SIZE = 4

HEADER_SIZE_SERVER = UINT_SIZE * 4 + 1
HEADER_SIZE_CLIENT = UINT_SIZE * 3


def recv_header_server(conn) -> bytes:
    data = b""
    while len(data) < HEADER_SIZE_SERVER:
        chunck = conn.recv(HEADER_SIZE_SERVER - len(data))
        if not chunck:
            raise ConnectionError("Socket closed before reciving enough data")
        data += chunck
    return data


def recv_header_client(conn) -> bytes:
    data = b""
    while len(data) < HEADER_SIZE_CLIENT:
        chunck = conn.recv(HEADER_SIZE_CLIENT - len(data))
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
