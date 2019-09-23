import argparse
import cv2
import zmq
from constants import PORT, SERVER_ADDRESS
from imutils.video import VideoStream
from utils import image_to_string
import time
import struct
import serial
import time

class Streamer:
	def __init__(self, server_address=SERVER_ADDRESS, port=PORT):
		"""
		Tries to connect to the StreamViewer with supplied server_address and creates a socket for future use.

		:param server_address: Address of the computer on which the StreamViewer is running, default is `localhost`
		:param port: Port which will be used for sending the stream
		"""

		print("Connecting to ", server_address, "at", port)
		context = zmq.Context()
		self.footage_socket = context.socket(zmq.REQ)
		self.footage_socket.connect('tcp://' + server_address + ':' + port)
		self.keep_running = True

	def start(self):
		"""
		Starts sending the stream to the Viewer.
		Creates a camera, takes a image frame converts the frame to string and sends the string across the network
		:return: None
		"""
		print("Streaming Started...")
		camera = VideoStream(usePiCamera=True).start()
		time.sleep(2.0)
		self.keep_running = True

		while self.footage_socket and self.keep_running:
			try:
				frame = camera.read()  # grab the current frame
				image_as_string = image_to_string(frame)
				self.footage_socket.send(image_as_string)
				response = self.footage_socket.recv()
				for r in response.decode().split(','):
					if int(r) == 8: # up
						ser.write(struct.pack("<HBBBBB", 4, 1, 1, 0, 0, 0))
					elif int(r) == 2: # down
						ser.write(struct.pack("<HBBBBB", 4, 2, 2, 0, 0, 0))
					elif int(r) == 4: # left
						ser.write(struct.pack("<HBBBBB", 4, 0, 0, 1, 0, 0))
					elif int(r) == 6: # right
						ser.write(struct.pack("<HBBBBB", 4, 0, 0, 2, 0, 0))

			except KeyboardInterrupt:
				cv2.destroyAllWindows()
				break
		print("Streaming Stopped!")
		cv2.destroyAllWindows()

	def stop(self):
		"""
		Sets 'keep_running' to False to stop the running loop if running.
		:return: None
		"""
		self.keep_running = False

port = PORT
server_address = SERVER_ADDRESS

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--server',
					help='IP Address of the server which you want to connect to, default'
						 ' is ' + SERVER_ADDRESS,
					required=True)
parser.add_argument('-p', '--port',
					help='The port which you want the Streaming Server to use, default'
						 ' is ' + PORT, required=False)

args = parser.parse_args()

if args.port:
	port = args.port
if args.server:
	server_address = args.server

ser = serial.Serial()
ser.port = "/dev/ttyUSB0"
ser.baudrate = 115200
if ser.isOpen():
    ser.close()
ser.open()

streamer = Streamer(server_address, port)
streamer.start()
