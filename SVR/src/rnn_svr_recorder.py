'''
Created on Jan 7, 2018
To do list:
**Priority**function to convert waveform to wav
UI to type in what was said
LSTM-RNN
@author: James
'''
# Rants to make me feel better
# I swear I'm gonna go back to a C type language if I see another poorly documented python library.
# Honestly anything with better documentation like JS and php.net.

# Note to self, analyze code from here for wav
# https://gist.github.com/Pretz/1773870 
# RNN tutorial
# https://github.com/mrubash1/RNN-Tutorial
# https://svds.com/tensorflow-rnn-tutorial/
# should also check this
# https://www.swharden.com/wp/2016-07-31-real-time-audio-monitor-with-pyqt/

import random
import time
from datetime import datetime

import serial
import wave
import struct
import sys
import csv, codecs, io
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QThread, QMutex
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QAction, qApp,
                              QDesktopWidget, QPushButton, QToolTip, QMessageBox,
                              QMenu, QTextEdit)

import pyqtgraph
import ui_main

ydata = [0] * 1000
dataHighSpeed = [0] * 1000
average_Voltage = 0
tempRecording = []
mutex = QtCore.QMutex()
completeMutex = QtCore.QMutex()
recordingMutex = QtCore.QMutex()
complete = False
recording = False

try:
    # Change the string to whatever serial port your Arduino is connected to on the bottom right corner in the Arduino sketch
    arduino = serial.Serial("COM3", 115200, timeout=3)
except:
    print('Please check the port')
    sys.exit(1)

class WavWriteThread(QtCore.QThread):
    def __init__(self):
        QThread.__init__(self)
        self.exiting = False
        
    def __del__(self):
        self.exiting = True
        self.wait()
    
    def run(self, fname, fcount):
        data = []
        
        
        for time, value in csv.reader(open(fname, 'U'), delimiter=','):
            try:
                data.append(float(value))#Here you can see that the time column is skipped
            except ValueError:
                pass # Just skip it
    
    
        arr = np.array(data)#Just organize all your samples into an array
        # Normalize data
        arr /= np.max(np.abs(data)) #Divide all your samples by the max sample value
        filename_head, extension = fname.rsplit(".", 1)        
        data_resampled = resample( arr, len(data) )
        wavfile.write("test%d.wav"%fcount, 1450, data_resampled) #resampling at 16khz
        print ("File written succesfully !")
        self.__del__()


class SerialReadThread(QtCore.QThread):
    def __init__(self):
        QThread.__init__(self)
        self.exiting = False
         
            
    def __del__(self):
        completeMutex.lock()
        global complete
        complete = True
        completeMutex.unlock()
        self.exiting = True
        self.wait()
    
    def run(self):
        recordCount = 0
        fileCount = 0
        timeZero = 0
        timeCurrent = 0
        timeFromZero = 0
        while True:
            
            t1=time.clock()
            dummydata = arduino.readline()      # Debug variable to see serial data sent
            data = dummydata.rstrip()
            while Is_Number(data) != True:      # Necessary to check since first serial data sent is not always valid
                dummydata = arduino.readline()
                data = dummydata.rstrip()
            data = float(data) * (5.0 / 1023.0) - average_Voltage
            
            mutex.lock()
            global dataHighSpeed
            dataHighSpeed.append(data)
            del dataHighSpeed[0]
            mutex.unlock()
            
            recordingMutex.lock()
            if recording == True:
                if recordCount == 0:
                    recordCount += 1
                    fileCount += 1
                    timeZero = time.clock()
                    timeCurrent = time.clock()
                    timeFromZero = timeCurrent - timeZero
                    tempRecording.append(data)
                    f =  open("test%d.csv" %fileCount, "w", newline='\n')
                    writer = csv.writer(f, csv.excel)
                        
                    row = [timeFromZero, data]
                    writer.writerow(row)
                else:
                    recordCount += 1
                    timeCurrent = time.clock()
                    timeFromZero = timeCurrent - timeZero
                    tempRecording.append(data)
                    
                    row = [timeFromZero, data]
                    writer.writerow(row)
            else:
                if recordCount != 0:
                    recordCount = 0
                    timeZero = 0
                    timeCurrent = 0
                    timeFromZero = 0
                    tempRecording.clear()
                    f.close()
                    self.wavThread = WavWriteThread()
                    self.wavThread.run("test%d.csv" %fileCount, fileCount)
                else:
                    pass
            recordingMutex.unlock()  
            
            print("update took %.03f ms"%((time.clock()-t1)*1000))
            completeMutex.lock()
            if complete == True:
                completeMutex.unlock()
                return
            completeMutex.unlock()
      
class ExampleApp(QMainWindow, ui_main.Ui_MainWindow):
    def __init__(self, parent=None):
        global average_Voltage
        average_Voltage = Calibration_Zero_Average()
        self.thread = SerialReadThread()
        self.thread.start()
        
        
        
        self.Y = [0] * 500
        pyqtgraph.setConfigOption('background', 'w') #before loading widget
        super(ExampleApp, self).__init__(parent)
        self.setupUi(self)
        self.btnAdd.clicked.connect(self.RecordToggle)
        self.grPlot.plotItem.showGrid(True, True, 0.7)
        self.update()

    def update(self):
        t1=time.clock()
        points=500 #number of data points
        X=np.arange(points)
        mutex.lock()
        self.Y.append(dataHighSpeed[999])
        del self.Y[0]
        mutex.unlock()
        C=pyqtgraph.hsvColor(time.time()/5%1,alpha=.5)
        pen=pyqtgraph.mkPen(color=C,width=10)
        self.grPlot.plot(X,self.Y,pen=pen,clear=True)
        #print("update took %.02f ms"%((time.clock()-t1)*1000))
        #if self.chkMore.isChecked():
        QtCore.QTimer.singleShot(1, self.update) # QUICKLY repeat 
    
    def RecordToggle(self):
        recordingMutex.lock()
        global recording
        recording = not recording
        if recording == True:
            recordingMutex.unlock()
            self.btnAdd.setText("Stop")
        else:
            recordingMutex.unlock()
            self.btnAdd.setText("Record")
            
        
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',"Are you sure to quit?", 
             QMessageBox.Yes |QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.thread.__del__()
            arduino.close()
            event.accept()
        else:
            event.ignore()   


####################
#    write_wave
#    write wave function from
#    https://stackoverflow.com/questions/41209733/csv-to-wav-python
#    Author: Gab55
#    Return: None
####################
def write_wav(data, filename, framerate, amplitude):
    wavfile = wave.open(filename,'w')
    nchannels = 1
    sampwidth = 2
    framerate = framerate
    nframes = len(data)
    comptype = "NONE"
    compname = "not compressed"
    wavfile.setparams((nchannels,
                        sampwidth,
                        framerate,
                        nframes,
                        comptype,
                        compname))
    frames = []
    for s in data:
        mul = int(s * amplitude)
        frames.append(struct.pack('h', mul))

    frames = ''.join(frames)
    wavfile.writeframes(frames)
    wavfile.close()
    print("%s written" %(filename)) 

####################
#    Is_Number
#    Self explanatory
#    Return: Float
####################
def Is_Number(x):
    try:
        float(x)
        return True
    except ValueError:
        return False

####################
#    Calculate_Average_Voltage
#    Self explanatory
#    Return: Float
####################
def Calculate_Average_Voltage(x):
    Average_Voltage = sum(x)/len(x)
    return Average_Voltage

####################
#    Calibration_Zero_Average
#    Calculates the average voltage of 1000 samples, zeroes the voltage
#    to that average.
#    Return: Float
####################
def Calibration_Zero_Average():
    dataArray = [0] * 1000
    for x in range(0,1000):
        dummydata = arduino.readline()      # Debug variable to see serial data sent
        data = dummydata.rstrip()
        while Is_Number(data) != True:      # Necessary to check since first serial data sent is not always valid
            dummydata = arduino.readline()
            data = dummydata.rstrip()
        data = float(data) * (5.0 / 1023.0)
        dataArray[x] = data
    return Calculate_Average_Voltage(dataArray)
 

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    app.exec_()
    print("DONE")