#!/usr/bin/env python3

import os
import rsa
import socket
from user import User
from exceptions import IncorrectPassword, UserDoesNotExist, UserAlreadyExists
from passlib.hash import pbkdf2_sha256
from cryptography.fernet import Fernet
from contextlib import contextmanager
from base64 import b64encode

class Client:

    def __init__(self, server_hostname: str, server_port: int) -> None:
        
        # Set hostname and port for the server from the creation of the client
        self.server_hostname = server_hostname 
        self.server_port = server_port

        # Alloc a list where Users connected to this client are held
        self.users:list[User] = []

    @contextmanager
    def socket_connection(self) -> None:
        try:
            self.socketClient = socket.socket()
            self.socketClient.settimeout(20)
            self.socketClient.connect((self.server_hostname, self.server_port))
            yield
        finally:
            self.socketClient.close()

    def send_command(self, command: str) -> str:
        # Used to send command to the server

        # Send command
        self.socketClient.send(command.encode())

        # Get return from server 
        return self.socketClient.recv(3072).decode()

    def login(self, username: str, password: str) -> User:

        # Will need to test for formatting of username and password
        # Will implement later
 
        # Start a socket connection to server
        with self.socket_connection():

            # Send the login command w/ parameter "username" to the server
            # Store return in result - should be the salt
            # If user doesn't exist, will return nothing

            result = self.send_command(f"login {username}")

            if not result:
                raise UserDoesNotExist(username)
            
            stored_salt = result.encode()
            # session_salt = result[1].encode()

            # Generate the new_hash from the new salt and old hash

            test_hash = pbkdf2_sha256.hash(password, salt=stored_salt)
            # test_hash = pbkdf2_sha256.hash(password_hash, salt=salt)

            # Send the test_hash to the server
            # Result should be the user data returned: display_name, public_key, enc_private_key respectively
            # If password is wrong, will return nothing

            result = self.send_command(test_hash)

            if not result:
                raise IncorrectPassword(password)

            display_name, public_key, enc_private_key = result.split("||")

            # Unencrypt the private key that was returned from the server

            fernet_key = pbkdf2_sha256.hash(password, salt=test_hash.encode())
            fernet_key = bytes(f"{fernet_key[-43:]}=".replace(".","+"),"utf-8") # Need to replace '.' with '+' because it is not in the base64 encoding, which is needed for fernet keys

            f = Fernet(fernet_key)

            private_key = f.decrypt(enc_private_key).decode()

            # Load in Public and Private keys for the User class
            # This converts them from bytes to rsa keys
            
            public_key_rsa = rsa.PublicKey.load_pkcs1(public_key)
            private_key_rsa = rsa.PrivateKey.load_pkcs1(private_key)

            self.users.append(User(username, None if display_name == "None" else display_name, password, public_key_rsa, private_key_rsa))

            return self.users[-1] # Return the last added User

    def create_account(self, username: str, password: str) -> User:
        
        # Will test for formatting of username and password
        # Will implement later

        # Start a socket connection
        with self.socket_connection():

            # Send the create account command to server

            result = self.send_command(f"create {username}")

            # If the user already exists the server will return nothing
            if not result:
                raise UserAlreadyExists(username)

            # Now to generate all the keys and hashes
            # These are generated client-side that way the password and unencrypted private key are never held on the server or sent over the internet

            # Generate salt and hash

            new_salt = b64encode(os.urandom(64))
            password_hash = pbkdf2_sha256.hash(password, salt=new_salt).encode()

            # Generate public & private keys
            public_key_rsa, private_key_rsa = rsa.newkeys(2048)

            # Convert from rsa format to bytes
            public_key = public_key_rsa.save_pkcs1()
            private_key = private_key_rsa.save_pkcs1()

            # Generate fernet key to encrypt private key
            fernet_key = pbkdf2_sha256.hash(password, salt=password_hash)
            fernet_key = bytes(f"{fernet_key[-43:]}=".replace(".","+"),"utf-8") # Need to replace '.' with '+' because it is not in the base64 encoding, which is needed for fernet keys

            # Encrypt private key
            f = Fernet(fernet_key)
            enc_private_key = f.encrypt(private_key)

            # Send all the hashes and keys to server to store
            self.send_command(f"{password_hash.decode()}||{new_salt.decode()}||{public_key.decode()}||{enc_private_key.decode()}")

            self.users.append(User(username, None, password, public_key_rsa, private_key_rsa))




if __name__ == "__main__":


    c1 = Client("localhost", 35491)
    c2 = Client("localhost", 35491)
    
    c1.login("arcar", "stryker03")

    c2.create_account("clay","password")
    c1.login("clay","password")

    

    