# Developer note
This module tries to receive packet sent from hardware through serial and run it on time domain, whose windows size can be adjusted by user, pause or scrolled through history
## HISTORY:
- EEG_SerialAndFFT_OFFICIAL.py: init file
- EEG_SerialAndFFT_withBuffer.py: init file
- test_time_scroller.py: real-time without zero padding, worked
- test_time_scroller_2.py : real-time with zero padding, worked
- test_application.py: try GUI_bundle, not working
- test_application_1.1.py: working with GUI_bundle
- test_application_2.py: GUI_bundle for old data, real-time for new data
## UPDATE:
### Update - init 
- try to span the time as the application runs, so the time will run even if there is no packet received. This is to maintain the frequency information
- This setting will only show frequency from 0 to 50.
### Update 30/08/2018
- try putting control panel to the system - code at Bosch, 30/8/2018
- Try switching to use pyplot the GUI_bundle for ease of implementation
### Update 31/08/2018
- GUIPlot class and PlotNotebook should only be used when all the graphs share similar xlim and ylim as pyplot cannot show different plot range (time -> 5000 data points and frequency of 50 data points)
- Write another application with one frame running with GUIPlot to view the data and use original method to real-time logging data (test_time_scroller_2.py). The serial packets are stored into a csv file that can be viewed using GUI_bundle
- Test running thread for serial communication
### Update 01/09/2018
- Got both graphs to run at the same time and data is recorded to a csv file.
- Attempt to create a GUI with the left frame being the plotter (GUI_bundle) to view the csv file and the right frame as the real-time DAQ (time domain and FFT show)
### Update 07/09/2018
- Got everything to work, currently working on adding more configuration functions to the GUI
- Attempt to run FFT for plotter csv, choose a range of signal (same as setting the filter in GUI_bundle) then add a plot of FFT at the bottom of the same figure (PlotNotebook same tab)
### Update 07/10/2018
- [FAILED] Attempt to rewrite the way system send and receive data, not a packet of 500 data anymore, try to be more continuous with buffer design -> better FFT quality
- Attempt to read for data 256 Hz, change 10 bits down to 8 bits then send a packet of 1500 data points
### Update 08/10/2018
- Finished dynamic FFT function -> after choosing the filter range, FFT can be drawn again
- NOTICE: The PlotNotebook source code is changed so that only plots that are not type "frequency" is applied with event handler. The frequency plot is fixed and unchanged until drawn again using the re FFT function.
- Attempt to write a buffer for serial -> instead of printing out the entire packet of 1500 data points, there will be a buffer to plot out data gradually on time domain (for real-time viewing purpose). The FFT remains the same.
### Update 15/10/2018 
- Attempt to add controller to the parameters of SignalViewer class. All the parameters can now be configured online.
### Update 10/11/2018
- [SUCCESS] Attempt to add window option: define a window size (number of data point) then move that window around for FFT and also save the data points within the window to separate files. This function is to be used for feature extraction.
- [CHANGED] Attempt to create a new profile for the logger application, there will be three subplots in the following order:
    - First plot: whole plot, all the data logged in the file
    - Second plot: dynamic log that is the defined window. The window range will be shown in the first plot and when a, d are pressed, window will be slided across first plot, creating the effect on the second plot (second plot only shows data within the window)
    - Third plot: FFT of the window
### Update 23/11/2018
- [CONT] Attempt to log multiple channels at the same time.
### Update 08/12/2018
- Attempt to rewrite the multi channel function with buffer for play back (from SSVEP function)
- IDEA: instead of rewriting everything, create two serial buffer with each is a size of 750