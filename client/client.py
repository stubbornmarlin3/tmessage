#!/usr/bin/env python3

import os
import rsa
import socket
from user import User
from exceptions import IncorrectPassword, UserDoesNotExist, UserAlreadyExists, ServerError
from passlib.hash import pbkdf2_sha256
from cryptography.fernet import Fernet
from contextlib import contextmanager
from base64 import b64encode

class Client:

    def __init__(self, server_hostname: str, server_port: int) -> None:
        
        # Set hostname and port for the server from the creation of the client
        self._server_hostname = server_hostname 
        self._server_port = server_port

        # Alloc a list where Users connected to this client are held
        self.user:dict[str,User] = {}

    @contextmanager
    def _socket_connection(self) -> None:
        try:
            self._socketClient = socket.socket()
            self._socketClient.settimeout(20)
            self._socketClient.connect((self._server_hostname, self._server_port))
            yield
        finally:
            self._socketClient.close()

    def _send_command(self, command: str) -> str:
        # Used to send command to the server

        # Send command
        self._socketClient.send(command.encode())

        # Get return from server 
        return self._socketClient.recv(3072).decode()

    def login(self, username: str, password: str) -> None:

        # Will need to test for formatting of username and password
        # Will implement later
 
        # Start a socket connection to server
        with self._socket_connection():

            # Send the login command w/ parameter "username" to the server
            # Store return in result - should be the salt
            # If user doesn't exist, will return nothing

            result = self._send_command(f"login {username}")

            if not result:
                raise UserDoesNotExist(username)
            
            stored_salt = result.encode()

            # Generate the new_hash from the new salt and old hash

            test_hash = pbkdf2_sha256.hash(password, salt=stored_salt)

            # Send the test_hash to the server
            # Result should be the user data returned: display_name, public_key, enc_private_key respectively
            # If password is wrong, will return nothing

            result = self._send_command(test_hash)

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

            self.user.update({username : User(username, display_name, test_hash, public_key_rsa, private_key_rsa, self)})

    def create_account(self, username: str, password: str) -> None:
        
        # Will test for formatting of username and password
        # Will implement later

        # Start a socket connection
        with self._socket_connection():

            # Send the create account command to server

            result = self._send_command(f"create {username}")

            # If the user already exists the server will return nothing
            if not result:
                raise UserAlreadyExists(username)

            # Now to generate all the keys and hashes
            # These are generated client-side that way the password and unencrypted private key are never held on the server or sent over the internet

            # Generate salt and hash

            new_salt = b64encode(os.urandom(64))
            password_hash = pbkdf2_sha256.hash(password, salt=new_salt)

            # Generate public & private keys
            public_key_rsa, private_key_rsa = rsa.newkeys(2048)

            # Convert from rsa format to bytes
            public_key = public_key_rsa.save_pkcs1()
            private_key = private_key_rsa.save_pkcs1()

            # Generate fernet key to encrypt private key
            fernet_key = pbkdf2_sha256.hash(password, salt=password_hash.encode())
            fernet_key = bytes(f"{fernet_key[-43:]}=".replace(".","+"),"utf-8") # Need to replace '.' with '+' because it is not in the base64 encoding, which is needed for fernet keys

            # Encrypt private key
            f = Fernet(fernet_key)
            enc_private_key = f.encrypt(private_key)

            # Send all the hashes and keys to server to store
            result = self._send_command(f"{password_hash}||{new_salt.decode()}||{public_key.decode()}||{enc_private_key.decode()}")

            if not result:
                raise ServerError

    def delete_account(self, username:str, password: str) -> None:
        
        # Test formatting of username and password

        # Try to remove the user from the dictionary of users

        try:
            self.user.pop(username)
        except KeyError:
            pass

        # Start a socket connection
        with self._socket_connection():

            # Send the delete account command to server

            result = self._send_command(f"delete {username}")

            if not result:
                raise UserDoesNotExist(username)
            
            stored_salt = result.encode()

            # Generate the new_hash from the new salt and old hash

            test_hash = pbkdf2_sha256.hash(password, salt=stored_salt)

            # Send the test_hash to the server
            # Result should be the user data returned: display_name, public_key, enc_private_key respectively
            # If password is wrong, will return nothing

            result = self._send_command(test_hash)

            if not result:
                raise IncorrectPassword(password)
            
            result = self._send_command("<>") # Send this as a way to check for status of 
            
            if not result:
                raise ServerError
            
    def logout(self, username: str) -> None:
         self.user.pop(username)
        

    def get_users(self) -> list[str]:
        return list(self._users.keys())
    
    

if __name__ == "__main__":


    c1 = Client("localhost", 35491)


    c1.login("arcar","stryker03")
    c1.user["arcar"].send_message("test","New message")

    c1.login("test","password")
    messages = c1.user["test"].fetch_messages(True)

    print(messages)


    