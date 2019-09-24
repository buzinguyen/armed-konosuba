#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import os
import serial
import struct
from Tkinter import *
from GUI_bundle import *
import thread

class single_controller(Frame):
    arrow = {
        'left': '←', 
        'up': '↑',
        'right': '→',
        'down': '↓',
        'upleft': '↖',
        'upright': '↗',
        'downright': '↘',
        'downleft': '↙',
        'thickup': '▲',
        'thickdown': '▼',
        'thickleft': '◀',
        'thickright': '▶'}
    
    def __init__(self, master):
        Frame.__init__(self, master)
        self.enter = Button(self, text = 'O', command = self.onEnter)
        self.up = Button(self, text = self.arrow['thickup'], command = self.onUp)
        self.down = Button(self, text = self.arrow['thickdown'], command = self.onDown)
        self.up.grid(row = 0, column = 0, padx = 5, pady = 5)
        self.enter.grid(row = 1, column = 0, padx = 5)
        self.down.grid(row = 2, column = 0, padx = 5, pady = 5)
    
    def onEnter(self):
        print('Enter')
    
    def onUp(self):
        print('Up')
    
    def onDown(self):
        print('Down')

class RoboticArm:
    def __init__(self, port = 'COM7', baudrate = 115200):
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        if self.ser.isOpen():
            self.ser.close()
        self.ser.open()
    
    def send_handFigure(self, packet = struct.pack('<HBBBBB', 0, 0, 0, 0, 0, 0)):
        self.ser.write(packet)

    def calibrate_finger(self, finger, step = 1):
        if finger == 'thumb':
            self.ser.write(struct.pack('<HBBBBB', 1, step, 0, 0, 0, 0))
        elif finger == 'index':
            self.ser.write(struct.pack('<HBBBBB', 1, 0, step, 0, 0, 0))
        elif finger == 'middle':
            self.ser.write(struct.pack('<HBBBBB', 1, 0, 0, step, 0, 0))
        elif finger == 'ring':
            self.ser.write(struct.pack('<HBBBBB', 1, 0, 0, 0, step, 0))
        elif finger == 'pinky':
            self.ser.write(struct.pack('<HBBBBB', 1, 0, 0, 0, 0, step))
        else:
            None
    
    def write(self, data):
        decode = struct.unpack('<HBBBBB', data)
        if decode[0] == 0: # a packet with hand figure data
            self.send_handFigure(data)
        elif decode[0] == 1: # a packet to calibrate finger
            # the reason why there is nothing here is because the data from processing will always only to set hand figure. Only the GUI of this python code will be used to calibrate finger, hence, just ignore the packet.
            pass

class processing_socket_adapter(Frame):
    def __init__(self, master, HOST = '', PORT = 50007, serialOut = None):
        Frame.__init__(self, master)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((HOST, PORT))
        echo("[INFO] Waiting for client to connect on port 50007")
        self.start()
        self.packet = struct.pack('<HBBBBB', 0, 0, 0, 0, 0, 0)
        self.serialOut = serialOut
    
    def setSerialOut(self, serial):
        self.serialOut = serial
    
    def start(self):
        thread.start_new_thread(self.read_socket, ())
    
    def read_socket(self):
        try:
            while True:
                self.s.listen(1)
                conn, addr = self.s.accept()
                echo('[INFO] Connected by: {}'.format(addr))

                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    echo("[INFO] From processing: {}".format(data))
                    try:
                        array = data.split(',')
                        mode = int(array[0])
                        thumb = int(((120.0 - 10.0)/180.0) * float(180 - int(float(array[1])*180.0/3.14)))
                        index = int(float(array[2])*180.0/3.14)
                        middle = int(float(array[3])*180.0/3.14)
                        ring = int(float(array[4])*180.0/3.14)
                        pinky = int(float(array[5])*180.0/3.14)
                        echo("[INFO] Sending packet: {}-{}-{}-{}-{}-{}".format(mode, thumb, index, middle, ring, pinky))
                        self.packet = struct.pack('<HBBBBB', 0, thumb, index, middle, ring, pinky)
                        if self.serialOut:
                            self.serialOut.write(self.packet)
                    except IndexError:
                        pass
                    conn.send("{}".format(data))
                conn.close()
        except KeyboardInterrupt:
            conn.close()
            self.s.close()

############################################################################
####                            MAIN LOOP HERE                          ####
############################################################################
# the packet received will have the radian value of respective fingers
# use this value multiply with 180 divided by PI (3.14) to receive degree value
# There is a difference of 21/25 between the processing figure and the mechanical arm due to design mismatch

def root_init():
    global roboticArm, processingAdapter
    roboticArm = RoboticArm('COM5', 115200)
    processingAdapter = processing_socket_adapter(root, serialOut = roboticArm)
    processingAdapter.pack()

def echo(string):
    infoText.insert(END, "{}\n".format(string))
    infoText.key_press(string)

roboticArm = None
processingAdapter = None

root = Tk()
root.title('EEG Control Panel')
infoFrame = Frame(root)
infoFrame.pack(side = LEFT)
controlFrame = Frame(root)
controlFrame.pack(side = LEFT)

step = Entry(controlFrame)
step.insert(END, '1')
step.pack(padx = 5, pady = 10)
indexButton = Button(controlFrame, text = 'index', width = 10, command = lambda: roboticArm.calibrate_finger('index', step = int(step.get())))
indexButton.pack(padx = 5, pady = 2)
middleButton = Button(controlFrame, text = 'middle', width = 10, command = lambda: roboticArm.calibrate_finger('middle', step = int(step.get())))
middleButton.pack(padx = 5, pady = 2)
ringButton = Button(controlFrame, text = 'ring', width = 10, command = lambda: roboticArm.calibrate_finger('ring', step = int(step.get())))
ringButton.pack(padx = 5, pady = 2)
pinkyButton = Button(controlFrame, text = 'pinky', width = 10, command = lambda: roboticArm.calibrate_finger('pinky', step = int(step.get())))
pinkyButton.pack(padx = 5, pady = 2)
thumbButton = Button(controlFrame, text = 'thumb', width = 10, command = lambda: roboticArm.calibrate_finger('thumb', step = int(step.get())))
thumbButton.pack(padx = 5, pady = 2)

infoText = SyntaxHighlightingText(infoFrame)
infoText.pack()
root.after(0, root_init)
root.mainloop()

