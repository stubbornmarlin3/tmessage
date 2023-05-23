#!/usr/bin/env python3
import time
import socket
import mysql.connector as mysql
from threading import Thread
from credentials import mysql_config

class Server:

    def __init__(self, server_hostname: str, server_port: int) -> None:
        
        # Set hostname and port for the server from the creation of the client
        self.server_hostname = server_hostname 
        self.server_port = server_port

        # Create a socket for the client to use
        self.socketServer = socket.socket()
        print("Server socket created")

        self.socketServer.bind((self.server_hostname, self.server_port))
        self.socketServer.listen()

    def __del__(self) -> None:

        # Used to cleanup the socket server after the program exits
        self.socketServer.close()
        print("Server socket closed")

    def start_mysql_connection(self) -> mysql.MySQLConnection:

        db = mysql.connect(**mysql_config)
        print("Connected to MySQL server")
        print(db.get_server_info())

        return db


    def start_connection_manager(self) -> None:

        # The main loop for the server
        while True:

            connection, addr = self.socketServer.accept()
            print("Connection established!")
            Thread(target=self.recv_command, args=[connection]).start()
            print("Thread made!")

    def recv_command(self, connection: socket.socket) -> str:

        command = connection.recv(256).decode().split()
        print(command)

        match command[0]:
            case "login":
                output = self.login(command[1], command[2])
            case "create":
                output = self.create_account(command[1], command[2])
            case other:
                output = ""

        connection.send(output.encode())
        connection.close()

    def login(self, username: str, password: str) -> str:

        dbc = self.start_mysql_connection().cursor()
        dbc.execute()

    def create_account(self, username: str, password: str) -> str:
        pass


if __name__ == "__main__":

    s1 = Server("localhost", 35491)
    s1.start_connection_manager()