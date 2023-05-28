import rsa

class User:

    def __init__(self, username: str, display_name: str, password: str, public_key: rsa.PublicKey, private_key: rsa.PrivateKey) -> None:

        self.username = username
        self.display_name = display_name
        self.password = password
        self.public_key = public_key
        self.private_key = private_key

    def logout(self):
        pass

    def send_message(self):
        pass

    def recv_message(self):
        pass