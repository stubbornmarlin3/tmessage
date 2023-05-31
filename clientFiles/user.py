import rsa
from exceptions import UserDoesNotExist, IncorrectPassword, ServerError, MessageTooLong
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client import Client


class User:

    def __init__(self, username: str, display_name: str, password_hash: str, public_key: rsa.PublicKey, private_key: rsa.PrivateKey, client: 'Client') -> None:

        self.username = username
        self.display_name = display_name
        self.password_hash = password_hash
        self.public_key = public_key
        self.private_key = private_key
        
        self.client = client

    def send_message(self, to:str, message:str) -> None:
        
        # Test for formatting

        if len(message.encode()) > 245:
            raise MessageTooLong

        # Open connection to server

        with self.client._socket_connection():
            
            # Send send message command
            result = self.client._send_command(f"send {to} {self.username}")

            # This will happen if the 'from' user does not exist.
            # This means someone can't just send the command to the sever and send from a random username
            if not result:
                raise UserDoesNotExist(self.username)
            
            
            # If username is good (which it should be unless someone is doing something devious), send 'from' password_hash to confirm access
            # This keeps someone from sending messages from accounts they don't own
            result = self.client._send_command(self.password_hash)

            if not result:
                raise IncorrectPassword
            

            # Send as a everything is good and to grab the public key of to user
            result = self.client._send_command("<>")

            if not result:
                raise UserDoesNotExist(to)
            
            # Make into a usable public key
            to_public_key = rsa.PublicKey.load_pkcs1(result.encode())

            # Send the encrypted message to the server
            result = self.client._send_command(str(rsa.encrypt(message.encode(),to_public_key),encoding="raw_unicode_escape"))

            if not result:
                raise ServerError

    def fetch_messages(self, unread_only: bool) -> dict[str,list[str]]:
        
        # Test for formatting

        # Open connection to server

        with self.client._socket_connection():
            
            # Send fetch messages command
            result = self.client._send_command(f"fetch {self.username}")

            # This will happen if the user does not exist.
            # This means someone can't just send the command to the sever and fetch from a random username
            if not result:
                raise UserDoesNotExist(self.username)
            
            
            # If username is good (which it should be unless someone is doing something devious), send user password_hash to confirm access
            # This keeps someone from fetching messages from accounts they don't own
            result = self.client._send_command(self.password_hash)

            if not result:
                raise IncorrectPassword
            
            self.client._send_command(str(int(unread_only)))

            messages = {}

            while True:

                result = self.client._send_command("<>") # Send this after each row that was grabbed as a way to say 'received'

                if result == "<>":
                    break

                if not result:
                    raise ServerError

                sender_id, message_content = result.split("||")

                message_content = rsa.decrypt(bytes(message_content, "raw_unicode_escape"), self.private_key).decode()

                try:
                    messages[sender_id].append(message_content)
                except KeyError:
                    messages.update({sender_id:[message_content]})


        return messages



    def regen_keys(self):
        pass

    def change_display_name(self):
        pass

    def change_password(self):
        pass

    def change_username(self):
        pass