import socket
import time

    # 서버에 연결
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.20.5', 5051))

while True:
    # 서버로부터 현재 시간을 받음
    server_time = float(client_socket.recv(1024).decode())
    client_socket.send(str(server_time).encode())
