# read developer_note
from __future__ import print_function
import os, sys, serial, ast, thread, csv, time, struct, glob, datetime, json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import scipy.fftpack
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Tkinter import *
from GUI_bundle import *
from multiprocessing import Process
from Queue import *
import pandas as pd
import tkMessageBox
import serial.tools.list_ports
import ttk

#define global variables
serial_queue = [None, None]
signal_viewer = [None, None]
acquireFrame = None
preference_info = json.load(open("preference", "rb"))
currentDir = os.getcwd()

def json_level_count(json_object):
    level = 0
    stack = []
    all_route = []

    for i in json_object.keys():
        stack.append([i])

    while len(stack):
        b = json_object
        current_path = stack.pop()
        tmp_level = len(current_path)
        for i in current_path:
            b = b[i]
        try:
            for key in b.keys():
                new_path = current_path[:]
                new_path.append(key)
                stack.append(new_path)
        except AttributeError:
            if tmp_level > level:
                level = tmp_level
            all_route.append(current_path)
    return level, all_route

def updatePreference():
    global currentDir, signal_plotter
    new_preference = {}
    preference_array = []
    raw_output = signal_plotter.preferenceObject.output()
    
    for key in raw_output.keys():
        preference_array.append(list(np.concatenate([key.split(" "),[raw_output[key]]])))
    for sub_array in preference_array:
        an_instance = sub_array[-1:][0]
        buffer = new_preference
        for i in range(0, len(sub_array)-1):
            try:
                buffer = buffer[sub_array[i]]
                continue
            except KeyError:
                reverse_constant = len(sub_array) + i - 1
                for j in range(i + 1, len(sub_array) - 1):
                    sub_instance = {}
                    sub_instance[sub_array[reverse_constant-j]] = an_instance
                    an_instance = sub_instance
                buffer[sub_array[i]] = an_instance
                if i == 0:
                    new_preference[sub_array[i]] = buffer[sub_array[i]]
                else:
                    for m in range(0, i):
                        sub_instance = new_preference
                        for n in range(0, i - m - 1):
                            sub_instance = sub_instance[sub_array[n]]
                        sub_instance[sub_array[i - m - 1]] = buffer
                        buffer = sub_instance
                    new_preference = buffer
                break
    with open("preference", "wb") as out_file:
        json.dump(json.loads(json.dumps(new_preference)), out_file, sort_keys = True, indent = 4)

    signal_plotter.print("[INFO] Preference file is updated. Serial is restarted with the new preference information")
    restart_serial()

class VerticalScrolledFrame(Frame):
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas, background = "gray25")
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

class signalViewer(Frame):
    global serial_queue, preference_info
    def __init__(self, master, channel_id = 0):
        Frame.__init__(self, master, background = "gray25", width = 550, height = 400)
        self.pack_propagate(0)
        Label(self, text = "Channel {}".format(channel_id), font = "Helvetica 10 bold", background = "gray25", foreground = "gray100").pack(anchor = "w")
        figure = Figure(facecolor = "#404040", tight_layout = True)
        ax1 = figure.add_subplot(2, 1, 1)
        ax2 = figure.add_subplot(2, 1, 2)

        self.channel_id = channel_id
        self.packet_number_frequency = float(preference_info['packet_number_frequency']) # windows size is determined by self.frequency_limit. This number is only used to specify how many packets will be used to run FFT together
        self.packet_number_time = float(preference_info['packet_number_time']) # total windows size = packet size * this number.
        self.frequency_limit = float(preference_info['frequency_limit'])
        self.frequency_amp = float(preference_info['frequency_amp'])

        # the queue prescaler is to help with the dynamic view of the time plot. Cause if the time for 1 packet is too long (1500/256 ~ 5 seconds), it is hard to see the changes
        # This feature helps with making the time plot dynamic by phase shift the entire process and gradually output smaller packets = real packet/prescaler
        # In real life, the trigger process will still be delayed but at least the time plot show movements.
        # If not desire, set queue_prescaler = 1 and also change the PRESCALER value of serial reader class to 1
        self.real_packet_size = float(preference_info['real_packet_size'])
        self.queue_prescaler = float(preference_info['queue_prescaler'])
        self.channel_number = int(preference_info['channel_number'])
        self.packet_size = int(int(self.real_packet_size/self.queue_prescaler)/self.channel_number)
        
        self.time_digital_amplitude = float(preference_info['time_digital_amplitude'])
        self.frequency_digital_amplitude = float(preference_info['frequency_digital_amplitude'])
        self.sampling_frequency = float(preference_info['sampling_frequency'])

        self.packet_time = int(float(1000.0/self.sampling_frequency)*float(self.packet_size))
        self.line1, = ax1.plot([(float(self.time_digital_amplitude)/float(self.packet_size*self.packet_number_time))*x for x in range (0, int(self.packet_size*self.packet_number_time))])
        # change size of plot line2 and line3 to zoom in the value. Current max y = 24*50 = 1200. Change 24 -> 2 to zoom in with height of 100 for EEG
        self.line2, = ax2.plot([int((float(self.frequency_digital_amplitude)/float(self.frequency_amp))/self.frequency_limit)*x for x in range(0, int(self.frequency_limit))])
        self.line3, = ax2.plot([int((float(self.frequency_digital_amplitude)/float(self.frequency_amp))/self.frequency_limit)*x for x in range(0, int(self.frequency_limit))])
        self.dataArrayFrequency = [[0]*int(self.packet_size*self.packet_number_frequency)]
        self.dataArrayTime = [[0]*int(self.packet_size*self.packet_number_time)]
        self.counter = 0
        self.canvas = FigureCanvasTkAgg(figure, self)
        self.canvas.get_tk_widget().pack()
        self.canvas.draw()
        self.previousTime = getTimeMillis()
        self.run_job = None

        ax1.tick_params(axis = 'x', colors = 'white')
        ax1.tick_params(axis = 'y', colors = 'white')
        ax2.tick_params(axis = 'x', colors = 'white')
        ax2.tick_params(axis = 'y', colors = 'white')
        if int(preference_info['frequency_zoom_ylim']):
            ax2.set_ylim(0, int(preference_info['frequency_zoom_ylim']))
        
        self.first_run()
    
    def first_run(self):
        # this first run is used to init all the plotting and the numbers, arrays of this class, run this one time then starts looping with self.run_async_task()
        while True:
            if serial_queue[self.channel_id].qsize() > 0:
                singlePacket = packet(ast.literal_eval(serial_queue[self.channel_id].get(0)))
                self.previousTime = singlePacket.time
                # as there is a delay between packeting read session, hence there should be a zero padding in between packets
                T = 1.0/float(self.sampling_frequency) #Sampling rate of packet 1024 Hz
                packet_time = (float(T)*float(self.packet_size))*1000.0
                data = singlePacket.getData()[self.channel_id]
                self.dataArrayFrequency.append(list(data))
                self.dataArrayTime.append(list(data))
                bufferDataFrequency = list(np.concatenate(self.dataArrayFrequency, 0))
                bufferDataFrequency = bufferDataFrequency[len(bufferDataFrequency) - int(self.packet_size*self.packet_number_frequency):]
                yf = scipy.fftpack.fft(bufferDataFrequency)
                xf = np.linspace(0.0, 1.0/(2.0*T), float(float(self.packet_size)*self.packet_number_frequency)/2.0)
                self.line2.set_xdata(xf[:int(self.frequency_limit*float(T)*self.packet_size*self.packet_number_frequency)])
                self.line2.set_ydata((2.0/(float(self.packet_size)*self.packet_number_frequency) * np.abs(yf[:int(float(self.packet_size)*self.packet_number_frequency)//2]))[:int(self.frequency_limit*float(T)*self.packet_size*self.packet_number_frequency)])
                bufferDataTime = list(np.concatenate(self.dataArrayTime, 0))
                bufferDataTime = bufferDataTime[len(bufferDataTime) - int(self.packet_size*self.packet_number_time):]
                self.line1.set_xdata(np.linspace(0.0, float(packet_time*self.packet_number_time), self.packet_size*self.packet_number_time))
                self.line1.set_ydata(bufferDataTime)
                yf = scipy.fftpack.fft(data)
                xf = np.linspace(0.0, 1.0/(2.0*T), float(float(self.packet_size)/2.0))
                self.line3.set_xdata(xf[:int(self.frequency_limit*float(T)*self.packet_size)])
                self.line3.set_ydata((2.0/float(self.packet_size) * np.abs(yf[:self.packet_size//2]))[:int(self.frequency_limit*float(T)*self.packet_size)])
                self.canvas.draw()
                self.counter = singlePacket.count
                self.dataArrayFrequency = [bufferDataFrequency]
                self.dataArrayTime = [bufferDataTime]
                self.run_async_task()
                break
    
    def run_async_task(self):
        if serial_queue[self.channel_id].qsize() > 0:
            singlePacket = packet(ast.literal_eval(serial_queue[self.channel_id].get(0)))
            # sample spacing
            # This version will buffer the latest 10 packets to do FFT (5000 data points)
            # check if it is a new packet or not (based on counter value)
            # currently line1 for time, line2 for FFT with buffer and line3 for FFT with single packet
            index = singlePacket.count
            data = singlePacket.getData()[self.channel_id]
            T = 1.0/float(self.sampling_frequency)
            packet_time = (float(T)*float(self.packet_size))*1000.0
            if((index - self.counter) == 1 or (self.counter - index) == ((256*self.queue_prescaler) - 1)):
                # as there is a delay between packeting read session, hence there should be a zero padding in between packets
                #[:(500 - len(zero_padder) - len(self.previousResidue))]
                time_padder = singlePacket.time - self.previousTime
                self.previousTime = singlePacket.time
                zero_padder = [0]*int(time_padder - packet_time)
                new_data = zero_padder + list(data)
                self.dataArrayFrequency.append(list(new_data))
                self.dataArrayTime.append(list(new_data))

                bufferDataFrequency = list(np.concatenate(self.dataArrayFrequency))
                bufferDataFrequency = bufferDataFrequency[len(bufferDataFrequency) - int(self.packet_size*self.packet_number_frequency):]
                yf = scipy.fftpack.fft(bufferDataFrequency)
                xf = np.linspace(0.0, 1.0/(2.0*T), float(float(self.packet_size)*self.packet_number_frequency)/2.0)
                self.line2.set_xdata(xf[:int(self.frequency_limit*float(T)*self.packet_size*self.packet_number_frequency)])
                self.line2.set_ydata((2.0/(float(self.packet_size)*self.packet_number_frequency) * np.abs(yf[:int(float(self.packet_size)*self.packet_number_frequency)//2]))[:int(self.frequency_limit*float(T)*self.packet_size*self.packet_number_frequency)])

                bufferDataTime = list(np.concatenate(self.dataArrayTime))
                bufferDataTime = bufferDataTime[len(bufferDataTime) - int(self.packet_size*self.packet_number_time):]
                self.line1.set_xdata(np.linspace(0.0, float(packet_time*self.packet_number_time), self.packet_size*self.packet_number_time))
                self.line1.set_ydata(bufferDataTime)

                yf = scipy.fftpack.fft(data)
                xf = np.linspace(0.0, 1.0/(2.0*T), float(float(self.packet_size)/2.0))
                self.line3.set_xdata(xf[:int(self.frequency_limit*float(T)*self.packet_size)])
                self.line3.set_ydata((2.0/float(self.packet_size) * np.abs(yf[:self.packet_size//2]))[:int(self.frequency_limit*float(T)*self.packet_size)])
                self.canvas.show()
                self.counter = index
                self.dataArrayFrequency = [bufferDataFrequency]
                self.dataArrayTime = [bufferDataTime]
            else:
                print("WARNING: packet {} lost - channel {}".format(index, self.channel_id))
                if index > self.counter:
                    self.dataArrayFrequency.append([[0]*self.packet_size*(index - self.counter)])
                    self.dataArrayTime.append([[0]*self.packet_size*(index - self.counter)])
                    self.counter = index
                else:
                    adder = ((256*self.queue_prescaler) - 1 - self.counter) + (index - 0)
                    self.dataArrayFrequency.append([[0]*self.packet_size*adder])
                    self.dataArrayTime.append([[0]*self.packet_size*adder])
                    self.counter = index
            serial_queue[self.channel_id].task_done()
        self.run_job = root.after(self.packet_time, self.run_async_task)

class packet:
    # configure to work with two channels
    # the channel data is read in odd and even manner
    # use modulus to separate odd data and even data
    def __init__(self, array):
        self.data = array[2:]
        self.count = array[1]
        self.time = array[0]

    def getData(self):
        channel_0 = []
        channel_1 = []
        for i in range(0, len(self.data)):
            if i%2:
                channel_0.append(self.data[i])
            else:
                channel_1.append(self.data[i])
        return [channel_0, channel_1]

    def getCount(self):
        return self.count

def getTimeMillis():
    return(int(round(time.time() * 1000)))

def packet_print(values):
    print("------ SINGLE PACKET ------")
    print("Count: ")
    print(values[0])
    print("Value: ")
    print(values[1:])

class EEGReader(Frame):
    """A class to read the serial messages from Arduino."""
    global preference_info
    SIZE_STRUCT = int(preference_info['real_packet_size']) + 1
    SAMPLING_FREQUENCY = int(preference_info['sampling_frequency'])
    PRESCALER = int(preference_info['queue_prescaler'])
    verbose = 2

    def __init__(self, master, out_file = True, buffer = False):
        global ser
        Frame.__init__(self, master)
        self.file = None
        self.out_file = out_file       
        self.session = getTimeMillis()
        self.buffer = buffer

        if not ser.isOpen():
            try:
                ser.open()
            except:
                pass
            if ser.isOpen():
                self.restart()
        else:            
            self.restart()
        
    def restart(self):
        global ser, preference_info
        self.SIZE_STRUCT = int(preference_info['real_packet_size']) + 1
        self.SAMPLING_FREQUENCY = int(preference_info['sampling_frequency'])
        self.PRESCALER = int(preference_info['queue_prescaler'])
        try:
            self.session = getTimeMillis()
            if not self.buffer:
                ser.close()
                ser.open()
                ser.flushInput()
                thread.start_new_thread(self.readPacket, ())
            else:
                thread.start_new_thread(self.readBuffer, ())
        except:
            pass
    
    def set_configure(self, data):
        self.out_file = data['out_file']
        try:
            if data['new_session']:
                self.session = getTimeMillis()
        except:
            pass
    
    def get_configure(self):
        config = {
            'out_file': self.out_file
        }
        return config
    
    def unixToTime(self, timestamp):
        return datetime.datetime.fromtimestamp(int(float(timestamp)/1000.0)).strftime('%Y%m%d{}%H%M%S'.format("T"))

    def readBuffer(self):
        global serial_queue
        with open('buffer.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter = ',')
            reader = list(reader)
            for line in reader:
                new_values = tuple(map(int, line))
                if self.verbose == 1:
                    packet_print(new_values)
                elif self.verbose == 2:
                    current_time = getTimeMillis()
                    prescaler_time_array = np.linspace(current_time - ((self.SIZE_STRUCT - 1)*float(1.0/float(self.SAMPLING_FREQUENCY))), current_time, self.PRESCALER).astype(int)
                    prescaler_index = 0
                    prescaler_packet_size = int((self.SIZE_STRUCT - 1) / self.PRESCALER)
                    ## from new_values -> smaller packets with counter = new_counter * self.PRESCALER + index of self
                    raw_values = new_values[1:]
                    raw_counter = new_values[0]
                    prescaler_counter_array = [(self.PRESCALER*raw_counter + x) for x in range(0, self.PRESCALER)]
                    for i in prescaler_time_array:
                        timestamp_packet = list(np.concatenate([[i], [prescaler_counter_array[prescaler_index]], raw_values[(prescaler_index*prescaler_packet_size):((prescaler_index + 1)*prescaler_packet_size)]]))
                        for i in range(0, 2):
                            serial_queue[i].put_nowait(str(timestamp_packet))
                        prescaler_index+=1
                # sleep for 1 channel
                #time.sleep(float(1500.0/256.0))
                # sleep for 2 channels
                time.sleep(float(750.0/256.0))

    def readPacket(self):
        global serial_queue, ser
        """Wait for next serial message from the Arduino, and read the whole
        message as a structure."""
        # UPDATE: instead of return data, put it to a queue, plot will read queue data to plot later
        # Keep in mind that the timestamp is not the actual time that the data is recorded by arduino but the timestamp when the entire packet is received into python
        while True:
            try:
                myByte = ser.read(1)
                if myByte == 'S':
                    data = ser.read(self.SIZE_STRUCT)
                    myByte = ser.read(1)
                    if myByte == 'E':
                        # is  a valid message struct
                        unpack_string = '<B'
                        for i in range (0, self.SIZE_STRUCT - 1):
                            unpack_string = unpack_string + 'B'
                        new_values = struct.unpack(unpack_string, data)
                        if self.verbose == 1:
                            packet_print(new_values)
                        elif self.verbose == 2:
                            current_time = getTimeMillis()
                            prescaler_time_array = np.linspace(current_time - ((self.SIZE_STRUCT - 1)*float(1.0/float(self.SAMPLING_FREQUENCY))), current_time, self.PRESCALER).astype(int)
                            prescaler_index = 0
                            prescaler_packet_size = int((self.SIZE_STRUCT - 1) / self.PRESCALER)
                            ## from new_values -> smaller packets with counter = new_counter * self.PRESCALER + index of self
                            raw_values = new_values[1:]
                            raw_counter = new_values[0]
                            prescaler_counter_array = [(self.PRESCALER*raw_counter + x) for x in range(0, self.PRESCALER)]
                            for i in prescaler_time_array:
                                timestamp_packet = list(np.concatenate([[i], [prescaler_counter_array[prescaler_index]], raw_values[(prescaler_index*prescaler_packet_size):((prescaler_index + 1)*prescaler_packet_size)]]))
                                for i in range(0, 2):
                                    serial_queue[i].put_nowait(str(timestamp_packet))
                                prescaler_index+=1
                        if self.out_file:
                            session_packet = list(np.concatenate([[current_time], new_values]))
                            a_packet = packet(session_packet)
                            self.file = open("data/{}_serial_logger.csv".format(self.unixToTime(self.session)), "a+")
                            self.file.write("{},{},{}\n".format(a_packet.time, a_packet.count, str(a_packet.data).replace('[','').replace(']','')))
                            self.file.close()
            except:
                break

class control_panel(Frame):
    # as the timestamp in the csv file is the time that the entire packet is received. Then that time - (time of 500 data points: 488.3 ms) is the relative beginning time
    global preference_info
    def __init__(self, master):
        Frame.__init__(self, master)
        controlFrame = Frame(self, width = 300, height = 500, background = "gray25")
        controlFrame.pack_propagate(0)
        controlFrame.pack(side = LEFT)
        plotFrame = Frame(self, width = 800, height = 500, background = "gray25")
        plotFrame.pack_propagate(0)
        plotFrame.pack(side = LEFT)

        configureFrame = Frame(controlFrame, width = 300, height = 300, background = "gray25")
        configureFrame.pack_propagate(0)
        configureFrame.pack()
        terminalFrame = Frame(controlFrame, width = 300, height = 200, background = "gray25")
        terminalFrame.pack_propagate(0)
        terminalFrame.pack()

        configureNotebook = ttk.Notebook(configureFrame)
        configureTab = ttk.Frame(configureNotebook)
        preferenceTab = ttk.Frame(configureNotebook)
        configureNotebook.add(configureTab, text = "General")
        configureNotebook.add(preferenceTab, text = "Preference")
        configureNotebook.pack()

        scrollable_frame = VerticalScrolledFrame(preferenceTab, background = "gray25")
        scrollable_frame.pack()

        scrollable_configure = VerticalScrolledFrame(configureTab, background = "gray25")
        scrollable_configure.pack()
        
        self.preferenceObject = configure_tab(scrollable_frame.interior, width = 50, split_percentage = 0.45)
        preference_depth, all_preference_option = json_level_count(preference_info)
        for option in all_preference_option:
            preference_value = preference_info
            for sub in option:
                preference_value = preference_value[sub]
            self.preferenceObject.add_instance(name = " ".join(option), method = "entry", init_value = str(preference_value))
        self.preferenceObject.pack()

        preferenceUpdateButton = Button(scrollable_frame.interior, text = "Update", command = updatePreference, width = 15)
        preferenceUpdateButton.pack()

        self.notebook = PlotNotebook(plotFrame)
        self.notebook.pack()
        
        self.sessionObject = configure_tab(scrollable_configure.interior, width = 50, split_percentage = 0.15)
        sessionObjectLabel = Label(scrollable_configure.interior, text = "Session Configuration", anchor = "w", justify = LEFT, width = 50, font = "Helvetica 10 bold", background = "gray25", foreground = "gray100")
        sessionObjectLabel.pack(pady = (10, 0))
        self.sessionObject.add_instance(name = 'Session', method = 'menu', input_option = os.listdir('data'), init_value = 'Select')
        self.sessionObject.pack()
        sessionButtonFrame = Frame(scrollable_configure.interior, width = 300, height = 50, background = "gray25")
        sessionButtonFrame.pack()
        update_session_button = Button(sessionButtonFrame, text = 'Update', command = self.update_session, width = 15)
        update_session_button.pack(padx = 5, side = LEFT)        
        refresh_session_button = Button(sessionButtonFrame, text = 'Refresh', command = self.refresh_session, width = 15)
        refresh_session_button.pack(padx = 5, side = LEFT)   

        self.serialObject = configure_tab(scrollable_configure.interior, width = 50)
        serialObjectLabel = Label(scrollable_configure.interior, text = "Serial Configuration", anchor = "w", justify = LEFT, width = 50, font = "Helvetica 10 bold", background = "gray25", foreground = "gray100")
        serialObjectLabel.pack(pady = (10, 0))
        serial_list = [comport.device for comport in serial.tools.list_ports.comports()]
        serial_list.append('buffer')
        self.serialObject.add_instance(name = 'Port', method = 'menu', input_option = serial_list, init_value = 'Select')
        self.serialObject.add_instance(name = 'Baudrate', method = 'entry', init_value = '115200')
        self.serialObject.pack()
        update_serial_button = Button(scrollable_configure.interior, text = 'Connect', command = self.update_serial, width = 15)
        update_serial_button.pack()      

        actionLabel = Label(scrollable_configure.interior, text = "Action Panel", anchor = "w", justify = LEFT, width = 50, font = "Helvetica 10 bold", background = "gray25", foreground = "gray100")
        actionLabel.pack(pady = (10, 0))
        actionFrame = Frame(scrollable_configure.interior, background = "gray25")
        actionFrame.pack_propagate(0)
        actionFrame.pack()
        triggerButton = Button(actionFrame, text = 'Trigger', command = self.on_click_trigger, width = 15)
        reFFTButton = Button(actionFrame, text = "FFT", command = self.redrawFFT, width = 15)
        triggerButton.grid(row = 0, column = 0, padx = 5)
        reFFTButton.grid(row = 0, column = 1, padx = 5)

        self.windowObject = configure_tab(scrollable_configure.interior, width = 50)
        self.windowObject.add_instance(name = "Window Length", method = 'entry', init_value = self.notebook.currentApp.plot.window_size)
        self.windowObject.bind("<Leave>", self.on_update_window)
        self.windowObject.pack(pady = 5)

        terminalScroll = Scrollbar(terminalFrame)
        self.terminal = SyntaxHighlightingText(terminalFrame)
        self.terminal.config(wrap = WORD, font = 'Helvetica 8', spacing3 = 5, bg = 'gray10', fg = "gray100")
        terminalScroll.config(command = self.terminal.yview)
        self.terminal.config(yscrollcommand = terminalScroll.set)
        terminalScroll.pack(side = RIGHT, fill = Y, padx = (0, 10), pady = 5)
        self.terminal.pack(side = LEFT, padx = (10, 0), pady = 5)
        self.terminal.config(state = DISABLED)

        self.file = None
        self.shift = False
    
    def on_update_window(self, event):
        new_window_size = int(self.windowObject.output()['Window Length'])
        if new_window_size > 0 and new_window_size != self.notebook.currentApp.plot.window_size:
            self.notebook.currentApp.plot.window_size = new_window_size
            signal_plotter.print("[INFO] Window size is updated to {}".format(new_window_size))
        elif new_window_size == 0 and self.notebook.currentApp.plot.window_size is not None:
            self.notebook.currentApp.plot.window_size = None
            signal_plotter.print("[INFO] Window is now in custom mode.")
    
    def redrawFFT(self):
        global signal_plotter
        signal_plotter.print("[INFO] Run FFT for the chosen window")
        current_filter = self.notebook.currentApp.getFilter()
        for i in range (0, self.notebook.currentApp.getPlotCount()):
            self.notebook.currentApp.removePlot(1)
            self.notebook.currentApp.redraw()
        self.update_session(limA = current_filter['A'], limB = current_filter['B'], reFFT = True)
    
    def print(self, string):
        self.terminal.config(state = NORMAL)
        self.terminal.insert(END, "{}\n".format(string))
        self.terminal.config(state = DISABLED)
        self.terminal.key_press(string)
        self.terminal.see("end")

    def update_session(self, limA = None, limB = None, reFFT = False):
        self.plot_session(self.sessionObject.output()['Session'], limA = limA, limB = limB, reFFT = reFFT)
    
    def refresh_session(self):
        self.sessionObject.instance_array['Session'].set_input_option(os.listdir('data'))
    
    def on_click_trigger(self):
        global serial_reader
        config = serial_reader.get_configure()
        new_config = {
            "out_file": (not config["out_file"]),
            "new_session": 1
        }
        serial_reader.set_configure(new_config)
        self.print("[INFO] Logging triggered. Current status: {}".format((not config["out_file"])))
    
    def update_serial(self):
        global ser
        try:
            serial_input = self.serialObject.output()
            if serial_input['Port'] == 'buffer':
                restart_serial(buffer = True)
            else:
                ser.port = serial_input['Port']
                ser.baudrate = int(serial_input['Baudrate'])
                restart_serial()
        except:
            pass
    
    def plot_session(self, session, limA = None, limB = None, reFFT = False):
        if not reFFT:
            log_file = pd.read_csv("data/{}".format(session), sep = ",", dtype = None, header = None)
            log_file['data'] = log_file[log_file.columns[2:]].apply(lambda x: ','.join(x.dropna().astype(int).astype(str)),axis=1)
            self.file = log_file[[0,1,'data']].copy()
        x_array = []
        y_array = []
        for i in range(0, self.file.shape[0]):
            packet_time = self.file.iloc[i][0]
            packet_data = self.file.iloc[i]['data']
            x_array.append(list(np.linspace(long(packet_time) - float(1500.0/256.0)*1000.0, long(packet_time), 1500).astype(long)))
            y_array.append(map(int, packet_data.split(",")))
        x_array = list(np.concatenate(x_array))
        y_array = list(np.concatenate(y_array))
        plot = singlePlot()
        plot.setX(x_array)
        plot.setY(y_array)
        plot.setIndex(1)

        fft_cursor_A = singlePlot()
        fft_cursor_B = singlePlot()
        
        if limA and limB:
            # add fft cursor to time plot
            fft_cursor_A.setX([limA, limA])
            fft_cursor_A.setY([min(y_array), max(y_array)])
            fft_cursor_A.setType("frequency_cursor")
            fft_cursor_A.setIndex(1)
            fft_cursor_B.setX([limB, limB])
            fft_cursor_B.setY([min(y_array), max(y_array)])
            fft_cursor_B.setType("frequency_cursor")
            fft_cursor_B.setIndex(1)
            # plot FFT
            fft_plot = singlePlot()
            # Number of samplepoints
            filter_data = {"time": x_array, "value": y_array}
            filter_dataFrame = pd.DataFrame(data = filter_data)
            filter_dataFrame = filter_dataFrame[(filter_dataFrame['time'] <= limB) & (filter_dataFrame['time'] >= limA)]
            fft_x = list(filter_dataFrame['time'])
            fft_y = list(filter_dataFrame['value'])
            N = len(fft_y)
            # sample spacing
            T = float(max(fft_x) - min(fft_x))/float(N)
            T = T * 0.001
            yf = scipy.fftpack.fft(fft_y)
            fft_plot.setX(np.linspace(min(fft_x), max(fft_x), int(50.0*float(T)*float(N))))
            fft_plot.setY((2.0/N * np.abs(yf[:N//2]))[:int(50.0*float(T)*float(N))])
            fft_plot.setType("frequency")
            fft_plot.setIndex(2)
            self.notebook.currentApp.setMethod('line')
            self.notebook.currentApp.addPlot(plot)
            self.notebook.currentApp.addPlot(fft_plot)  
            self.notebook.currentApp.addPlot(fft_cursor_A)
            self.notebook.currentApp.addPlot(fft_cursor_B)
            self.notebook.currentApp.setFilter(limA, limB)
        else:
            # add fft cursor to time plot
            fft_cursor_A.setX([min(x_array), min(x_array)])
            fft_cursor_A.setY([min(y_array), max(y_array)])
            fft_cursor_A.setType("frequency_cursor")
            fft_cursor_A.setIndex(1)
            fft_cursor_B.setX([max(x_array), max(x_array)])
            fft_cursor_B.setY([min(y_array), max(y_array)])
            fft_cursor_B.setType("frequency_cursor")
            fft_cursor_B.setIndex(1)
            # plot FFT
            fft_plot = singlePlot()
            # Number of samplepoints
            N = len(y_array)
            # sample spacing
            T = float(max(x_array) - min(x_array))/float(N)
            T = T * 0.001
            yf = scipy.fftpack.fft(y_array)
            #xf = np.linspace(0.0 + min(x_array), 1.0/(2.0*T) + min(x_array), N/2)
            #fft_plot.setX(xf[:int(50.0*float(T)*float(N))])
            fft_plot.setX(np.linspace(min(x_array), max(x_array), int(50.0*float(T)*float(N))))
            fft_plot.setY((2.0/N * np.abs(yf[:N//2]))[:int(50.0*float(T)*float(N))])
            fft_plot.setType("frequency")
            fft_plot.setIndex(2)
            self.notebook.currentApp.setMethod('line')
            self.notebook.currentApp.addPlot(plot)
            self.notebook.currentApp.addPlot(fft_plot)
            self.notebook.currentApp.addPlot(fft_cursor_A)
            self.notebook.currentApp.addPlot(fft_cursor_B)
            self.notebook.currentApp.setFilter(min(x_array), max(x_array))
        
        self.notebook.currentApp.redraw()

    def onKeyPress(self, event):
        # If there is no window, then move graph
        # If there is window, move window
        if event.char == 'a':
            currentFilter = self.notebook.currentApp.getFilter()
            filterStep = 0.05*float(currentFilter['B'] - currentFilter['A'])
            filterA = currentFilter['A'] - filterStep
            filterB = currentFilter['B'] - filterStep
            self.notebook.currentApp.setFilter(filterA, filterB)
            self.notebook.currentApp.redraw()
        elif event.char == 'd':
            currentFilter = self.notebook.currentApp.getFilter()
            filterStep = 0.05*float(currentFilter['B'] - currentFilter['A'])
            filterA = currentFilter['A'] + filterStep
            filterB = currentFilter['B'] + filterStep
            self.notebook.currentApp.setFilter(filterA, filterB)
            self.notebook.currentApp.redraw()
        elif event.char == 'A' and self.notebook.currentApp.plot.window_size is not None:
            filterHandler = self.notebook.currentApp.plot.filterHandler
            if filterHandler['counter'] == 2:
                filterStep = 0.05*self.notebook.currentApp.plot.window_size
                filterA = filterHandler['A'] - filterStep
                filterB = filterHandler['B'] - filterStep
                self.notebook.currentApp.windowing(filterA, filterB)
                self.notebook.currentApp.redraw()
        elif event.char == 'D' and self.notebook.currentApp.plot.window_size is not None:
            filterHandler = self.notebook.currentApp.plot.filterHandler
            if filterHandler['counter'] == 2:
                filterStep = 0.05*self.notebook.currentApp.plot.window_size
                filterA = filterHandler['A'] + filterStep
                filterB = filterHandler['B'] + filterStep
                self.notebook.currentApp.windowing(filterA, filterB)
                self.notebook.currentApp.redraw()

def restart_serial(buffer = False):
    global ser, acquireFrame, serial_queue, serial_reader, signal_viewer, preference_info
    preference_info = json.load(open("preference", "rb"))
    
    if not buffer:
        if ser.isOpen():
            ser.close()
        ser.open()
    
    serial_reader.buffer = buffer

    if ser.isOpen() or buffer:
        try:
            # ignore this error
            acquireFrame.pack_forget()
            acquireFrame.destroy()
        except:
            pass
        acquireFrame = Frame(root, width = 1100, height = 400, background = "gray25")
        acquireFrame.pack_propagate(0)
        acquireFrame.pack(padx = 10, pady = 10)
        try:
            # ignore this error
            for i in range(0, 2):
                root.after_cancel(signal_viewer[i].run_job)
                signal_viewer[i].pack_forget()
                signal_viewer[i].destroy()
        except:
            pass
        
        for i in range(0, 2):
            serial_queue[i] = Queue()
        
        serial_reader.restart()
        
        for i in range(0, 2):
            signal_viewer[i] = signalViewer(acquireFrame, channel_id = i)
            signal_viewer[i].pack(side = LEFT)

def on_exit():
    if tkMessageBox.askokcancel('', 'Are you sure you want to exit?'):
        root.destroy()
        root.quit()

root = Tk()
root.title("Signal Time - Frequency Plotter")
root.configure(background = "gray25")
ttk.Style().theme_use('alt')
ttk.Style().configure(root, background = "gray25")

plotterFrame = Frame(root, width = 1100, height = 500, background = "gray25")
plotterFrame.pack_propagate(0)
plotterFrame.pack(padx = 10, pady = (0, 10))

ser = serial.Serial()
ser.port = 'COM1'
ser.baudrate = 115200

serial_reader = EEGReader(root, out_file = False)
serial_reader.pack()

try:
    restart_serial()
except:
    pass

signal_plotter = control_panel(plotterFrame)
signal_plotter.pack()
signal_plotter.print("[INFO] EEG Logger Module")
signal_plotter.print("[INFO] System initialized successfully.")

root.bind("<Key>", signal_plotter.onKeyPress)
root.protocol("WM_DELETE_WINDOW", on_exit)
root.mainloop()
