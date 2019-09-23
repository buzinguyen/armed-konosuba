from Tkinter import *
import ttk
import tkFileDialog
import time
import datetime
from ConfigureTab import configure_tab
from PlotNotebook import singlePlot, plotter, GUIPlot, SyntaxHighlightingText, PlotNotebook, timePicker
from DataLogger import GWSensorLogger, GatewayStatusLogger
from DataReport import sensorReport
from IntentText import TextWithIndentation
import os
import sys

#########################################################################
#### FUNCTION USED ON MAINLOOP TO INTERACT WITH GUIPlot OBJECT
#########################################################################
def addPlotToCanvas(plot):
    global plotNotebook
    plotNotebook.currentApp.addPlot(plot)
    plotNotebook.currentApp.redraw()

def getPlotGroupIndex():
    global plotListVar
    groupString = plotListVar.get()
    plotGroup = groupString.split(" - ")
    index = int(plotGroup[0][-2:].replace(' ','0'))
    return index

def removePlotInCanvas():
    global plotListVar, plotNotebook
    echo("[INFO] {} is deleted.".format(plotListVar.get()))
    if plotListVar.get() != "New":
        index = getPlotGroupIndex()
        plotNotebook.currentApp.removePlot(index)
        plotNotebook.currentApp.redraw()
        updatePlotList()

def removeAllPlotInCanvas():
    global plotNotebook
    echo("[INFO] All plots are removed from canvas.")
    counter = plotNotebook.currentApp.getPlotCount()
    for plot in range(0, counter):
        plotNotebook.currentApp.removePlot(1)
    plotNotebook.currentApp.redraw()
    updatePlotList()

def timeToUnix(array):
    newArray = []
    for data in array:
        newArray.append(int(str(int(time.mktime(datetime.datetime.strptime(data, "%m/%d/%Y %I:%M %p").timetuple())))+"000"))
    return newArray

def setScatterSize(size):
    global plotNotebook
    plotNotebook.currentApp.setScatterSize(size)
    plotNotebook.currentApp.redraw()
    echo("[INFO] Scatter size is changed to {} .".format(size))

def setMethod(method):
    global plotNotebook
    plotNotebook.currentApp.setMethod(method)
    plotNotebook.currentApp.redraw()
    echo("[INFO] Change viewing method to {}.".format(method))

def syncGlobalFilter(filA, filB):
    global filterA, filterB, plotNotebook, startTimeEntry, stopTimeEntry
    if startTimeEntry.get() != '':
        filterA = int(timeToUnix([startTimeEntry.get()])[0])
    elif filA != filterA:
        filterA = filA
    if stopTimeEntry.get() != '':
        filterB = int(timeToUnix([stopTimeEntry.get()])[0])
    elif filB != filterB:
        filterB = filB
    if filterA != 0 and filterB != 0:
        plotNotebook.currentApp.setFilter(filterA, filterB)
        echo("[INFO] New filter value is set.")

def plotSingleSensor():
    global GWSensorFile, GWStatusFile, gatewayVar, sensorVar, filterA, filterB, plotListVar, plotNotebook
    try:
        plot = singlePlot()
        data = GWSensorFile.getDataArray(gatewayVar.get(), sensorVar.get())
        plot.setParent(gatewayVar.get())
        plot.setX(data['time'])
        plot.setY(data['value'])
        plot.setName("Sensor {} ({}) Data Plotter".format(sensorVar.get(), gatewayVar.get()))
        plot.setLegend(sensorVar.get())
        syncGlobalFilter(min(data['time']), max(data['time']))
        if plotListVar.get() != "New":
            index = getPlotGroupIndex()
            plot.setIndex(index)
        else:
            plot.setIndex(plotNotebook.currentApp.getPlotCount()+1)
        addPlotToCanvas(plot)
        echo("[INFO] Sensor {} data is plotted.".format(sensorVar.get()))
    except IndexError:
        pass
        echo("[WARN] Choose a sensor before plotting single (or user 'Plot All' to plot all sensors allocated with this gateway).")

def plotGatewayStatus():
    global GWSensorFile, GWStatusFile, gatewayVar, sensorVar, filterA, filterB, plotListVar, plotNotebook
    try:
        plot = singlePlot()
        data = GWStatusFile.getDataArray(gatewayVar.get())
        timeArray = timeToUnix(GWStatusFile.getHeader()[1:])
        statusArray = list(data.iloc[0])[1:]
        plot.setX(timeArray)
        plot.setName("Gateway {} Status Plotter".format(gatewayVar.get()))
        plot.setLegend(gatewayVar.get())
        statusValueArray = []
        for x in statusArray:
            if x == "Online":
                statusValueArray.append(1)
            else:
                statusValueArray.append(0)
        plot.setY(statusValueArray)
        plot.setType('gateway')
        syncGlobalFilter(min(timeArray), max(timeArray))
        if plotListVar.get() != "New":
            index = getPlotGroupIndex()
            plot.setIndex(index)
        else:
            plot.setIndex(plotNotebook.currentApp.getPlotCount()+1)
        addPlotToCanvas(plot)
        echo("[INFO] Gateway {} status is plotted.".format(gatewayVar.get()))
    except IndexError:
        pass
        echo("[WARN] Choose a gateway before plotting gateway status.")

def plotAllSensors():
    global GWSensorFile, GWStatusFile, gatewayVar, sensorVar
    echo("[INFO] All sensors are plotted.")
    for i in GWSensorFile.getSensorList(gatewayVar.get()):
        sensorVar.set(i)
        plotSingleSensor()

def refresh():
    global filterA, filterB, plotNotebook
    syncGlobalFilter(filterA, filterB)
    plotNotebook.currentApp.refresh()

################################################################
def postSysStartHierarchy():
    global currentDir
    gatewayPath = os.path.abspath("gateway.csv").replace("\\","/")
    sensorPath = os.path.abspath("sensor.csv").replace("\\","/")
    initLogFiles(gatewayPath, sensorPath)
    echo("[INFO] No filter is applied.")
    echo("[INFO] Default plot view is 'scatter'.")
    echo("[INFO] Default step size is 500000 .")
    echo("[INFO] System initialized on {}".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    echo("[INFO] Current directory is {}".format(currentDir.replace("\\","/")))

def initSystem():
    global licenseData
    fd = open("license.md", "rb")
    licenseData = fd.read()
    fd.close()

def initLogFiles(gatewayPath = None, sensorPath = None):
    global initList, GWSensorGroup, gatewayList, GWStatusFile, GWSensorFile
    echo("[INFO] Try getting init information from log file.")
    try:
        GWSensorFile = GWSensorLogger(sensorPath)
        GWSensorGroup = GWSensorFile.getGroup()
        gatewayList = GWSensorGroup.keys()
        gatewayList.sort()
        initList = GWSensorFile.getInitList()
    except IOError as e:
        echo("[WARN] Cannot find default file for sensor file. Please manually assign a file in configure tab.")
    
    echo("[INFO] Done, try getting gateway status list.")
    try:
        GWStatusFile = GatewayStatusLogger(gatewayPath)
    except IOError as e:
        echo("[WARN] Cannot find default file for gateway file. Please manually assign a file in configure tab.")
    
    echo("[INFO] Done, module is initialized.")
    gatewayMenu['values'] = gatewayList

def changeGateway():
    global sensorVar
    sensorVar.set("Select")
    sensorMenu['values'] = ["Select"]

def updateSensorList():
    global gatewayVar, sensorVar
    try:
        sensorList = GWSensorGroup[gatewayVar.get()]
        sensorMenu['values'] = sensorList
        sensorVar.set("Select")
    except KeyError as e:
        pass
    finally:
        pass

def updatePlotList():
    global plotNotebook, plotListVar
    try:
        plotList = []
        plotGroup = plotNotebook.currentApp.getPlotList()
        for group in plotGroup:
            groupList = []
            plotIndex = group.pop(0)
            for plot in group:
                groupList.append(plot.getLegend())
            namestring = str([x for x in groupList]).replace(",", " and")
            namestring = namestring.replace("[","")
            namestring = namestring.replace("]","")
            namestring = namestring.replace("'","")
            plotInstance = "Plot {} - {}".format(plotIndex, namestring)
            plotList.append(plotInstance)
        plotList.append("New")
        plotMenu['values'] = plotList
        plotListVar.set("New")
    except KeyError as e:
        pass
    finally:
        pass

def shiftPlotLeft():
    global filterA, filterB, filterStep, plotNotebook
    currentFilter = plotNotebook.currentApp.getFilter()
    filA = currentFilter['A']
    filB = currentFilter['B']
    if filA != filterA:
        filterA = filA
    if filB != filterB:
        filterB = filB
    filterA = filterA - filterStep
    filterB = filterB - filterStep
    plotNotebook.currentApp.setFilter(filterA, filterB)
    plotNotebook.currentApp.redraw()

def shiftPlotRight():
    global plotNotebook, filterA, filterB, filterStep
    currentFilter = plotNotebook.currentApp.getFilter()
    filA = currentFilter['A']
    filB = currentFilter['B']
    if filA != filterA:
        filterA = filA
    if filB != filterB:
        filterB = filB
    filterA = filterA + filterStep
    filterB = filterB + filterStep
    plotNotebook.currentApp.setFilter(filterA, filterB)
    plotNotebook.currentApp.redraw()

def echo(infoString):
    infoText.config(state = NORMAL)
    infoText.insert(END, "{}\n".format(infoString))
    infoText.config(state = DISABLED)
    infoText.key_press(infoString)
    infoText.see("end")

def updateConfiguration():
    global plotConfigObject, fileConfigObject, moveStepConfigObject, filterStep, plotNotebook, GWSensorFile, GWStatusFile
    updatePlot = plotConfigObject.output()
    updateFile = fileConfigObject.output()
    updateMoveStep = moveStepConfigObject.output()
    changes = False

    try:
        if GWSensorFile.path != updateFile['Sensor File'] or GWStatusFile.path != updateFile['Gateway File']:
            initLogFiles(gatewayPath = updateFile['Gateway File'], sensorPath = updateFile['Sensor File'])
            echo("[INFO] New log files are set.")
            changes = True
    except AttributeError:
        if os.path.isfile(updateFile['Gateway File']) and os.path.isfile(updateFile['Sensor File']):
            initLogFiles(gatewayPath = updateFile['Gateway File'], sensorPath = updateFile['Sensor File'])
            echo("[INFO] New log files are set.")
            changes = True
        else:
            echo("[WARN] Log files are not valid. Please choose another file.")
        pass

    if int(plotNotebook.currentApp.plot.scatterSize) != int(updatePlot['Scatter Size']):
        setScatterSize(int(updatePlot['Scatter Size']))
        changes = True
    
    if plotNotebook.currentApp.plot.method != updatePlot['Plot Method']:
        setMethod(updatePlot['Plot Method'])
        changes = True
    
    moveStepMethod = updateMoveStep['Move Step Size']
    if moveStepMethod != "custom":
        stepSet = {
            "10 minutes": 600000, 
            "30 minutes": 1800000,
            "1 hour": 3600000, 
            "3 hours": 10800000, 
            "6 hours": 21600000, 
            "12 hours": 43200000, 
            "1 day": 86400000, 
            "3 days": 259200000
        }
        newFilterStep = stepSet[moveStepMethod]
        if int(newFilterStep) != int(filterStep):
            filterStep = newFilterStep
            echo("[INFO] New step size of {} is set.".format(moveStepMethod))
            changes = True
    else:
        newFilterStep = int(updateMoveStep['Custom Step'])
        if int(newFilterStep) != int(filterStep):
            filterStep = newFilterStep
            echo("[INFO] New step size of {} is set.".format(filterStep))
            changes = True

    # uncomment to set the zoom constant of mouse wheel based on the filterStep value
    #plotNotebook.currentApp.plot.setZoomConstant(filterStep)

    if changes:
        refresh()
    else:
        echo("[INFO] No changes made.")

def onConfigTabSwitch(event):
    # this function is currently a redundancy, write something in the update() function or delete this
    global plotConfigObject, fileConfigObject, moveStepConfigObject
    plotConfigObject.update()
    fileConfigObject.update()
    moveStepConfigObject.update()
    ##
    if moveStepConfigObject.output()['Move Step Size'] != 'custom':
        moveStepConfigObject.disable_instance('Custom Step')
    else:
        moveStepConfigObject.enable_instance('Custom Step')

def askForFile(name):
    global fileConfigObject, GWSensorFile, GWStatusFile, gatewayVar, sensorVar
    filename = tkFileDialog.askopenfilename(initialdir = "/",title = "Select {}".format(name),filetypes = (("log files","*.csv"),("all files","*.*")))
    if filename != None and filename != '':
        fileConfigObject.set_value(name, filename)
        if name == "Gateway File":
            try:
                GWStatusFile.setPath(filename)
            except AttributeError:
                pass
            gatewayVar.set("Select")
            echo("[INFO] {} is used as gateway log file.".format(filename))
        elif name == "Sensor File":
            try:
                GWSensorFile.setPath(filename)
            except AttributeError:
                pass
            sensorVar.set("Select")
            echo("[INFO] {} is used as new sensor log file.".format(filename))

def onClickGenerateReport():
    def reportLine(string):
        reportText.insert(END, "{}\n".format(string))
        reportText.key_press(string)
    
    def sensorReportAdapter(dict):
        generalItem = ['Name', 'Gateway', 'Host', 'Location', 'Start_Time', 'Stop_Time', 'Packet_Count', 'Average']
        dailyItem = ['Start_Time', 'Stop_Time', 'Packet_Count', 'Average', 'Percentage']
        generalDict = dict['General']
        dailyDict = dict['Detail']
        reportLine("    ************** NEW REPORT ****************")
        reportLine("[REPORT] General Information:")
        for i in generalItem:
            reportLine("    {} : {}".format(i, generalDict[i]))
        reportLine("")
        reportLine("[REPORT] Detailed Day-by-Day Information:")
        for key in sorted(dailyDict.keys()):
            daily = dailyDict[str(key)]
            for i in dailyItem:
                reportLine("        {} : {}".format(i, daily[i]))
            reportLine("    ************************************************")
        reportLine("[REPORT] Done Report")
        reportLine("")

    global plotNotebook, filterA, filterB, initList
    
    echo("[WARN] All previous reports will be deleted.")
    reportText.deleteAll()
    
    filter = {
        'A': filterA,
        'B': filterB
    }
    
    plotGroup = plotNotebook.currentApp.getPlotList()
    if len(plotGroup) == 0:
        echo("[WARN] There is nothing to report.")
    else:
        echo("[INFO] Getting report generator ready.")

    for group in plotGroup:
        group.pop(0)
        for plot in group:
            if plot.getType() == 'gateway':
                continue
            else:
                report = sensorReport(plot, initList, filter)
                sensorReportAdapter(report.getReport())
                echo("[INFO] Report for {} generated.".format(plot.getLegend()))
    
    echo("[INFO] All reports generated.")
    echo("[WARN] Save the report before instantiate a new one or data may be lost.")
    plotNotebook.currentApp.saveFigureAsImage('report_figure')
    fd = open("report.txt", "a+")
    fd.write(reportText.get(1.0, END))
    fd.close()

def onKeyPress(event):
#    if k=='\x1b[A':
#       print "up"
#    elif k=='\x1b[B':
#       print "down"
#    elif k=='\x1b[C':
#       print "right"
#    elif k=='\x1b[D':
#       print "left"
    if event.char == 'a':
        shiftPlotLeft()
    elif event.char == 'd':
        shiftPlotRight()
                            
################# DECLARE GLOBAL VARIABLES #####################
licenseData = ""
startTimeInfo = ""
stopTimeInfo = ""
gatewayList = []
sensorList = []
plotList = []
GWSensorGroup = {}
filterA = 0
filterB = 0
filterStep = 500000
GWSensorFile = None
GWStatusFile = None
initList = None
currentDir = os.getcwd()
################################################################
initSystem()
################################################################
root = Tk()
root.title("Plantect - Gateway Sensor Monitoring System")
################################################################
gatewayVar = StringVar(root)
sensorVar = StringVar(root)
plotListVar = StringVar(root)
gatewayVar.set("Select")
sensorVar.set("Select")
plotListVar.set("New")

topNotebook = ttk.Notebook(root)
mainTab = ttk.Frame(topNotebook)
instructionTab = ttk.Frame(topNotebook)
aboutTab = ttk.Frame(topNotebook)
topNotebook.add(mainTab, text = "Main System")
topNotebook.add(instructionTab, text = "Instruction")
topNotebook.add(aboutTab, text = "About")
topNotebook.pack()

# Define mainTab
mainTabLeft = Frame(mainTab, width = 300, height = 800)
mainTabLeft.pack_propagate(0)
mainTabLeft.pack(side = LEFT)
controlPanelFrame = Frame(mainTabLeft, width = 300, height = 450)
controlPanelFrame.pack_propagate(0)
controlPanelFrame.pack()
plotFrame = Frame(mainTab, width = 1200, height = 800)
plotFrame.pack_propagate(0)
plotFrame.pack(side = LEFT)
infoFrame = Frame(mainTabLeft, width = 300, height = 350)
infoFrame.pack_propagate(0)
infoFrame.pack(fill = X)
infoFrameLabel = Frame(infoFrame)
infoFrameLabel.pack(fill = X)
infoFrameContent = Frame(infoFrame)
infoFrameContent.pack()

# Define plotFrame notebook
plotNotebook = PlotNotebook(plotFrame)
plotNotebook.pack()

# Define appNotebook <- inside controlPanelFrame <- inside mainTab <- topNotebook
appNotebook = ttk.Notebook(controlPanelFrame)
functionTab = ttk.Frame(appNotebook)
configTab = ttk.Frame(appNotebook)
reportTab = ttk.Frame(appNotebook)
appNotebook.add(functionTab, text = "Main")
appNotebook.add(configTab, text = "Configure")
appNotebook.add(reportTab, text = "Report")
appNotebook.pack(fill = BOTH, expand = True)

# report tab
reportLabelFrame = Frame(reportTab, width = 300, height = 30)
reportLabelFrame.pack_propagate(0)
reportLabelFrame.pack()
reportTextFrame = Frame(reportTab, width = 300, height = 350)
reportTextFrame.pack_propagate(0)
reportTextFrame.pack()
reportControlFrame = Frame(reportTab, width = 300, height = 70)
reportControlFrame.pack_propagate(0)
reportControlFrame.pack()

reportLabel = Label(reportLabelFrame, text = "Report Generator")
reportLabel.pack(padx = 10, anchor = 'w', pady = 5)

reportTextScroll = Scrollbar(reportTextFrame)
reportText = SyntaxHighlightingText(reportTextFrame)
reportText.config(wrap = WORD, font = 'Helvetica 8', spacing3 = 5, bg = 'white smoke')
reportTextScroll.config(command = reportText.yview)
reportText.config(yscrollcommand = reportTextScroll.set)
reportTextScroll.pack(side = RIGHT, fill = Y, padx = (0, 10), pady = 5)
reportText.pack(side = LEFT, padx = (10, 0), pady = 5)

reportButton = Button(reportControlFrame, command = onClickGenerateReport, text = "Generate", width = 15)
reportButton.pack(padx = 10, pady = 5)

###############################################
# CONFIGURE TAB DESIGN
###############################################
fileConfigFrame = Frame(configTab)
fileConfigFrame.pack(fill = X, pady = 5)
plotConfigFrame = Frame(configTab)
plotConfigFrame.pack(fill = X, pady = 5)
moveStepConfigFrame = Frame(configTab)
moveStepConfigFrame.pack(fill = X, pady = 5)

fileConfigLabel = Label(fileConfigFrame, text = "Browse Log File", width = 50, anchor = "w", justify = LEFT, font = "Helvetica 10 bold")
fileConfigLabel.pack()
fileConfigObject = configure_tab(fileConfigFrame, width = 50)
fileConfigObject.add_instance(name = "Gateway File", init_value = os.path.abspath("gateway.csv").replace('\\','/'))
fileConfigObject.add_instance(name = "Sensor File", init_value = os.path.abspath("sensor.csv").replace('\\','/'))
fileConfigObject.pack()
browseButtonFrame = Frame(fileConfigFrame)
browseButtonFrame.pack()
getGatewayFile = Button(browseButtonFrame, text = "Browse Gateway", width = 15, command = lambda:askForFile("Gateway File"))
getGatewayFile.grid(row = 0, column = 0, padx = 5)
getSensorFile = Button(browseButtonFrame, text = "Browse Sensor", width = 15, command = lambda:askForFile("Sensor File"))
getSensorFile.grid(row = 0, column = 1, padx = 5)

plotConfigLabel = Label(plotConfigFrame, text = "Configure Plot", width = 50, anchor = "w", justify = LEFT, font = "Helvetica 10 bold")
plotConfigLabel.pack()
plotConfigObject = configure_tab(plotConfigFrame, width = 50)
plotConfigObject.add_instance(name = "Scatter Size", init_value = 1)
plotConfigObject.add_instance(name = "Plot Method", method = "menu", input_option = ["scatter", "line"], init_value = 'scatter')
plotConfigObject.pack()

moveStepConfigLabel = Label(moveStepConfigFrame, text = "Configure Step", width = 50, anchor = "w", justify = LEFT, font = "Helvetica 10 bold")
moveStepConfigLabel.pack()
moveStepConfigObject = configure_tab(moveStepConfigFrame, width = 50)
moveStepConfigObject.add_instance(name = "Move Step Size", method = "menu", input_option = ["10 minutes", "30 minutes", "1 hour", "3 hours", "6 hours", "12 hours", "1 day", "3 days", "custom"], init_value = "custom")
moveStepConfigObject.add_instance(name = "Custom Step", init_value = filterStep)
moveStepConfigObject.pack()

configUpdateButton = Button(configTab, text = "Update", command = updateConfiguration, width = 15)
configUpdateButton.pack(pady = 10)

configTab.bind("<Enter>", onConfigTabSwitch)
#################################################################
# define about tab of notebook
licenseFrame = Frame(aboutTab, width = 1500, height = 200)
licenseFrame.pack_propagate(0)
licenseFrame.pack(side = LEFT)
licenseInformation = Label(licenseFrame, text = licenseData, font = "Helvetica 12")
licenseInformation.pack(anchor = "center")

#################################################################
# Define instruction frame
instructionFrame = Frame(instructionTab, width = 1500, height = 800)
instructionFrame.pack_propagate(0)
instructionFrame.pack(fill = BOTH)
instructionTextScroll = Scrollbar(instructionFrame)
instructionText = TextWithIndentation(instructionFrame)
instructionText.config(width = 1500, height = 800, wrap = WORD, font = 'Helvetica 12', spacing3 = 10, bg = 'white smoke')
instructionTextScroll.config(command = instructionText.yview)
instructionText.config(yscrollcommand = instructionTextScroll.set)
instructionTextScroll.pack(side = RIGHT, fill = Y, padx = (0, 10), pady = 5)
instructionText.pack(side = LEFT, padx = (10, 0), pady = 5, fill = BOTH)
data = open('instruction')
instruction = data.read().split('\n')
tab = '    ' #a tab is four space
for i in instruction:
    # encode tab as key, with format <0> <- number inside bracket is the indentation level
    tabArray = [m.start() for m in re.finditer(tab, i)]
    i = i[len(tabArray)*len(tab):] # delete the tabs so that there is only text
    key = "<{}>".format(len(tabArray)) 
    instructionText.insert(END, "{}\n".format(i)) # output the text
    instructionText.key_press("{} {}".format(key, i)) # encode the text with correct indentation key to format it.
instructionText.config(state = DISABLED)

# define GUI of function tab (main tab)
filterFrame = Frame(functionTab, width = 300, height = 250)
filterFrame.pack_propagate(0)
filterFrame.pack(fill = X)
filterFrameLabel = Frame(filterFrame)
filterFrameLabel.pack(fill = X)
filterFrameContent = Frame(filterFrame)
filterFrameContent.pack()
actionFrame = Frame(functionTab, width = 300, height = 200)
actionFrame.pack_propagate(0)
actionFrame.pack(fill = X)
actionFrameLabel = Frame(actionFrame)
actionFrameLabel.pack(fill = X)
actionFrameContent = Frame(actionFrame)
actionFrameContent.pack()

# define GUI of filterFrame, including choosing gateway, sensor, plot, startTime, stopTime
filterActionLabel = Label(filterFrameLabel, text = "FILTER ACTION", font = 'Helvetica 10 bold')
filterActionLabel.pack(pady = (10, 0), anchor = 'w', padx = (10, 0))
gatewayLabel = Label(filterFrameContent, text = "Gateway")
gatewayLabel.grid(row = 0, column = 0, pady = 5, sticky = 'w')
gatewayMenu = ttk.Combobox(filterFrameContent, textvariable = gatewayVar, values = gatewayList, postcommand = changeGateway, width = 30)
gatewayMenu.grid(row = 0, column = 1, pady = 5)
sensorLabel = Label(filterFrameContent, text = "Sensor")
sensorLabel.grid(row = 1, column = 0, pady = 5, sticky = 'w')
sensorMenu = ttk.Combobox(filterFrameContent, textvariable = sensorVar, values = sensorList, postcommand = updateSensorList, width = 30)
sensorMenu.grid(row = 1, column = 1, pady = 5)
plotMenuLabel = Label(filterFrameContent, text = "Plot")
plotMenuLabel.grid(row = 2, column = 0, pady = 5, sticky = 'w')
plotMenu = ttk.Combobox(filterFrameContent, textvariable = plotListVar, values = plotList, postcommand = updatePlotList, width = 30)
plotMenu.grid(row = 2, column = 1, pady = 5)
startTimeFrame = Frame(filterFrameContent)
startTimeFrame.grid(row = 3, columnspan = 2, sticky = 'w')
stopTimeFrame = Frame(filterFrameContent)
stopTimeFrame.grid(row = 4, columnspan = 2, sticky = 'w')
startTimeEntry = timePicker(startTimeFrame)
startTimeEntry.setLabel("Start Time")
stopTimeEntry = timePicker(stopTimeFrame)
stopTimeEntry.setLabel("Stop Time")

# define actionFrame
plotActionLabel = Label(actionFrameLabel, text = "PLOT ACTION", font = 'Helvetica 10 bold')
plotActionLabel.pack(pady = (10, 0), anchor = 'w', padx = (10, 0))
logSingleButton = Button(actionFrameContent, text = 'Plot Single', width = 15, command = plotSingleSensor)
logSingleButton.grid(row = 0, column = 0, pady = 2, padx = 5)
logGatewayButton = Button(actionFrameContent, text = 'Plot Gateway', width = 15, command = plotGatewayStatus)
logGatewayButton.grid(row = 1, column = 0, pady = 2, padx = 5)
logAllButton = Button(actionFrameContent, text = "Plot All", width = 15, command = plotAllSensors)
logAllButton.grid(row = 2, column = 0, pady = 2, padx = 5)
refreshButton = Button(actionFrameContent, text = 'Refresh', width = 15, command = refresh)
refreshButton.grid(row = 0, column = 1, pady = 2, padx = 5)
removeButton = Button(actionFrameContent, text = "Remove", width = 15, command = removePlotInCanvas)
removeButton.grid(row = 1, column = 1, pady = 2, padx = 5)
removeAllButton = Button(actionFrameContent, text = "Remove All", width = 15, command = removeAllPlotInCanvas)
removeAllButton.grid(row = 2, column = 1, pady = 2, padx = 5)

shiftLeftButton = Button(actionFrameContent, text = "Move Left", width = 15, command = shiftPlotLeft)
shiftLeftButton.grid(row = 3, column = 0, pady = (20,0), padx = 5)
shiftRightButton = Button(actionFrameContent, text = "Move Right", width = 15, command = shiftPlotRight)
shiftRightButton.grid(row = 3, column = 1, pady = (20,0), padx = 5)

infoLabel = Label(infoFrameLabel, text = "INFO", font = 'Helvetica 10 bold')
infoLabel.pack(pady = (10, 0), anchor = 'w', padx = (10, 0))
infoTextScroll = Scrollbar(infoFrameContent)
infoText = SyntaxHighlightingText(infoFrameContent)
infoText.config(wrap = WORD, font = 'Helvetica 8', spacing3 = 5, bg = 'white smoke')
infoTextScroll.config(command = infoText.yview)
infoText.config(yscrollcommand = infoTextScroll.set)
infoTextScroll.pack(side = RIGHT, fill = Y, padx = (0, 10), pady = 10)
infoText.pack(side = LEFT, padx = (10, 0), pady = 10)
infoText.config(state = DISABLED)

root.bind("<Key>", onKeyPress)
root.after(500, postSysStartHierarchy)
root.mainloop()