import socket
import time

serverSocket = socket.socket()

IP = "192.168.1.4"
PORT = 35491

def recvData(connection: socket.socket) -> None:

    data = connection.recv(128).split()

    print(data)

    if data[0] == b'login':
        login(data[1], data[2], connection)

def login(username: str, password: str, connection: socket.socket) -> None:
    
    if username == b'arcar' and password == b'stryker03':
        connection.send(b'0')
    else:
        connection.close()


if __name__ == "__main__":

    serverSocket.bind((IP,PORT))
    serverSocket.listen()

    while True:

        (connection, addr) = serverSocket.accept()
        print("Connection established!")

        recvData(connection)