#!/usr/bin/env python3

import socket
import time

socketClient = socket.socket()

socketClient.connect(("192.168.1.4",35491))

time.sleep(5)
socketClient.send(b'login\narcar\nstryker0')

data = socketClient.recv(128)
print(data)


socketClient.close()



 