import argparse
import cv2
import numpy as np
import zmq
from constants import PORT
from utils import string_to_image
from imutils.video import FPS
import base64
import imutils
import time

def rotate_bound(image, angle):
	# grab the dimensions of the image and then determine the
	# center
	(h, w) = image.shape[:2]
	(cX, cY) = (w // 2, h // 2)

	# grab the rotation matrix (applying the negative of the
	# angle to rotate clockwise), then grab the sine and cosine
	# (i.e., the rotation components of the matrix)
	M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
	cos = np.abs(M[0, 0])
	sin = np.abs(M[0, 1])

	# compute the new bounding dimensions of the image
	nW = int((h * sin) + (w * cos))
	nH = int((h * cos) + (w * sin))

	# adjust the rotation matrix to take into account translation
	M[0, 2] += (nW / 2) - cX
	M[1, 2] += (nH / 2) - cY

	# perform the actual rotation and return the image
	return cv2.warpAffine(image, M, (nW, nH))
	
class StreamViewer:
	def __init__(self, port=PORT):
		"""
		Binds the computer to a ip address and starts listening for incoming streams.

		:param port: Port which is used for streaming
		"""
		context = zmq.Context()
		self.footage_socket = context.socket(zmq.REP)
		self.footage_socket.setsockopt(zmq.CONFLATE, 1)
		self.footage_socket.bind('tcp://*:' + port)
		self.current_frame = None
		self.keep_running = True
		self.max = 35

	def receive_stream(self, display=True):
		"""
		Displays displayed stream in a window if no arguments are passed.
		Keeps updating the 'current_frame' attribute with the most recent frame, this can be accessed using 'self.current_frame'
		:param display: boolean, If False no stream output will be displayed.
		:return: None
		"""
		self.keep_running = True
		fps = FPS()
		fps.start()
		initBB = None
		pastBB = None
		ite_counter = 0
		overall_confidence = None
		success = None
		tracker = cv2.TrackerMedianFlow_create()
		grab = False

		while self.footage_socket and self.keep_running:
			try:
				client_response = []
				f = self.footage_socket.recv_string()
				self.current_frame = string_to_image(f)

				if display:
					frame = self.current_frame
					frame = rotate_bound(frame, 90)
					(H, W) = frame.shape[:2]

					if initBB is not None:
						(success, box) = tracker.update(frame)

						if success:
							(x, y, w, h) = [int(v) for v in box]
							cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

							center = (x + w/2, y + h/2)
							
							try:
								offset = (W/2 - center[0], H/2 - center[1], z)
							except:
								offset = (W/2 - center[0], H/2 - center[1])

							old_center = (pastBB[0] + pastBB[2]/2, pastBB[1] + pastBB[3]/2)
							old_offset = (W/2 - old_center[0], H/2 - old_center[1])

							offset_w = 5*float(W/w)
							offset_h = 2*float(H/h)

							if float(W*H)/float(w*h) > 1.2:								
								try:
									if offset[0] > offset_w and self.max > 0: #right
										client_response.append('2')
										self.max = self.max - 1
									elif offset[0] < -offset_w and self.max < 70: #left
										client_response.append('8')
										self.max = self.max + 1
								except ValueError:
									pass

								try:
									if offset[1] > offset_h: #up
										client_response.append("6")
									elif offset[1] < -offset_h: #down
										client_response.append("4")
								except ValueError:
									pass
							else:
								grab = True
							pastBB = (x, y, w, h)
							
							if ite_counter > 20:
								ite_counter = 0
								try:
									target = frame[y:y+h, x:x+w]
									blob = cv2.dnn.blobFromImage(cv2.resize(target, (300, 300)), 0.007843, (300, 300), 127.5)
									net.setInput(blob)
									detections = net.forward()

									for i in np.arange(0, detections.shape[2]):
										confidence = detections[0, 0, i, 2]
										if confidence > 0.8:
											idx = int(detections[0, 0, i, 1])
											box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
											(startX, startY, endX, endY) = box.astype("int")
											if CLASSES[idx] != TARGET_CLASS:
												initBB = None
												tracker = cv2.TrackerMedianFlow_create()
											else:
												if(float(abs(startX - endX)*abs(startY - endY))/float(w*h) < 0.8):
													initBB = None
													tracker = cv2.TrackerMedianFlow_create()
												else:
													overall_confidence = confidence
										else:
											initBB = None
											tracker = cv2.TrackerMedianFlow_create()
								except:
									initBB = None
									tracker = cv2.TrackerMedianFlow_create()
							else:
								ite_counter+=1
						else:
							initBB = None
							tracker = cv2.TrackerMedianFlow_create()
					else:
						blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)

						net.setInput(blob)
						detections = net.forward()

						for i in np.arange(0, detections.shape[2]):
							confidence = detections[0, 0, i, 2]
							if confidence > 0.8:
								idx = int(detections[0, 0, i, 1])
								box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
								(startX, startY, endX, endY) = box.astype("int")
								if CLASSES[idx] != TARGET_CLASS:
									overall_confidence = 0
									pass
								else:
									overall_confidence = confidence
									initBB = (startX, startY, abs(endX - startX), abs(endY - startY))
									pastBB = initBB
									tracker.init(frame, initBB)
							else:
								overall_confidence = 0
					
					fps.update()
					fps.stop()

					info = [
						("Tracker", "medianflow"),
						("Track success", "Yes" if success else "No"),
						("FPS", "{:.2f}".format(fps.fps())),
						("Object", TARGET_CLASS),
						("Confidence", "{:.2f}".format(overall_confidence))
					]

					for (i, (k, v)) in enumerate(info):
						text = "{}: {}".format(k, v)
						cv2.putText(frame, text, (10, H - ((i * 20) + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
					
					cv2.imshow("Object Tracker: {}".format(TARGET_CLASS), frame)
					key = cv2.waitKey(1)
					if not grab:
						for i in range(len(client_response), 2):
							client_response.append('0')
						self.footage_socket.send_string(','.join(client_response))
					else:
						self.footage_socket.send_string('1')
						self.stop()
                    
			except KeyboardInterrupt:
				cv2.destroyAllWindows()
				break
		print("Streaming Stopped!")

	def stop(self):
		"""
		Sets 'keep_running' to False to stop the running loop if running.
		:return: None
		"""
		self.keep_running = False

port = PORT

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', help='The port which you want the Streaming Viewer to use, default is ' + PORT, required=False)
parser.add_argument("-pt", "--prototxt", required=True, help="path to Caffe 'deploy' prototxt file")
parser.add_argument("-m", "--model", required=True, help="path to Caffe pre-trained model")
parser.add_argument("-c", "--confidence", type=float, default=0.2, help="minimum probability to filter weak detections")
args = vars(parser.parse_args())

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
TARGET_CLASS = "bottle"

print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

if args["port"]:
	port = args["port"]

stream_viewer = StreamViewer(port)
stream_viewer.receive_stream()
