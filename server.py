#!/usr/bin/env python3
import time
import os
import socket
import mysql.connector as mysql
from passlib.hash import pbkdf2_sha256
from threading import Thread
from credentials import mysql_config
from base64 import b64encode

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


    def start_connection_manager(self) -> None:

        # The main loop for the server
        while True:

            connection, addr = self.socketServer.accept()
            print("Connection established!")
            Thread(target=self.recv_command, args=[connection]).start()
            print("Thread made!")

    def recv_command(self, connection: socket.socket) -> str:

        command = connection.recv(128).decode().split()
        print(command)

        match command[0]:
            case "login":
                self.login(command[1], connection)
            case "create":
                self.create_account(command[1], connection)
            case other:
                connection.send(f"Unknown command {command}".encode())

        connection.close()

    def send_data(self, data: str, connection: socket.socket) -> str:
        # Send data
        connection.send(data.encode())

        # Get return from client
        return connection.recv(2048).decode()

    def login(self, username: str, connection: socket.socket) -> None:

        # Create connection to mysql
        with mysql.connect(**mysql_config) as db:
            
            print("Connected to mysql database")
            
            # Create cursor for mysql
            with db.cursor() as dbc:

                print("Create cursor")

                dbc.execute(
                    "SELECT password_hash, password_salt FROM users WHERE username = %s LIMIT 1;",
                    (username,)
                )
                result = dbc.fetchall()

                if not result:
                    print("User does not exist")
                    return
                
                old_hash = result[0][0] # Get the hash returned from the database
                old_salt = result[0][1] # Get the salt returned from the database
                new_salt = b64encode(os.urandom(64)) # Generate a new salt
                
                client_hash = self.send_data(f"{old_salt} {new_salt.decode()}", connection)

                if pbkdf2_sha256.hash(old_hash, salt=new_salt) != client_hash:
                    print("Incorrect password")
                    return
                







    def create_account(self, username: str) -> None:
        pass


if __name__ == "__main__":

    s1 = Server("localhost", 35491)
    s1.start_connection_manager()