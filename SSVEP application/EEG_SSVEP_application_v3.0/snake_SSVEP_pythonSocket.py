import socket
import os
import serial
import struct
from Tkinter import *
import thread

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 50007))

s.listen(1)
conn, addr = s.accept()
print("Connected by {}",format(addr))

while True:
    try:
        key = input()
        conn.send(str(key))
    except Exception:
        continue
