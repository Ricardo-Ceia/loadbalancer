from _typeshed import DataclassInstance
from ast import Constant
from ntpath import curdir
import socket
import threading
import sys


class RecHealthPacket:
    def __init__(self, server_id, cpu_usage):
        self.server_id = server_id
        self.cpu_usage = cpu_usage


servers: list[RecHealthPacket] = []


def decision(servers: list[RecHealthPacket]) -> int:
    server_with_smallest_cpu_usage = min(servers, key=lambda s: s.cpu_usage)
    return server_with_smallest_cpu_usage.server_id
