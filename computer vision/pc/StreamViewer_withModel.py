import argparse
import cv2
import numpy as np
import zmq
from constants import PORT
from utils import string_to_image
import base64
import imutils
import time

class StreamViewer:
    def __init__(self, port=PORT):
        """
        Binds the computer to a ip address and starts listening for incoming streams.

        :param port: Port which is used for streaming
        """
        context = zmq.Context()
        self.footage_socket = context.socket(zmq.SUB)
        self.footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
        self.footage_socket.setsockopt(zmq.CONFLATE, 1)
        self.footage_socket.bind('tcp://*:' + port)
        self.current_frame = None
        self.keep_running = True

    def receive_stream(self, display=True):
        """
        Displays displayed stream in a window if no arguments are passed.
        Keeps updating the 'current_frame' attribute with the most recent frame, this can be accessed using 'self.current_frame'
        :param display: boolean, If False no stream output will be displayed.
        :return: None
        """
        self.keep_running = True
        while self.footage_socket and self.keep_running:
            try:
                frame = self.footage_socket.recv_string()
                self.current_frame = string_to_image(frame)

                if display:
                    frame = imutils.resize(self.current_frame, width=400)
                    (h, w) = frame.shape[:2]
                    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                            0.007843, (300, 300), 127.5)

                    net.setInput(blob)
                    detections = net.forward()

                    for i in np.arange(0, detections.shape[2]):
                            confidence = detections[0, 0, i, 2]
                            if confidence > args["confidence"]:
                                    idx = int(detections[0, 0, i, 1])
                                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                                    (startX, startY, endX, endY) = box.astype("int")

                                    label = "{}: {:.2f}%".format(CLASSES[idx],
                                            confidence * 100)
                                    cv2.rectangle(frame, (startX, startY), (endX, endY),
                                            COLORS[idx], 2)
                                    y = startY - 15 if startY - 15 > 15 else startY + 15
                                    cv2.putText(frame, label, (startX, y),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
                                    
                    cv2.imshow("Stream", frame)
                    key = cv2.waitKey(1)

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
parser.add_argument('-p', '--port',
                    help='The port which you want the Streaming Viewer to use, default'
                         ' is ' + PORT, required=False)
parser.add_argument("-pt", "--prototxt", required=True,
        help="path to Caffe 'deploy' prototxt file")
parser.add_argument("-m", "--model", required=True,
        help="path to Caffe pre-trained model")
parser.add_argument("-c", "--confidence", type=float, default=0.2,
        help="minimum probability to filter weak detections")
args = vars(parser.parse_args())

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        "sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

if args["port"]:
    port = args["port"]

stream_viewer = StreamViewer(port)
stream_viewer.receive_stream()
