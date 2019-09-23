#run this on pi to get alpha-triggered hand control data
import numpy as np
import zmq
import struct
import serial

class StreamViewer:
	def __init__(self, port = "5555"):
		context = zmq.Context()
		self.footage_socket = context.socket(zmq.SUB)
		self.footage_socket.bind('tcp://*:' + port)
		self.footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
		self.keep_running = True
		self.ser = serial.Serial()
		self.ser.port = "/dev/ttyUSB0"
		self.ser.baudrate = 115200
		if self.ser.isOpen():
			self.ser.close()
		self.ser.open()

	def receive_stream(self):
		self.keep_running = True
		while self.footage_socket and self.keep_running:
			try:
				alpha_trigger = self.footage_socket.recv_string()
				if int(alpha_trigger) == 1:
					self.ser.write(struct.pack("<HBBBBB", 0, 90, 50, 50, 50, 50))
				elif int(alpha_trigger) == 2:
					self.ser.write(struct.pack("<HBBBBB", 0, 120, 10, 10, 10, 10))

			except KeyboardInterrupt:
				break
		print("Streaming Stopped!")

	def stop(self):
		self.keep_running = False

stream_viewer = StreamViewer()
stream_viewer.receive_stream()
