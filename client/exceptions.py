class UserDoesNotExist(Exception):

    def __init__(self, username: str) -> None:
        "Raised when the user does not exist in Database"

        super().__init__(f"The user '{username}' does not exist!")

class IncorrectPassword(Exception):

    def __init__(self, password: str) -> None:
        "Raised when the password hash does not match one in Database"

        super().__init__(f"The password '{password}' was incorrect!")

class UserAlreadyExists(Exception):

    def __init__(self, username: str) -> None:
        "Raised when the username already exists in the Database"

        super().__init__(f"The username '{username}' is already taken!")