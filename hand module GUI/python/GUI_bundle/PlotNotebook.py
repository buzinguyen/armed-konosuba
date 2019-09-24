import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import csv
import Tkinter
from Tkinter import *
import ttk
import datetime
import time
from string import ascii_letters, digits, punctuation, join
from ConfigureTab import configure_tab
import tkFileDialog
import Tkinter as tk
matplotlib.use('TkAgg')

##################################################
# Tkinter root <- GUIPlot class as a frame <- plotter class <- single plot class
# GUIPlot is a class acts a Frame on Tkinter, pass data from Tkinter to plotter class
# plotter is a class used to manage all the plots shown, a plotter has multple singlePlot objects
# singlePlot defines parameter of a single plot, holds x, y data, filter data, name etc
# ---- CAN UNDERSTAND AS GUIPlot is a frame that implements plotter and work on a plotter object and plotter implements pyplot from matplotlib
# ################################################ 

class singlePlot:
    def __init__ (self):
        self.arrayX = []
        self.arrayY = []
        self.limA = 0
        self.limB = 0
        self.name = ''
        self.index = 1 # in subplot, index must be higher than 0, eg. 211 <- index = 1, 212 <- index = 2
        self.legend = ''
        self.type = 'sensor'
        self.parent = None
    
    def getX(self):
        if(self.limA != 0 and self.limB != 0):
            return self.arrayX[self.limA:self.limB]
        elif(self.limA != 0):
            return self.arrayX[self.limA:]
        elif(self.limB != 0):
            return self.arrayX[:self.limB]
        else:
            return self.arrayX

    def getY(self):
        if(self.limA != 0 and self.limB != 0):
            return self.arrayY[self.limA:self.limB]
        elif(self.limA != 0):
            return self.arrayY[self.limA:]
        elif(self.limB != 0):
            return self.arrayY[:self.limB]
        else:
            return self.arrayY
    
    def getCustomX(self, a, b):
        return self.arrayX[a:b]

    def getCustomY(self, a, b): 
        return self.arrayY[a:b]
    
    def setX(self, array):
        self.arrayX = array
    
    def setY(self, array):
        self.arrayY = array
    
    def setLimA(self, lim):
        self.limA = lim
    
    def setLimB(self, lim):
        self.limB = lim
    
    def setName(self, name):
        self.name = name
    
    def shiftPlot(self, value):
        self.limA = self.limA + value
        self.limB = self.limB + value
    
    def getName(self):
        return self.name

    def setIndex(self, index):
        self.index = index
    
    def getIndex(self):
        return self.index
    
    def setLegend(self, legend):
        self.legend = legend

    def getLegend(self):
        return self.legend
    
    def setType(self, type):
        self.type = type
    
    def getType(self):
        return self.type
    
    def getParent(self):
        return self.parent
    
    def setParent(self, parent):
        self.parent = parent

class plotter:
    def __init__(self, id):
        self.ID = int(id)
        self.plotArray = []
        self.figure = plt.figure(num = self.ID, figsize=(15,8))
        self.scatterSize = 1
        self.xlimA = 0
        self.xlimB = 0
        self.method = 'scatter'
        self.handler = plt.text(0, 0, '') # show info of the datapoint when left click
        self.cursor = [] # holds the vertical cursors when moving mouse
        self.xCursor = None # the horizontal cursor when right click
        self.marker = None # the circle to indicate where is the last left click position
        self.filterHandler = {
            'counter': 0,
            'A': 0,
            'B': 0,
            'cursorA': [],
            'cursorB': []
        }
        self.zoomConstant = 10000000

    def setMethod(self, method):
        if method == 'line':
            self.method = 'line'
        elif method == 'scatter':
            self.method = 'scatter'
    
    def saveFigureAsImage(self, name = 'figure'):
        plt.figure(self.ID)
        plt.savefig("{}.png".format(name))
        
    def plotLine(self):
        plt.clf()
        plt.figure(self.ID)
        indexList = []
        for i in range(0, len(self.plotArray)):
            indexList.append(self.plotArray[i].getIndex())
        subplotNum = len(set(indexList))
        for i in range(0, len(self.plotArray)):
            plt.subplot(subplotNum, 1, self.plotArray[i].getIndex())
            plt.plot(self.plotArray[i].getX(), self.plotArray[i].getY(), label = self.plotArray[i].getLegend())
            #plt.title(self.plotArray[i].getName())
            plt.legend(loc = 'best', ncol = 2, mode = 'expand', shadow = True, fancybox = True)
            
            if(self.plotArray[i].getType() == 'gateway'):
                plt.yticks([-2, -1, 0, 1, 2], ("", "", "Offline", "Online", ""))
            
            axisTime = []
            for i in np.linspace(self.xlimA, self.xlimB, 4):
                axisTime.append(self.unixToTime(int(i)))
            plt.xticks(np.linspace(self.xlimA, self.xlimB, 4), axisTime) 
            
            if(self.xlimA != 0 and self.xlimB != 0):
                plt.xlim(self.xlimA, self.xlimB)
            elif(self.xlimA != 0):
                plt.xlim(self.xlimA)
            elif(self.xlimB != 0):
                plt.xlim(self.xlimB)
        try:
            plt.tight_layout()
        except ValueError:
            pass
        #plt.subplots_adjust(hspace = 0.5)
        self.cursor = []
    
    def plotScatter(self):
        plt.clf()
        plt.figure(self.ID)
        indexList = []
        for i in range(0, len(self.plotArray)):
            indexList.append(self.plotArray[i].getIndex())
        subplotNum = len(set(indexList))
        for i in range(0, len(self.plotArray)):
            plt.subplot(subplotNum, 1, self.plotArray[i].getIndex())
            plt.scatter(self.plotArray[i].getX(), self.plotArray[i].getY(), s = self.scatterSize, label = self.plotArray[i].getLegend())
            #plt.title(self.plotArray[i].getName())
            plt.legend(loc = 'best', ncol = 2, mode = 'expand', shadow = True, fancybox = True)
            
            if(self.plotArray[i].getType() == 'gateway'):
                plt.yticks([-1, 0, 1, 2], ("", "Offline", "Online", ""))
            
            axisTime = []
            for i in np.linspace(self.xlimA, self.xlimB, 4):
                axisTime.append(self.unixToTime(int(i)))
            plt.xticks(np.linspace(self.xlimA, self.xlimB, 4), axisTime) 
            
            if(self.xlimA != 0 and self.xlimB != 0):
                plt.xlim(self.xlimA, self.xlimB)
            elif(self.xlimA != 0):
                plt.xlim(self.xlimA)
            elif(self.xlimB != 0):
                plt.xlim(self.xlimB)
        try:
            plt.tight_layout()
        except ValueError:
            pass
        #plt.subplots_adjust(hspace = 0.5)
        self.cursor = []
    
    def setScatterSize(self, size):
        self.scatterSize = size

    def addPlot(self, plot):
        self.plotArray.append(plot)
        self.plotScatter()
    
    def getFigure(self):
        return self.figure
    
    def removePlot(self, index):
        newPlotArray = []
        for plot in self.plotArray:
            if plot.getIndex() != index:
                if(plot.getIndex() > index):
                    plot.setIndex(plot.getIndex()-1)
                newPlotArray.append(plot)
        self.plotArray = newPlotArray[:]
        self.plotScatter()
    
    def shiftPlot(self, value):
        for i in range (0, len(self.plotArray)):
            self.plotArray[i-1].shiftPlot(value)
        self.plotScatter()
    
    def setFilter(self, xlimA, xlimB):
        plt.figure(self.ID)
        self.xlimA = xlimA
        self.xlimB = xlimB
        axisTime = []
        for i in np.linspace(self.xlimA, self.xlimB, 4):
            axisTime.append(self.unixToTime(int(i)))

        indexList = []
        for i in range(0, len(self.plotArray)):
            indexList.append(self.plotArray[i].getIndex())
        subplotNum = len(set(indexList))

        for i in range(1, subplotNum + 1):
            plt.subplot(subplotNum, 1, i)
            plt.xlim(self.xlimA, self.xlimB)
            plt.xticks(np.linspace(self.xlimA, self.xlimB, 4), axisTime)

    def getFilter(self):
        return {'A': self.xlimA, 'B': self.xlimB} 
    
    def refresh(self):
        if self.method == 'line':
            self.plotLine()
        elif self.method == 'scatter':
            self.plotScatter()
    
    def getPlotList(self):
        plotList = []
        indexList = []
        for i in range(0, len(self.plotArray)):
            indexList.append(self.plotArray[i].getIndex())

        for index in set(indexList):
            current = []
            current.append(index)
            for plot in self.plotArray:
                if plot.getIndex() == index:
                    current.append(plot)
            plotList.append(current)
        return plotList
    
    def getPlotCount(self):
        indexList = []
        for i in range(0, len(self.plotArray)):
            indexList.append(self.plotArray[i].getIndex())
        subplotNum = len(set(indexList))
        return subplotNum
    
    def eventHandler(self, event):
        # Left click to show data info at the point
        # Right click to show vertical line at the mouse cursor
        # middle click to set filter A, another one to set filter B and the final click to set filter
        plt.figure(self.ID)
        eventstring = '%s, %d, %d, %d, %f, %f' % ('double' if event.dblclick else 'single', event.button, event.x, event.y, event.xdata, event.ydata)
        eventArray = eventstring.split(",")
        mouseY = 750 - int(eventArray[3])
        plotCount = self.getPlotCount()
        thresholdY = 750.0/plotCount
        eventOnPlot = int(float(mouseY)/thresholdY) + 1
        plt.subplot(plotCount, 1, eventOnPlot)

        if int(eventArray[1]) == 1:
            #self.handler.set_visible(False)
            try:
                self.marker.remove()
                self.handler.remove()
            except AttributeError:
                pass
            except ValueError:
                pass
            except IndexError:
                pass
            finally:
                pass
            self.handler = plt.text(float(eventArray[4]), float(eventArray[5]), "X: {}  Y: {}".format(self.unixToTime(eventArray[4]), int(float(eventArray[5]))))
            self.marker = plt.scatter(float(eventArray[4]), float(eventArray[5]), s = 20, color = 'red')

        elif int(eventArray[1]) == 3:
            try:
                self.xCursor.pop(0).remove()
            except IndexError:
                pass
            except AttributeError:
                pass
            except ValueError:
                pass
            finally:
                pass
            plt.autoscale(False)
            self.xCursor = plt.plot([self.xlimA, self.xlimB], [float(eventArray[5]), float(eventArray[5])], color = 'green', ls = '--')
        
        elif int(eventArray[1]) == 2:
            if self.filterHandler['counter'] == 0:
                self.filterHandler['A'] = int(float(eventArray[4]))
                self.drawCursor(event, type = 'filter')
                self.filterHandler['counter']+=1
            elif self.filterHandler['counter'] == 1:
                self.filterHandler['B'] = int(float(eventArray[4]))
                self.drawCursor(event, type = 'filter')
                self.filterHandler['counter']+=1
            elif self.filterHandler['counter'] == 2:
                self.drawCursor(event, type = 'filter')
                self.filterHandler['counter'] = 0
                self.setFilter(self.filterHandler['A'], self.filterHandler['B'])

    def unixToTime(self, timestamp):
        return datetime.datetime.fromtimestamp(int(float(timestamp)/1000.0)).strftime('%Y-%m-%d %H:%M:%S')
    
    def drawCursor(self, event, type = 'cursor'):
        plt.figure(self.ID)
        indexList = []
        for i in range(0, len(self.plotArray)):
            indexList.append(self.plotArray[i].getIndex())
        subplotNum = len(set(indexList))

        try:
            for i in range(1, subplotNum + 1):
                plt.subplot(subplotNum, 1, i)
                self.cursor.pop(0).pop(0).remove()
                if self.filterHandler['counter'] == 2 and type == 'filter':
                    self.filterHandler['cursorA'].pop(0).pop(0).remove()
                    self.filterHandler['cursorB'].pop(0).pop(0).remove()
            self.xCursor.pop(0).remove()
        except IndexError:
            pass
        except AttributeError:
            pass
        except ValueError:
            pass
        finally:
            pass
            
        for i in range(1, subplotNum + 1):
            plt.subplot(subplotNum, 1, i)
            plt.autoscale(False)
            if type == 'cursor':
                self.cursor.append(plt.plot([event.xdata, event.xdata], plt.gca().get_ylim(), color='green', ls = '--'))
            elif type == 'filter':
                if self.filterHandler['counter'] == 0:
                    self.filterHandler['cursorA'].append(plt.plot([event.xdata, event.xdata], plt.gca().get_ylim(), color='yellow', ls = '-.'))
                elif self.filterHandler['counter'] == 1:
                    self.filterHandler['cursorB'].append(plt.plot([event.xdata, event.xdata], plt.gca().get_ylim(), color='yellow', ls = '-.'))
    
    def setZoomConstant(self, constant):
        self.zoomConstant = constant

    def zoom(self, event):
        plt.figure(self.ID)
        if self.xlimB - self.xlimA > 2*event.step*self.zoomConstant:
            self.xlimA += (event.step * self.zoomConstant)
            self.xlimB -= (event.step * self.zoomConstant)
            self.setFilter(self.xlimA, self.xlimB)

class GUIPlot(Frame):
    def __init__(self, master, id):
        Frame.__init__(self, master)
        self.ID = id
        self.plot = plotter(self.ID)
        self.canvas = FigureCanvasTkAgg(self.plot.getFigure(), self)
        self.canvas.mpl_connect('button_press_event', self.onclick)
        self.canvas.mpl_connect('motion_notify_event', self.onMouseMoveCursor)
        self.canvas.mpl_connect('scroll_event', self.onMouseScroll)
        self.canvas.mpl_connect('axes_enter_event', self.onFocus)
        self.canvas.get_tk_widget().pack()
        self.canvas.show()
    
    def onFocus(self, event):
        self.focus_set()
    
    def onMouseMoveCursor(self, event):
        self.plot.drawCursor(event)
        self.canvas.draw()
        #print("Mouse position: (%s %s)" % (event.x, event.y))
        #return
    
    def onMouseScroll(self, event):
        self.plot.zoom(event)
        self.canvas.draw()

    def getID(self):
        return self.ID

    def addPlot(self, plot):
        self.plot.addPlot(plot)

    def removePlot(self, index):
        self.plot.removePlot(index)

    def redraw(self):
        #self.canvas.draw_idle()
        self.canvas.draw()
    
    def shiftPlot(self, value):
        self.plot.shiftPlot(value)

    def setScatterSize(self, size):
        self.plot.setScatterSize(size)
    
    def setFilter(self, xlimA, xlimB):
        self.plot.setFilter(xlimA, xlimB)
    
    def getFilter(self):
        return self.plot.getFilter()
    
    def setMethod(self, method):
        self.plot.setMethod(method)
    
    def refresh(self):
        self.plot.refresh()
        #self.canvas.draw_idle()
        self.canvas.draw()
    
    def getPlotList(self):
        return self.plot.getPlotList()
    
    def getPlotCount(self):
        return self.plot.getPlotCount()
    
    def saveFigureAsImage(self, name = 'figure'):
        self.plot.saveFigureAsImage(name)
    
    def onclick(self, event):
        #print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #  ('double' if event.dblclick else 'single', event.button,
        #   event.x, event.y, event.xdata, event.ydata))
        try:
            #self.plot.eventHandler('%s, %d, %d, %d, %f, %f' % 
            #    ('double' if event.dblclick else 'single', event.button,
            #    event.x, event.y, event.xdata, event.ydata))
            self.plot.eventHandler(event)
            self.canvas.draw()
        except TypeError:
            pass
        except ZeroDivisionError:
            pass 
        finally:
            pass

class timePicker(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        self.year = StringVar(master)
        self.year.set("----")
        self.month = StringVar(master)
        self.month.set("--")
        self.day = StringVar(master)
        self.day.set("--")
        self.hour = StringVar(master)
        self.hour.set("-")
        self.minute = StringVar(master)
        self.minute.set("--")
        self.invokeVar = False
        
        self.yearArray = [x for x in range(2017, 2019)]
        self.monthArray = [x for x in range(1, 13)]
        self.dayArray = [x for x in range(1, 32)]
        self.hourArray = [x for x in range(0, 24)]
        self.minuteArray = ["%02d" % x for x in range(0, 60)]

        self.yearMenu = ttk.Combobox(master, textvariable = self.year, values = self.yearArray, width = 4, postcommand = self.invoke)
        yearLabel = Label(master, text = "Year")
        self.monthMenu = ttk.Combobox(master, textvariable = self.month, values = self.monthArray, width = 2, postcommand = self.invoke)
        monthLabel = Label(master, text = "Month")
        self.dayMenu = ttk.Combobox(master, textvariable = self.day, values = self.dayArray, width = 2, postcommand = self.invoke)
        dayLabel = Label(master, text = "Day")
        self.hourMenu = ttk.Combobox(master, textvariable = self.hour, values = self.hourArray, width = 2, postcommand = self.invoke)
        hourLabel = Label(master, text = "Hour")
        self.minuteMenu = ttk.Combobox(master, textvariable = self.minute, values = self.minuteArray, width = 2, postcommand = self.invoke)
        minuteLabel = Label(master, text = "Minute")

        self.label = Label(master, text = "Time Widget")
        self.label.grid(row = 0, columnspan = 5, sticky = 'w')
        yearLabel.grid(row = 1, column = 0, sticky = 'w')
        self.yearMenu.grid(row = 2, column = 0)
        monthLabel.grid(row = 1, column = 1, sticky = 'w')
        self.monthMenu.grid(row = 2, column = 1)
        dayLabel.grid(row = 1, column = 2, sticky = 'w')
        self.dayMenu.grid(row = 2, column = 2)
        hourLabel.grid(row = 1, column = 3, sticky = 'w')
        self.hourMenu.grid(row = 2, column = 3)
        minuteLabel.grid(row = 1, column = 4, sticky = 'w')
        self.minuteMenu.grid(row = 2, column = 4)
    
    def invoke(self):
        self.invokeVar = True

    def getYear(self):
        return self.year.get()
    
    def getMonth(self):
        return self.month.get()
    
    def getDay(self):
        return self.day.get()
    
    def getHour(self):
        return self.hour.get()
    
    def getMinute(self):
        return self.minute.get()
    
    def getTimestamp(self):
        print("Write timestamp function here")
        return 0

    def checkValue(self):
        if(self.year.get() == '----'):
            return False
        if(self.month.get() == '--'):
            return False
        if(self.day.get() == '--'):
            return False
        if(self.hour.get() == '-'):
            return False
        if(self.minute.get() == '--'):
            return False
        return True

    def get(self):
        if(self.invokeVar or self.checkValue()):
            if(int(self.hour.get()) >= 12):
                if(int(self.hour.get()) == 12):
                    hourVal = 12
                else:
                    hourVal =  int(self.hour.get())%12
                timestring = "{}/{}/{} {}:{} PM".format(self.month.get(), self.day.get(), self.year.get(), hourVal, self.minute.get())
            else:
                if(int(self.hour.get()) == 0):
                    hourVal = 12
                else:
                    hourVal = self.hour.get()
                timestring = "{}/{}/{} {}:{} AM".format(self.month.get(), self.day.get(), self.year.get(), hourVal, self.minute.get())
        else:
            timestring = ''
        return timestring
    
    def setLabel(self, label):
        self.label.configure(text = label)

class SyntaxHighlightingText(Text):
    tags = {'good': 'green4',
            'bad': 'red',
            'key': 'blue',
            'int': 'gold4',
            'report': 'cyan4'}

    def __init__(self, master):
        Text.__init__(self, master)
        self.config_tags()
        self.characters = ascii_letters + digits + punctuation
        self.keywordList = ['[INFO]', '[WARN]', '[REPORT]']
        self.reportKey = ['Name', 'Gateway', 'Host', 'Location', 'Start_Time', 'Stop_Time', 'Packet_Count', 'Average', 'Percentage']
        self.line = 1
        for tag in self.tags.keys():
            self.tag_config(tag, font = "Helvetica 8 bold")

    def config_tags(self):
        for tag, val in self.tags.items():
            self.tag_config(tag, foreground=val)

    def remove_tags(self, start, end):
        for tag in self.tags.keys():
            self.tag_remove(tag, start, end)
    
    def deleteAll(self):
        self.delete(1.0, END)
        self.line = 1

    def key_press(self, buffer):
        tokenized = buffer.split(' ')
        cline = self.line
        self.remove_tags('%s.%d'%(cline, 0), '%s.%d'%(cline, len(buffer)))

        start, end = 0, 0
        for token in tokenized:
            end = start + len(token)
            if token in self.keywordList:
                if token == '[INFO]' or token == '[REPORT]':
                    self.tag_add('good', '%s.%d'%(cline, start), '%s.%d'%(cline, end))
                elif token == '[WARN]':
                    self.tag_add('bad', '%s.%d'%(cline, start), '%s.%d'%(cline, end))
            elif token in self.reportKey:
                self.tag_add('report', '%s.%d'%(cline, start), '%s.%d'%(cline, end))
            elif bool("GW" in token) or bool("TH" in token) or bool("SR" in token) or bool("CO2" in token):
                self.tag_add('key', '%s.%d'%(cline, start), '%s.%d'%(cline, end))
            elif bool("/" in token):
                self.tag_add('key', '%s.%d'%(cline, start), '%s.%d'%(cline, end))
            else:
                try:
                    int(token)
                except ValueError:
                    pass
                else:
                    self.tag_add('int', '%s.%d'%(cline, start), '%s.%d'%(cline, end))

            start += len(token)+1
        self.line += 1

class PlotNotebook(ttk.Notebook):
    """A ttk Notebook with close buttons on each tab"""

    __initialized = False

    def __init__(self, *args, **kwargs):
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__inititialized = True

        kwargs["style"] = "CustomNotebook"
        ttk.Notebook.__init__(self, *args, **kwargs)

        self._active = None

        self.tabArray = []
        self.tabArray.append(GUIPlot(self, '0'))
        self.add(self.tabArray[-1], text = "Note 0")
        self.tabArray.append(GUIPlot(self, '1'))
        self.add(self.tabArray[-1], text = "New")

        self.funcID = self.tabArray[-1].bind("<Visibility>", self.on_create_new_tab)
        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)
        self.bind("<<NotebookTabChanged>>", self.on_notebook_tab_changed)
        self.tabCounter = 1
        self.currentApp = self.tabArray[0]

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""

        element = self.identify(event.x, event.y)

        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            if index < (len(self.tabArray)-1) and len(self.tabArray) > 2:
                self.state(['pressed'])
                self._active = index
            else: 
                return

    def on_close_release(self, event):
        """Called when the button is released over the close button"""
        if not self.instate(['pressed']):
            return

        element =  self.identify(event.x, event.y)
        index = self.index("@%d,%d" % (event.x, event.y))

        if "close" in element and self._active == index and index < (len(self.tabArray)-1) and len(self.tabArray) > 2:
            self.forget(index)
            self.tabArray.pop(index)
            if index > 0:
                self.select(index - 1)
            self.event_generate("<<NotebookTabClosed>>")

        self.state(["!pressed"])
        self._active = None
    
    def on_create_new_tab(self, event):
        self.tabArray[-1].unbind("<Visibility>", self.funcID)
        name = "Note {}".format(self.tabCounter)
        self.tab(self.tabArray[-1], text = name)
        self.tabCounter+=1 
        self.tabArray.append(GUIPlot(self, self.tabCounter))
        self.add(self.tabArray[-1], text = "New")
        self.funcID = self.tabArray[-1].bind("<Visibility>", self.on_create_new_tab)
    
    def getTab(self):
        return self.tabArray[self.index(self.select())]

    def on_notebook_tab_changed(self, event):
        self.currentApp = self.tabArray[self.index(self.select())]

    def __initialize_custom_style(self):
        style = ttk.Style()
        self.images = (
            tk.PhotoImage("img_close", data='''
                R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
                '''),
            tk.PhotoImage("img_closeactive", data='''
                R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
                AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
                '''),
            tk.PhotoImage("img_closepressed", data='''
                R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
            ''')
        )

        style.element_create("close", "image", "img_close",
                            ("active", "pressed", "!disabled", "img_closepressed"),
                            ("active", "!disabled", "img_closeactive"), border=8, sticky='')
        style.layout("CustomNotebook", [("CustomNotebook.client", {"sticky": "nswe"})])
        style.layout("CustomNotebook.Tab", [
            ("CustomNotebook.tab", {
                "sticky": "nswe", 
                "children": [
                    ("CustomNotebook.padding", {
                        "side": "top", 
                        "sticky": "nswe",
                        "children": [
                            ("CustomNotebook.focus", {
                                "side": "top", 
                                "sticky": "nswe",
                                "children": [
                                    ("CustomNotebook.label", {"side": "left", "sticky": ''}),
                                    ("CustomNotebook.close", {"side": "left", "sticky": ''}),
                                ]
                        })
                    ]
                })
            ]
        })
    ])