#!/usr/bin/env python3

import socket

HOST = 'eliasfarhan.ch'  # The server's hostname or IP address
PORT = 12345        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall('Hello, world et je parle français éèà'.encode())
    data = s.recv(1024).decode()

print('Received', repr(data))
