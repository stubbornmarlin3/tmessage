#!/usr/bin/env python3

import time
import socket
from passlib.hash import pbkdf2_sha256
from cryptography.fernet import Fernet
from getpass import getpass
from threading import Thread

class User:

    def __init__(self) -> None:

        self.username = None
        self.display_name = None
        self._password = None
        self._password_hash = None
        self.public_key = None
        self.private_key = None


class Client:

    def __init__(self, server_hostname: str, server_port: int) -> None:
        
        # Set hostname and port for the server from the creation of the client
        self.server_hostname = server_hostname 
        self.server_port = server_port

        # Create a socket for the client to use
        self.socketClient = socket.socket()
        self.socketClient.settimeout(30)


    def send_command(self, command: str) -> str:
        # Used to send command to the server

        # Send command
        self.socketClient.send(command.encode())

        # Get return from server
        return self.socketClient.recv(2048).decode()

    def login(self) -> User:

        # Client gets username and password
        username = input("Username: ")
        password = getpass("Password: ")

        # Will need to test for formatting of username and password
        # Will implement later
 
        try:
            # Start a socket connection to server
            self.socketClient.connect((self.server_hostname, self.server_port))

            # Send the login command w/ parameter "username" to the server
            # Store return in result - should be old_salt and new_salt
            result = self.send_command(f"login {username}").split()
            
            old_salt = result[0].encode()
            new_salt = result[1].encode()

            old_hash = pbkdf2_sha256.hash(password, salt=old_salt)
            new_hash = pbkdf2_sha256.hash(old_hash, salt=new_salt)

            result = self.send_command(new_hash)
            

        except ConnectionRefusedError: # Usually because not connected to internet (or the server is down)
            print("ConnectionRefusedError")

        except TimeoutError: # Server took too long to respond
            print("TimeoutError")


    def create_account(self) -> None:
        pass



if __name__ == "__main__":

    c1 = Client("localhost", 35491)
    u1 = c1.login()