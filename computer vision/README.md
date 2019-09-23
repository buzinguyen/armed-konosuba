This is the directory for the active vision system of the prosthesis. Choose a file from PC directory to run on PC, and choose a file from PI directory to run on the prosthesis.

The files are named according to the functions that it supports.

run the pc to render the image sent from pi

syntax on pc:

> python .\StreamViewer_withModel_withResponse.py -pt .\MobileNetSSD_deploy.prototxt.txt -m .\MobileNetSSD_deploy.caffemodel -c 0.8

syntax on pi:

> python Streamer_withResponse.py -s <IP of PC>
