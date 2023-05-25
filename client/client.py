#!/usr/bin/env python3

import rsa
import socket
from user import User
from exceptions import IncorrectPassword, UserDoesNotExist
from passlib.hash import pbkdf2_sha256
from cryptography.fernet import Fernet
from contextlib import contextmanager

class Client:

    def __init__(self, server_hostname: str, server_port: int) -> None:
        
        # Set hostname and port for the server from the creation of the client
        self.server_hostname = server_hostname 
        self.server_port = server_port

        # Create a socket for the client to use
        self.socketClient = socket.socket()
        self.socketClient.settimeout(20)

        self.users:list[User] = []

    @contextmanager
    def socket_connection(self) -> None:
        try:
            self.socketClient = socket.socket()
            self.socketClient.connect((self.server_hostname, self.server_port))
            yield
        finally:
            self.socketClient.close()

    def send_command(self, command: str) -> list[str]:
        # Used to send command to the server

        # Send command
        self.socketClient.send(command.encode())

        # Get return from server as a list of strings seperated by '||' as defined by server
        return self.socketClient.recv(3000).decode().split("||")

    def login(self, username: str, password: str) -> User:

        # Will need to test for formatting of username and password
        # Will implement later
 
        # Start a socket connection to server
        with self.socket_connection():

            # Send the login command w/ parameter "username" to the server
            # Store return in result - should be the salt
            # If user doesn't exist, will return nothing

            result = self.send_command(f"login {username}")

            if not result[0]:
                raise UserDoesNotExist(username)
            
            stored_salt = result[0].encode()
            # session_salt = result[1].encode()

            # Generate the new_hash from the new salt and old hash

            test_hash = pbkdf2_sha256.hash(password, salt=stored_salt)
            # test_hash = pbkdf2_sha256.hash(password_hash, salt=salt)

            # Send the test_hash to the server
            # Result should be the user data returned: display_name, public_key, enc_private_key respectively
            # If password is wrong, will return nothing

            result = self.send_command(test_hash)

            if not result[0]:
                raise IncorrectPassword(password)

            display_name = result[0]
            public_key = result[1]
            enc_private_key = result[2]

            # Unencrypt the private key that was returned from the server

            fernet_key = pbkdf2_sha256.hash(password, salt=test_hash.encode())
            fernet_key = bytes(f"{fernet_key[-43:]}=".replace(".","+"),"utf-8") # Need to replace '.' with '+' because it is not in the base64 encoding, which is needed for fernet keys

            f = Fernet(fernet_key)

            private_key = f.decrypt(enc_private_key).decode()

            # Load in Public and Private keys for the User class
            
            public_key_rsa = rsa.PublicKey.load_pkcs1(public_key)
            private_key_rsa = rsa.PrivateKey.load_pkcs1(private_key)

            self.users.append(User(username, display_name, password, public_key_rsa, private_key_rsa))

            print(self.users)

            return self.users[-1] # Return the last added User

    def create_account(self, username: str, password: str) -> User:
        
        # will test for formatting of username and password
        # will implement later

        # start a socket connection
        self.socketClient.connect((self.server_hostname, self.server_port))





if __name__ == "__main__":

    from threading import Thread

    def login(client):

        client.login("arcar", "stryker03")
    
    c1 = Client("localhost", 35491)
    c2 = Client("localhost", 35491)
    
    Thread(target=login, args=[c1]).start()
    Thread(target=login, args=[c2]).start()

    