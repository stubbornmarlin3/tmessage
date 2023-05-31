#!/usr/bin/env python3

from client import Client
from getpass import getpass
from exceptions import UserDoesNotExist
import os
import time

# Config Stuff

VERSION = "v1.0.0"
SERVER_IP = "localhost"
SERVER_PORT = 35491


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


if __name__ == "__main__":
    
    client = Client(SERVER_IP,SERVER_PORT)

    clear_screen()
    print(f"~ Terminal Messages! ~\n\nVersion: {VERSION}\nServer: {SERVER_IP}:{SERVER_PORT}\n\nMade by Aidan Carter.")
    time.sleep(3)

    while True:

        while True:
            clear_screen()
            print("~ Login ~\n")
            username = input("Username: ")
            password = getpass("Password: ")

            try:
                client.login(username,password)
                break
            except UserDoesNotExist as e:
                print("\n",e)
                c = input("Would you like to create a new account? [Y/n]")
                
            except Exception as e:
                print("\n",e)
                time.sleep(3)
                clear_screen()

        while True:
            clear_screen()
            print(f"~ {client.user[username].display_name} ~\n\n")

            print("- Available Commands -\n")

            print(" * [send] ~ Send Message")
            print(" * [fetch] ~ Fetch Messages")
            print(" * [logout] ~ Logout")
            print(" * [quit] ~ Quit program")

            command = input("\n\n> ")

            clear_screen()
            print(f"~ {client.user[username].display_name} ~\n\n")

            match command.split():
                case ["send", *args] if len(args) == 2:
                    print("- Send Message -\n")
                    print(f"To: {args[0]}")
                    print(f"\nMessage: {args[1]}")

                    client.user[username].send_message(args[0],args[1])
                    print("\nSent!")
                    time.sleep(2)

                case ["send"]:
                    print("- Send Message -\n")
                    to_user = input("To: ")
                    message = input("\nMessage: ")

                    client.user[username].send_message(to_user,message)
                    print("\nSent!")
                    time.sleep(2)

                case ["fetch", *args]:
                    print("- Fetch Messages -\n")

                    messages = client.user[username].fetch_messages("--all" not in args)

                    if not messages:
                        print("No new messages!")

                    for from_user in messages.keys():
                        print(f"From: {from_user}\n================")
                        print(*messages[from_user], sep="\n================\n")
                    print("================")

                    input("\nPress enter to return...")

                case ["logout"]:
                    clear_screen()
                    client.logout(username)
                    break

                case ["quit"]:
                    clear_screen()
                    print("Goodbye!")
                    time.sleep(2)
                    clear_screen()
                    exit()
                



