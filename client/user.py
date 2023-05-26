import rsa

class User:

    def __init__(self, username: str, display_name: str, password: str, public_key: rsa.PublicKey, private_key: rsa.PrivateKey, client) -> None:

        self.username = username
        self.display_name = display_name
        self.password = password
        self.public_key = public_key
        self.private_key = private_key
        self._client = client

    def logout(self):
        pass

    def send_message(self):
        pass

    def recv_message(self):
        pass

    def set_display_name(self):
        pass