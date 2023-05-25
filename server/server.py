#!/usr/bin/env python3
import os
import socket
import mysql.connector as mysql
from mysql.connector import cursor
from datetime import datetime
from contextlib import contextmanager
from threading import Thread
from credentials import mysql_credentials


class Server:

    def __init__(self, server_hostname: str, server_port: int) -> None:

        # Set hostname and port for the server from the creation of the client
        self.server_hostname = server_hostname 
        self.server_port = server_port

        # Create a socket for the client to use
        print(f"{datetime.now()} Creating server socket...")
        self.socketServer = socket.socket()
        self.connections = []

        self.socketServer.bind((self.server_hostname, self.server_port))
        self.socketServer.listen()
        print(f"{datetime.now()} Server socket created and listening on {self.server_hostname}:{self.server_port}!")
        

    def __del__(self) -> None:

        # Used to cleanup the socket server after the program exits
        print(f"{datetime.now()} Closing active connections...")
        for connection in self.connections:
            connection.close()

        self.socketServer.close()
        print(f"{datetime.now()} Server socket closed!")


    def start_connection_manager(self) -> None:
        print(f"{datetime.now()} Started connection manager!")

        try:
            # The main loop for the server
            while True:

                print(f"{datetime.now()} (ConnectionManager) Waiting for new connection...")
                connection, addr = self.socketServer.accept()
                self.connections.append(connection)
                print(f"{datetime.now()} (ConnectionManager) Connection established to {connection.getpeername()}!")
                Thread(target=self.recv_command, args=[connection]).start()
                print(f"{datetime.now()} (ConnectionManager) Thread created!")

        except KeyboardInterrupt:
                print(f"{datetime.now()} KeyboardInterrupt to stop server...")

        print(f"{datetime.now()} (ConnectionManager) Stopped connection manager!")


    def recv_command(self, connection: socket.socket) -> str:
        print(f"{datetime.now()} {connection.getpeername()} Waiting for command...")

        command = connection.recv(128).decode().split()

        print(f"{datetime.now()} {connection.getpeername()} Received command {command}!")

        match command[0]:
            case "login":
                self.login(command[1], connection)
            case "create":
                self.create_account(command[1], connection)
            case other:
                print(f"{datetime.now()} {connection.getpeername()} Unknown command '{command}'!")
                connection.send(f"Unknown command {command}".encode())

        print(f"{datetime.now()} {connection.getpeername()} Closing connection...")
        self.connections.remove(connection)
        connection.close()
        print(f"{datetime.now()} (ConnectionManager) Connection closed!")

    @contextmanager # Used with "with" statement
    def mysql_connection(self, connection: socket.socket) -> cursor.MySQLCursor:
        try:
            db = mysql.connect(**mysql_credentials)
            print(f"{datetime.now()} {connection.getpeername()} Connected to MySQL Database!")
            dbc = db.cursor()
            print(f"{datetime.now()} {connection.getpeername()} Created a cursor for MySQL Database!")
            yield dbc

        finally:
            dbc.close()
            db.close()
            print(f"{datetime.now()} {connection.getpeername()} Connection to MySQL Database closed!")
    
    def send_data(self, data: str, connection: socket.socket) -> str:
        # Send data
        connection.send(data.encode())

        # Get return from client 
        return connection.recv(3000).decode()

    def login(self, username: str, connection: socket.socket) -> None:
        print(f"{datetime.now()} {connection.getpeername()} Starting login...")

        with self.mysql_connection(connection) as dbc:

            # Get the password_hash and password_salt from the Database to compare to client_hash
            # Also used to confirm the users exists, otherwise stop login

            dbc.execute(
                "SELECT password_hash, password_salt FROM users WHERE username = %s LIMIT 1;",
                (username,)
            )
            result = dbc.fetchall()

            if not result: # No user
                print(f"{datetime.now()} {connection.getpeername()} Invalid username given: '{username}'!")
                return
            
            result = result[0] # Since it is a list of tuples and we only have 1 tuple, drop the list
            
            db_hash = result[0] # Get the hash returned from the database
            db_salt = result[1] # Get the salt returned from the database
            
            # Send back the salt to client. The client will return the hash to check
            client_hash = self.send_data(f"{db_salt}", connection)
            print(f"{datetime.now()} {connection.getpeername()} Username: {username}")

            if db_hash != client_hash: # Compare hashes
                print(f"{datetime.now()} {connection.getpeername()} Incorrect password given for username '{username}'!")
                return
            
            print(f"{datetime.now()} {connection.getpeername()} Correct password given!")

            
            # If the password hashes match, get display name and keys from the Database to give client user data
            # (Although someone could just hack the Database to get this information, 
            # the only thing that is sacred is the private_key, which is encrypted by the password.)
            # This means that the only way to decrypt the key is with the password, which is never stored on the server or database

            dbc.execute(
                "SELECT display_name, public_key, enc_private_key FROM users WHERE username = %s LIMIT 1;",
                (username,)
            )
            result = dbc.fetchall()[0] # Drop the list, should always return something since user is confirmed to be there

            display_name = result[0]
            public_key = result[1]
            enc_private_key = result[2]

            print(f"{datetime.now()} {connection.getpeername()} Sending {username}'s account data...")

            self.send_data(f"{display_name}||{public_key}||{enc_private_key}", connection)


    def create_account(self, username: str) -> None:
        pass


if __name__ == "__main__":

    s1 = Server("localhost", 35491)
    s1.start_connection_manager()