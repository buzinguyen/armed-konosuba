import numpy as np
import datetime

class sensorReport:
    # Create a general sensor report info:
    # Packet count over period
    # Data average over period
    # Percentage throughout time (daily)
    # Percentage average throughout time
    # Pass filter variable on init of report or set later
    # Structure of system:
    # filter: {'filter A': 0, 'filter B': 0}
    def __init__(self, plot, initList = None, filter = {'A': None, 'B': None}):
        self.data = plot
        self.filter = filter
        self.report = {}
        self.initList = initList
        self.summary()
    
    def summary(self):
        x = self.data.getX()
        y = self.data.getY()
        if self.filter['A'] != None:
            filterA = self.filter['A']
        else:
            filterA = min(x)
        
        if self.filter['B'] != None:
            filterB = self.filter['B']
        else:
            filterB = max(x)
        self.filter['A'] = filterA
        self.filter['B'] = filterB
        data = self.runFilter(self.filter)
        x = data['x']
        y = data['y']

        parent_gateway = self.data.getParent()
        try:
            parent_host = self.initList[self.initList['Gateway ID'] == parent_gateway].iloc[0]['Host']
            parent_location = self.initList[self.initList['Gateway ID'] == parent_gateway].iloc[0]['Location']
        except KeyError:
            parent_host = "Unknown"
            parent_location = "Unknown"

        try:
            int(parent_location)
        except ValueError:
            pass
        else:
            parent_location = "<postcode:{}>".format(parent_location)

        generalReport = {
            'Name': self.data.getLegend(),
            'Gateway': parent_gateway,
            'Host': parent_host,
            'Location': parent_location,
            'Start_Time': self.unixToTime(filterA),
            'Stop_Time': self.unixToTime(filterB),
            'Packet_Count': len(y),
            'Average': int(np.mean(y))
        }
        self.report['General'] = generalReport
        dailyReportSet = {}
        dateNumber = int(float(filterB - filterA)/86400000.0)
        
        if dateNumber == 0:
            fila = filterA
            filb = filterB
            dailyReport = {}
            result = self.runFilter({'A': fila, 'B': filb})
            x = result['x']
            y = result['y']
            dailyReport['Start_Time'] = self.unixToTime(fila)
            dailyReport['Stop_Time'] = self.unixToTime(filb)
            dailyReport['Packet_Count'] = len(y)
            dailyReport['Average'] = int(np.mean(y))
            dailyReport['Percentage'] = "{} %".format(int(float(len(y)*100)/144.0))
            dailyReportSet[str(0)] = dailyReport
        else:
            for d in range(0, dateNumber):
                dailyReport = {}
                fila = filterA + 86400000*d
                filb = filterA + 86400000*(d+1)
                result = self.runFilter({'A': fila, 'B': filb})
                x = result['x']
                y = result['y']
                dailyReport['Start_Time'] = self.unixToTime(fila)
                dailyReport['Stop_Time'] = self.unixToTime(filb)
                dailyReport['Packet_Count'] = len(y)
                dailyReport['Average'] = int(np.mean(y))
                dailyReport['Percentage'] = "{} %".format(int(float(len(y)*100)/144.0))
                dailyReportSet[str(d)] = dailyReport
            
            fila = filterA + 86400000*dateNumber
            filb = filterB
            if fila < filb:
                dailyReport = {}
                result = self.runFilter({'A': fila, 'B': filb})
                x = result['x']
                y = result['y']
                dailyReport['Start_Time'] = self.unixToTime(fila)
                dailyReport['Stop_Time'] = self.unixToTime(filb)
                dailyReport['Packet_Count'] = len(y)
                dailyReport['Average'] = int(np.mean(y))
                dailyReport['Percentage'] = "{} %".format(int(float(len(y)*100)/144.0))
                dailyReportSet[str(dateNumber)] = dailyReport

        self.report['Detail'] = dailyReportSet
    
    def runFilter(self, filter):
        # filter must be a set with ['A'] and ['B'] filter value that is meaningful
        # return new data array with filtered value, do not overwrite self.data
        x = list(self.data.getX()[:])
        y = list(self.data.getY()[:])
        for i in range (0, len(x)):
            if x[i] >= filter['A']:
                for j in range (0, i):
                    x.pop(0)
                    y.pop(0)
                break
        
        for i in range (0, len(x)):
            ri = len(x) - 1 - i
            if x[ri] <= filter['B']:
                for j in range (ri, len(x)):
                    x.pop()
                    y.pop()
                break
        result = {}
        result['x'] = x
        result['y'] = y
        return result

    def setFilter(self, filter = {'A':None, 'B':None}):
        self.filter = filter

    def getReport(self):
        return self.report
        
    def unixToTime(self, timestamp):
        return datetime.datetime.fromtimestamp(int(float(timestamp)/1000.0)).strftime('%Y-%m-%d %H:%M:%S')
