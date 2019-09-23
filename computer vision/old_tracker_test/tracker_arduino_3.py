from imutils.video import VideoStream
from imutils.video import FPS
import imutils
import time
import cv2
import numpy as np
import serial
import struct

### GO WITH TEST_PAN_TILT_3

tracker = cv2.TrackerMedianFlow_create()
#tracker = cv2.TrackerCSRT_create()
# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
TARGET_CLASS = "bottle"
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt.txt", "MobileNetSSD_deploy.caffemodel")

# initialize the bounding box coordinates of the object we are going
# to track
initBB = None
print("[INFO] starting video stream...")
vs = VideoStream(src=1).start()
time.sleep(1.0)
# initialize the FPS throughput estimator
fps = None
pastBB = None
ser = serial.Serial()
ser.port = "COM10"
ser.baudrate = 115200
ser.open()
ite_counter = 0
overall_confidence = None
success = None
fps = FPS().start()

while True:
	frame = vs.read()
	if frame is None:
		break
	frame = imutils.resize(frame, width = 400)
	(H, W) = frame.shape[:2]
	#matrix = cv2.getRotationMatrix2D((W/2, H/2), 180, 1)
	#frame = cv2.warpAffine(frame,matrix,(W,H))

	if initBB is not None:
		(success, box) = tracker.update(frame)

		if success:
			(x, y, w, h) = [int(v) for v in box]
			cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

			center = (x + w/2, y + h/2)
			'''
			if (pastBB[2]*pastBB[3] - w*h) > 100:
				z = "further"
			elif (w*h - pastBB[2]*pastBB[3]) > 100:
				z = "closer"
			'''
			try:
				offset = (W/2 - center[0], H/2 - center[1], z)
			except:
				offset = (W/2 - center[0], H/2 - center[1])

			old_center = (pastBB[0] + pastBB[2]/2, pastBB[1] + pastBB[3]/2)
			old_offset = (W/2 - old_center[0], H/2 - old_center[1])

			need_delay = 0
			offset_w = 0.005*float(W/w)
			offset_h = 0.005*float(H/h)

			try:
				diff_w = abs(offset[0]/old_offset[0])
				diff_h = abs(offset[1]/old_offset[1])
			except:
				pass
			if diff_w == float("inf") or diff_w == float("-inf") or diff_w == float("NaN"):
				diff_w = 1
			if diff_h == float("inf") or diff_h == float("-inf") or diff_h == float("NaN"):
				diff_h = 1
			LR = 0
			UD = 0
			calibrate_LR = 0
			calibrate_UD = 0
			need_calibrate = False

			try:
				if offset[0] > offset_w: #4
					LR = 1
					calibrate_LR = int(offset[0]*0.065*diff_w)
					need_delay+=offset[0]*0.065*diff_w
					need_calibrate = True
				elif offset[0] < -offset_w: #6
					LR = 0
					calibrate_LR = int(-offset[0]*0.065*diff_w)
					need_delay+=(-offset[0]*0.065*diff_w)
					need_calibrate = True
			except ValueError:
				pass
			try:
				if offset[1] > offset_h: #8
					UD = 0
					calibrate_UD = int(offset[1]*0.05*diff_h)
					need_delay+=offset[1]*0.05*diff_h
					need_calibrate = True
				elif offset[1] < -offset_h: #2
					UD = 1
					calibrate_UD = int(-offset[1]*0.05*diff_h)
					need_delay+=(-offset[1]*0.05*diff_h)
					need_calibrate = True
			except ValueError:
				pass
				
			if need_calibrate:
				if calibrate_LR > 15:
					calibrate_LR = 15
				if calibrate_UD > 15:
					calibrate_UD = 15
				ser.write(struct.pack("<BBBB", LR, UD, calibrate_LR, calibrate_UD))
				time.sleep(float(0.02*need_delay))
			pastBB = (x, y, w, h)
			
			if ite_counter > 100 and calibrate_LR < 5 and calibrate_UD < 5:
				ite_counter = 0
				try:
					target = frame[y:y+h, x:x+w]
					blob = cv2.dnn.blobFromImage(cv2.resize(target, (300, 300)), 0.007843, (300, 300), 127.5)
					net.setInput(blob)
					detections = net.forward()

					for i in np.arange(0, detections.shape[2]):
						confidence = detections[0, 0, i, 2]
						if confidence > 0.95:
							idx = int(detections[0, 0, i, 1])
							box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
							(startX, startY, endX, endY) = box.astype("int")
							if CLASSES[idx] != TARGET_CLASS:
								initBB = None
								tracker = cv2.TrackerMedianFlow_create()
								#tracker = cv2.TrackerCSRT_create()
							else:
								if(float(abs(startX - endX)*abs(startY - endY))/float(w*h) < 0.8):
									initBB = None
									tracker = cv2.TrackerMedianFlow_create()
									#tracker = cv2.TrackerCSRT_create()
								else:
									overall_confidence = confidence
						else:
							initBB = None
							tracker = cv2.TrackerMedianFlow_create()
							#tracker = cv2.TrackerCSRT_create()
				except:
					initBB = None
					tracker = cv2.TrackerMedianFlow_create()
					#tracker = cv2.TrackerCSRT_create()
			else:
				ite_counter+=1
		else:
			initBB = None
			tracker = cv2.TrackerMedianFlow_create()
			#tracker = cv2.TrackerCSRT_create()
	else:
		blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)

		net.setInput(blob)
		detections = net.forward()

		for i in np.arange(0, detections.shape[2]):
			confidence = detections[0, 0, i, 2]
			if confidence > 0.95:
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
	key = cv2.waitKey(1) & 0xFF

	if key == ord("q"):
		break

cv2.destroyAllWindows()