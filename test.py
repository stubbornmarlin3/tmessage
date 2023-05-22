#!/usr/bin/env python3

# from credentials import HOSTNAME,HOSTNAME_ALT,USER
# import mysql.connector as mysql
# from passlib.hash import pbkdf2_sha256
# import rsa

# db = mysql.connect(
#     host=HOSTNAME_ALT,
#     user=USER,
#     database="tmessage",
#     connection_timeout=5
# )

# print(db.get_server_info())

# dbc = db.cursor()

# pw = pbkdf2_sha256.hash("password")

# nt = pbkdf2_sha256.hash("passwordd")

# print(pw)
# print(nt)

# print(pbkdf2_sha256.verify("password", pw))
# print(pbkdf2_sha256.verify("password", nt))

# pubkey, privkey = rsa.newkeys(512)

# dbc.execute(f"UPDATE users SET public_key = '{pubkey.n}${pubkey.e}' WHERE username = 'arcar';")

# db.commit()


# import socket

# #Create a socket instance
# socketObject = socket.socket()

# #Using the socket connect to a server...in this case localhost
# socketObject.connect(("192.168.1.4", 35491))


# while(True):

#     data = socketObject.recv(1024)
#     print(data)

#     socketObject.send(b'ping')

#     if data == b'':
#         break

# socketObject.close()

# import pytermgui as ptg

# CONFIG = """
# config:
#     InputField:
#         styles:
#             prompt: dim italic
#             cursor: '@72'
#     Label:
#         styles:
#             value: dim bold

#     Window:
#         styles:
#             border: '60'
#             corner: '60'

#     Container:
#         styles:
#             border: '96'
#             corner: '96'
# """

# with ptg.YamlLoader() as loader:
#     loader.load(CONFIG)

# with ptg.WindowManager() as manager:
#     window = (
#         ptg.Window(
#             "",
#             ptg.InputField("Balazs", prompt="Name: "),
#             ptg.InputField("Some street", prompt="Address: "),
#             ptg.InputField("+11 0 123 456", prompt="Phone number: "),
#             "",
#             ptg.Container(
#                 "Additional notes:",
#                 ptg.InputField(
#                     "A whole bunch of\nMeaningful notes\nand stuff", multiline=True
#                 ),
#                 box="EMPTY_VERTICAL",
#             ),
#             "",
#             ["Submit", lambda *_: manager.__exit__(_, StopIteration, __)],
#             width=60,
#             box="DOUBLE",
#         )
#         .set_title("[210 bold]New contact")
#         .center()
#     )

#     manager.add(window)

from passlib.hash import pbkdf2_sha256
import rsa
from cryptography.fernet import Fernet

password = b'stryker03'

psh = bytes(pbkdf2_sha256.hash(password).encode())

print(len(psh))

print(pbkdf2_sha256.verify(password, psh))

pub, priv = rsa.newkeys(256)

print(pub, priv)

print(f"{hex(pub.n)}${hex(pub.e)}".encode())

print(f"{hex(priv.d)}${hex(priv.p)}${hex(priv.q)}".encode())


pwh = pbkdf2_sha256.hash(password)
print(pwh)

key = bytes(f'{pwh[-43:]}=',"utf-8")
print(key, len(key))

f = Fernet(key)