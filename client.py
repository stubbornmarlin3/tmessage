#!/usr/bin/env python3

import rsa
import socket
from passlib.hash import pbkdf2_sha256
from cryptography.fernet import Fernet
from getpass import getpass

class UserDoesNotExist(Exception):
    "Raised when the user does not exist in Database"

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class IncorrectPassword(Exception):
    "Raised when the password hash does not match one in Database"

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class User:

    def __init__(self, username: str, display_name: str, password: str, public_key: rsa.PublicKey, private_key: rsa.PrivateKey) -> None:

        self.username = username
        self.display_name = display_name
        self.password = password
        self.public_key = public_key
        self.private_key = private_key


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
        return self.socketClient.recv(2048).decode().split("||")

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
            # If user doesn't exist, will return nothing

            result = self.send_command(f"login {username}")

            if not result[0]:
                raise UserDoesNotExist
            
            old_salt = result[0].encode()
            session_salt = result[1].encode()

            # Generate the new_hash from the new salt and old hash

            old_hash = pbkdf2_sha256.hash(password, salt=old_salt)
            test_hash = pbkdf2_sha256.hash(old_hash, salt=session_salt)

            # Send the test_hash to the server
            # Result should be the user data returned: display_name, public_key, enc_private_key respectively
            # If password is wrong, will return nothing

            result = self.send_command(test_hash)

            if not result[0]:
                raise IncorrectPassword

            display_name = result[0]
            public_key = result[1]
            enc_private_key = result[2]

            # Unencrypt the private key that was returned from the server

            fernet_key_old = pbkdf2_sha256.hash(password, salt=old_hash.encode())
            fernet_key_old = bytes(f"{fernet_key_old[-43:]}=".replace(".","+"),"utf-8")

            f_old = Fernet(fernet_key_old)

            private_key = f_old.decrypt(enc_private_key).decode()

            # Make public_key and private_key into rsa types for the User class
            
            public_key = public_key.split("$")
            private_key = private_key.split("$")

            public_key_rsa = rsa.PublicKey(public_key[0], public_key[1])
            private_key_rsa = rsa.PrivateKey(public_key[0], public_key[1], private_key[0], private_key[1], private_key[2])

            return User(username, display_name, password, public_key_rsa, private_key_rsa)

            
            

        except ConnectionRefusedError: # Usually because not connected to internet (or the server is down)
            print("ConnectionRefusedError")

        except TimeoutError: # Server took too long to respond
            print("TimeoutError")

        except UserDoesNotExist: # User did not exist
            print("UserDoesNotExist")

        except IncorrectPassword: # Password was incorrect
            print("IncorrectPassword")

    def create_account(self) -> None:
        pass



if __name__ == "__main__":

    c1 = Client("localhost", 35491)
    u1 = c1.login()
    print(u1.private_key)