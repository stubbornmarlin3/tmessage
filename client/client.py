#!/usr/bin/env python3

import rsa
import socket
from user import User
from passlib.hash import pbkdf2_sha256
from cryptography.fernet import Fernet
from getpass import getpass

class UserDoesNotExist(Exception):

    def __init__(self, username: str) -> None:
        "Raised when the user does not exist in Database"

        super().__init__(f"The user '{username}' does not exist!")

class IncorrectPassword(Exception):

    def __init__(self, password: str) -> None:
        "Raised when the password hash does not match one in Database"

        super().__init__(f"The password '{password}' was incorrect!")

class Client:

    def __init__(self, server_hostname: str, server_port: int) -> None:
        
        # Set hostname and port for the server from the creation of the client
        self.server_hostname = server_hostname 
        self.server_port = server_port

        # Create a socket for the client to use
        self.socketClient = socket.socket()
        self.socketClient.settimeout(20)


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
        self.socketClient.connect((self.server_hostname, self.server_port))

        # Send the login command w/ parameter "username" to the server
        # Store return in result - should be old_salt and new_salt
        # If user doesn't exist, will return nothing

        result = self.send_command(f"login {username}")

        if not result[0]:
            raise UserDoesNotExist(username)
        
        old_salt = result[0].encode()
        session_salt = result[1].encode()

        # Generate the new_hash from the new salt and old hash

        password_hash = pbkdf2_sha256.hash(password, salt=old_salt)
        test_hash = pbkdf2_sha256.hash(password_hash, salt=session_salt)

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

        fernet_key = pbkdf2_sha256.hash(password, salt=password_hash.encode())
        fernet_key = bytes(f"{fernet_key[-43:]}=".replace(".","+"),"utf-8")

        f = Fernet(fernet_key)

        private_key = f.decrypt(enc_private_key).decode()

        # Make public_key and private_key into rsa types for the User class
        
        public_key_rsa = rsa.PublicKey.load_pkcs1(public_key)
        private_key_rsa = rsa.PrivateKey.load_pkcs1(private_key)

        return User(username, display_name, password, public_key_rsa, private_key_rsa)

    def create_account(self) -> None:
        pass



if __name__ == "__main__":

    c1 = Client("localhost", 35491)
    u1 = c1.login("arcar","stryker03")
    print(u1.private_key)