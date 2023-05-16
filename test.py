#!/usr/bin/env python3

from credentials import HOSTNAME, USER, PASSWORD
import mysql.connector as mysql

db_connection = mysql.connect(
    host=HOSTNAME,
    user=USER,
    password=PASSWORD
)

print(db_connection.get_server_info())