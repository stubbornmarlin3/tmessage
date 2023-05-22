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

import sys
from pytermgui import WindowManager, Window

manager = WindowManager()
window = (
    Window(min_width=50)
    + "[210 bold]My first Window!"
    + ""
    + "[157]Try resizing the window by dragging the right border"
    + "[157]Or drag the top border to move the window"
    + "[193 bold]Alt-Tab[/bold 157] cycles windows"
    + "[193 bold]CTRL_C[/bold 157] exits the program"
    + ""
    + ["New window", lambda *_: manager.add(window.copy().center())]
    + ["Close current", lambda _, button: manager.close(button.parent)]
    + ["Exit program", lambda *_: sys.exit(0)]
)

manager.add(window)
manager.run()