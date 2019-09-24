#!/usr/bin/env python3

import socket

HOST = '0.0.0.0'  # The server's hostname or IP address
PORT = 12345        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_connection:
    server_connection.bind((HOST, PORT))
    server_connection.listen(5)
    while True:
        client_connection, connection_info = server_connection.accept()
        with client_connection:
            print("Connection by", connection_info)
            while True:
                data = client_connection.recv(1024)
                if not data:
                    break
                try:
                    print("Received", data.decode())
                except UnicodeDecodeError:
                    print("Force exit connection due to Unicode Exception", connection_info)
                    break
                client_connection.sendall(data)
            print("Exiting Connection by", connection_info)
