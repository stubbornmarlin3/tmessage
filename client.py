#!/usr/bin/env python3

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

    def send_command(self, command: str) -> str:
        # Used to send command to the server

        try:
            # Connect and send command
            self.socketClient.settimeout(20)
            self.socketClient.connect((self.server_hostname, self.server_port))
            self.socketClient.send(command.encode())

            # Get return from server then close connection
            output = self.socketClient.recv(256).decode()

        except ConnectionRefusedError:
            return "ConnectionRefusedError"
        
        except TimeoutError:
            return "TimeoutError"

        return output

    def login(self) -> User:

        username = input("Username: ")
        password = getpass("Password: ")

        output = self.send_command(f"login {username} {password}")
        print(output)

        if output:
            print("Here")
        else:
            print("There")


    def create_account(self) -> None:
        pass



if __name__ == "__main__":

    c1 = Client("localhost", 35491)
    c1.login()