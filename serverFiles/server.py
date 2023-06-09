#!/usr/bin/env python3

import socket
import mysql.connector as mysql
from mysql.connector import cursor
from datetime import datetime
from contextlib import contextmanager
from threading import Thread
from credentials import mysql_credentials


class Server:

    def __init__(self, server_hostname: str, server_port: int) -> None:

        # Set hostname and port for the server from the creation of the client
        self.server_hostname = server_hostname 
        self.server_port = server_port

        # Create a socket for the client to use
        print(f"{datetime.now()} Creating server socket...")
        self.socketServer = socket.socket()
        self.connections = []

        self.socketServer.bind((self.server_hostname, self.server_port))
        self.socketServer.listen()
        print(f"{datetime.now()} Server socket created and listening on {self.server_hostname}:{self.server_port}!")
        

    def __del__(self) -> None:

        # Used to cleanup the socket server after the program exits
        print(f"{datetime.now()} Closing active connections...")
        for connection in self.connections:
            connection.close()

        self.socketServer.close()
        print(f"{datetime.now()} Server socket closed!")


    def start_connection_manager(self) -> None:
        print(f"{datetime.now()} Started connection manager!")

        try:
            # The main loop for the server
            while True:

                print(f"{datetime.now()} (ConnectionManager) Waiting for new connection...")
                connection, addr = self.socketServer.accept()
                self.connections.append(connection)
                print(f"{datetime.now()} (ConnectionManager) Connection established to {connection.getpeername()}!")
                Thread(target=self.recv_command, args=[connection]).start()
                print(f"{datetime.now()} (ConnectionManager) Thread created for {connection.getpeername()}!")

        except KeyboardInterrupt:
                print(f"{datetime.now()} KeyboardInterrupt to stop server...")

        print(f"{datetime.now()} (ConnectionManager) Stopped connection manager!")


    def recv_command(self, connection: socket.socket) -> str:
        print(f"{datetime.now()} {connection.getpeername()} Waiting for command...")

        command = connection.recv(128).decode().split()

        print(f"{datetime.now()} {connection.getpeername()} Received command {command}!")

        match command[0]:
            case "login":
                self.login(command[1], connection)
            case "create":
                self.create_account(command[1], connection)
            case "delete":
                self.delete_account(command[1], connection)
            case "send":
                self.send_message(command[1], command[2], connection)
            case "fetch":
                self.fetch_messages(command[1], connection)
            case other:
                print(f"{datetime.now()} {connection.getpeername()} Unknown command '{command}'!")
                connection.send(f"Unknown command {command}".encode())

        print(f"{datetime.now()} {connection.getpeername()} Closing connection...")
        self.connections.remove(connection)
        connection.close()
        print(f"{datetime.now()} (ConnectionManager) Connection closed!")

    @contextmanager # Used with "with" statement
    def mysql_connection(self, connection: socket.socket) -> tuple[cursor.MySQLCursor, mysql.MySQLConnection]:
        try:
            db = mysql.connect(**mysql_credentials)
            print(f"{datetime.now()} {connection.getpeername()} Connected to MySQL Database!")
            dbc = db.cursor()
            print(f"{datetime.now()} {connection.getpeername()} Created a cursor for MySQL Database!")
            yield dbc, db

        finally:
            dbc.close()
            db.close()
            print(f"{datetime.now()} {connection.getpeername()} Connection to MySQL Database closed!")
    
    def send_data(self, data: str, connection: socket.socket) -> str:
        # Send data
        connection.sendall(data.encode())

        # Get return from client 
        return connection.recv(3072).decode()

    def login(self, username: str, connection: socket.socket) -> None:
        print(f"{datetime.now()} {connection.getpeername()} Starting login...")

        with self.mysql_connection(connection) as (dbc, db):

            # Get the password_hash and password_salt from the Database to compare to client_hash
            # Also used to confirm the users exists, otherwise stop login

            dbc.execute(
                "SELECT password_hash, password_salt, display_name, public_key, enc_private_key FROM users WHERE username = %s LIMIT 1;",
                (username,)
            )
            result = dbc.fetchall()

            if not result: # No user
                print(f"{datetime.now()} {connection.getpeername()} Invalid username given: '{username}'!")
                return
            
            db_hash, db_salt, display_name, public_key, enc_private_key = result[0] # Get the data returned from the database
            
            # Send back the salt to client. The client will return the hash to check
            client_hash = self.send_data(db_salt, connection)
            print(f"{datetime.now()} {connection.getpeername()} Login username: {username}")

            if db_hash != client_hash: # Compare hashes
                print(f"{datetime.now()} {connection.getpeername()} Incorrect password given for username '{username}'!")
                return
            
            print(f"{datetime.now()} {connection.getpeername()} Correct password given!")

            # If the password hashes match, send user data
            # (Although someone could just hack the Database to get this information, 
            # the only thing that is sacred is the private_key, which is encrypted by the password.)
            # This means that the only way to decrypt the key is with the password, which is never stored on the server or database

            print(f"{datetime.now()} {connection.getpeername()} Sending {username}'s account data...")

            self.send_data(f"{display_name}||{public_key}||{enc_private_key}", connection)


    def create_account(self, username: str, connection: socket.socket) -> None:
        print(f"{datetime.now()} {connection.getpeername()} Starting create_account...")

        with self.mysql_connection(connection) as (dbc, db):

            dbc.execute(
                "SELECT 1 FROM users WHERE username = %s LIMIT 1;",
                (username,)
            )
            result = dbc.fetchall()

            if result:
                print(f"{datetime.now()} {connection.getpeername()} User already exists: '{username}'!")
                return
            
            print(f"{datetime.now()} {connection.getpeername()} Creating user '{username}'...")
            
            # Send <> to say "ready for the user data"
            # The result will be the userdata seperated by '||'
            # Need to encode all the data into bytes for the database
            password_hash, new_salt, public_key, enc_private_key = list(map(lambda data: data.encode(), self.send_data("<>", connection).split("||")))

            print(f"{datetime.now()} {connection.getpeername()} Received hash, salt, & keys!")

            # Store in database!

            dbc.execute(
                "INSERT INTO users (username, display_name, password_hash, password_salt, public_key, enc_private_key) VALUES (%s, %s, %s, %s, %s, %s)",
                (username, username, password_hash, new_salt, public_key, enc_private_key)
            )

            print(f"{datetime.now()} {connection.getpeername()} Adding to database...")

            db.commit()

            print(f"{datetime.now()} {connection.getpeername()} User {username} successfully created!")

            self.send_data("<>", connection) # Send this as a way to say everything went good

    def delete_account(self, username: str, connection: socket.socket) -> None:
        print(f"{datetime.now()} {connection.getpeername()} Starting delete_account...")

        with self.mysql_connection(connection) as (dbc, db):

            # Get the password_hash and password_salt from the Database to compare to client_hash
            # Also used to confirm the users exists, otherwise stop method
            
            dbc.execute(
                "SELECT password_hash, password_salt FROM users WHERE username = %s LIMIT 1;",
                (username,)
            )
            result = dbc.fetchall()

            if not result:
                print(f"{datetime.now()} {connection.getpeername()} Invalid username given: '{username}'!")
                return
            
            # Get hash and salt from database
            db_hash, db_salt = result[0]

            # Send back the salt to client. The client will return the hash to check
            client_hash = self.send_data(db_salt, connection)
            print(f"{datetime.now()} {connection.getpeername()} Delete username: {username}")

            if db_hash != client_hash: # Compare hashes
                print(f"{datetime.now()} {connection.getpeername()} Incorrect password given for username '{username}'!")
                return
            
            self.send_data("<>", connection) # Send this as a way of saying the password was correct
            
            print(f"{datetime.now()} {connection.getpeername()} Correct password given!")

            # Remove user from database

            dbc.execute(
                "DELETE FROM users WHERE username = %s;",
                (username,)
            )

            print(f"{datetime.now()} {connection.getpeername()} Deleting user '{username}'...")

            db.commit()

            print(f"{datetime.now()} {connection.getpeername()} User {username} successfully deleted!")

            self.send_data("<>", connection) # Send this as a way of saying everything went good

    def send_message(self, to_user:str, from_user: str, connection: socket.socket) -> None:
        print(f"{datetime.now()} {connection.getpeername()} Sending message: '{from_user}' -> '{to_user}'...")
        
        with self.mysql_connection(connection) as (dbc, db):

            print(f"{datetime.now()} {connection.getpeername()} Checking '{from_user}'...")

            # Get the password hash for the 'from_user' to confirm they have access to send messages
            dbc.execute(
                "SELECT password_hash FROM users WHERE username = %s LIMIT 1;",
                (from_user,)
            )
            result = dbc.fetchall()

            if not result:
                print(f"{datetime.now()} {connection.getpeername()} Invalid username given: '{from_user}'!")
                return

            db_hash = result[0][0]

            client_hash = self.send_data("<>", connection)

            if db_hash != client_hash: # Compare hashes
                print(f"{datetime.now()} {connection.getpeername()} Incorrect password given for username '{from_user}'!")
                return
            
            # Send this saying password was good and now can actually work on sending message
            self.send_data("<>", connection)
            
            # Get the public key for the 'to_user'
            dbc.execute(
                "SELECT public_key FROM users WHERE username = %s LIMIT 1;",
                (to_user,)
            )
            result = dbc.fetchall()

            if not result:
                print(f"{datetime.now()} {connection.getpeername()} Invalid username given: '{to_user}'!")
                return
            
            to_public_key = result[0][0]

            enc_message = self.send_data(to_public_key, connection)

            dbc.execute(
                "INSERT INTO messages (message_content, sender_id, recipient_id) VALUES (%s, %s, %s);",
                (enc_message, from_user, to_user)
            )

            db.commit()

            print(f"{datetime.now()} {connection.getpeername()} Message sent!")
            
            # This is sent as a way to say everthing went good server side
            self.send_data("<>", connection)

    def fetch_messages(self, username: str, connection: socket.socket):
        print(f"{datetime.now()} {connection.getpeername()} Fetching messages for {username}...")
        
        with self.mysql_connection(connection) as (dbc, db):

            print(f"{datetime.now()} {connection.getpeername()} Checking '{username}'...")

            # Get the password hash for the 'from_user' to confirm they have access to fetch messages
            dbc.execute(
                "SELECT password_hash FROM users WHERE username = %s LIMIT 1;",
                (username,)
            )
            result = dbc.fetchall()

            if not result:
                print(f"{datetime.now()} {connection.getpeername()} Invalid username given: '{username}'!")
                return

            db_hash = result[0][0]

            client_hash = self.send_data("<>", connection)

            if db_hash != client_hash: # Compare hashes
                print(f"{datetime.now()} {connection.getpeername()} Incorrect password given for username '{username}'!")
                return
            
            # Send this saying password was good and now can actually work on fetching messages
            unread_only = int(self.send_data("<>", connection))

            dbc.execute(
                f"SELECT sender_id, message_content FROM messages WHERE recipient_id = %s {'AND read_status = 0' if unread_only else ''} ORDER BY sender_id ASC, timestamp ASC;",
                (username,)
            )
            result = dbc.fetchall()

            self.send_data("<>", connection) # Send this to say its going to start sending the fetched messages

            print(f"{datetime.now()} {connection.getpeername()} Sending fetched messages to client...")

            for row in result:
                self.send_data(f"{row[0]}||{row[1]}", connection)

            print(f"{datetime.now()} {connection.getpeername()} Updating read status...")

            dbc.execute(
                "UPDATE messages SET read_status = 1 WHERE recipient_id = %s",
                (username,)
            )

            db.commit()

            print(f"{datetime.now()} {connection.getpeername()} Fetch complete!")

            # Say everything went good server side
            self.send_data("<>", connection)

            
            

if __name__ == "__main__":

    s1 = Server("localhost", 35491)
    s1.start_connection_manager()