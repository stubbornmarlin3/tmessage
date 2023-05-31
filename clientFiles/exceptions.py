class UserDoesNotExist(Exception):

    def __init__(self, username: str) -> None:
        "Raised when the user does not exist in Database"

        super().__init__(f"The user '{username}' does not exist!")

class IncorrectPassword(Exception):

    def __init__(self, *args: object) -> None:
        "Raised when the password hash does not match one in Database"

        super().__init__(f"The password was incorrect!", *args)

class UserAlreadyExists(Exception):

    def __init__(self, username: str) -> None:
        "Raised when the username already exists in the Database"

        super().__init__(f"The username '{username}' is already taken!")

class ServerError(Exception):

    def __init__(self, *args: object) -> None:
        "Raised when something goes wrong server side"

        super().__init__("Something went wrong on the server!", *args)

class MessageTooLong(Exception):

    def __init__(self, *args: object) -> None:
        "Raised when the message is too long to be sent"
        super().__init__("The message you are sending is too long!", *args)