import pandas as pd
import numpy as np
import csv

class GWSensorLogger:
    def __init__(self, path = "sensor.csv"):
        with open(path, "rb") as csvread:
            reader = csv.reader(csvread, delimiter = ',')
            reader = list(reader)
            header = reader[0]
        csvread.close()
        self.file = pd.read_csv(path, sep = ",", dtype = None)
        self.initList = self.file[header[:4]]
        self.path = path
        
        gatewayList = self.initList['Gateway ID']
        sensorList = self.initList['Sensor ID']
        GWSensorGroup = {}
        GWSensorSubset = []

        for i in range(len(gatewayList.index)-1):
            GWSensorSubset.append(sensorList[i])
            if gatewayList[i] != gatewayList[i+1]:
                GWSensorGroup[gatewayList[i]] = GWSensorSubset
                GWSensorSubset = []

        self.GWSensorGroup = GWSensorGroup.copy()
    
    def setPath(self, path):
        self.__init__(path)

    def getInitList(self):
        return self.initList
    
    def getFile(self):
        return self.file
    
    def getGroup(self):
        return self.GWSensorGroup
    
    def getSensorList(self, gateway):
        return self.GWSensorGroup[gateway]
    
    def getSensorValue(self, gateway, sensor):
        return self.file.loc[[self.file['Gateway ID'] == gateway] and self.file['Sensor ID'] == sensor]
    
    def getDataArray(self, gateway, sensor):
        b = self.getSensorValue(gateway, sensor)[:]
        c = b.iloc[0].iloc[4:][:]
        c = list(c)
        timeArray = []
        valueArray = []
        for col in c:
            col = col.replace("'","")
            for data in col.split(","):
                array = data.split("-")
                timeArray.append(array[0])
                valueArray.append(array[1])

        data = {'time': timeArray, 'value': valueArray}
        sensorData = pd.DataFrame(data).drop_duplicates().sort_values(by = ['time'])
        sensorData['time'] = pd.to_numeric(sensorData['time'])
        sensorData['value'] = pd.to_numeric(sensorData['value'])

        return sensorData
    
    def getPath(self):
        return self.path

class GatewayStatusLogger:
    def __init__(self, path = "gateway.csv"):
        with open(path, "rb") as csvread:
            reader = csv.reader(csvread, delimiter = ',')
            reader = list(reader)
            self.header = reader[0]
        csvread.close()
        self.file = pd.read_csv(path, sep = ",", dtype = None)
        self.initList = self.file[self.header[:3]][:]
        self.path = path

    def setPath(self, path):
        self.__init__(path)

    def getInitList(self):
        return self.initList

    def getHeader(self):
        return self.header
    
    def getFile(self):
        return self.file
    
    def getDataArray(self, gateway):
        sensorData = self.file.loc[self.file['Gateway ID'] == gateway]
        return sensorData
    
    def getPath(self):
        return self.path