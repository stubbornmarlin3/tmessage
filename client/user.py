import rsa
from exceptions import UserDoesNotExist, IncorrectPassword, ServerError
# from client.client import Client

class User:

    def __init__(self, username: str, display_name: str, password_hash: str, public_key: rsa.PublicKey, private_key: rsa.PrivateKey, client) -> None:

        self.username = username
        self.display_name = display_name
        self.password_hash = password_hash
        self.public_key = public_key
        self.private_key = private_key
        
        self.client = client

    def send_message(self, to:str, message:str) -> None:
        
        # Test for formatting

        # Open connection to server

        with self.client._socket_connection():
            
            # Send send message command
            result = self.client._send_command(f"send {to} {self.username}")

            # This will happen if either the 'from' user does not exist.
            # This means someone can't just send the command to the sever and send from a random username
            if not result:
                raise UserDoesNotExist(self.username)
            
            
            # If username is good (which it should be unless someone is doing something devious), send 'from' password_hash to confirm access
            # This keeps someone from sending messages from accounts they don't own
            result = self.client._send_command(self.password_hash)

            if not result:
                raise IncorrectPassword(self.password_hash)
            

            # Send as a everything is good and to grab the public key of to user
            result = self.client._send_command("<>")

            if not result:
                raise UserDoesNotExist(to)
            
            # Make into a usable public key
            to_public_key = rsa.PublicKey.load_pkcs1(result.encode())

            # Send the encrypted message to the server
            result = self.client._send_command(str(rsa.encrypt(message.encode(),to_public_key)))

            if not result:
                raise ServerError


    def recv_message(self):
        pass

    def regen_keys(self):
        pass

    def change_display_name(self):
        pass

    def change_password(self):
        pass

    def change_username(self):
        pass

