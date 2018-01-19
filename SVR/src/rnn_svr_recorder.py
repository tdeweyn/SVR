'''
Created on Jan 7, 2018

@author: James
'''

import serial
import numpy as np
import datetime
from matplotlib import pyplot as plt

def Is_Number(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
    
def Calculate_Average_Voltage(x):
    Average_Voltage = sum(x)/len(x)
    return Average_Voltage

# Plotting currently based on rlabbe/real_time_plotting.py
# It does not work well since it freezes if you move the window.  Fix this

# rawdata = []
# count = 0
# 
# while count < 4:
#     rawdata.append(str(arduino.readline()))
#     count += 1
# print(rawdata)
# 
# def clean(L):
#     newl = []
#     for i in range(len(L)):
#         temp = L[i][2:]
#         newl.append(temp[:-5])
#     return newl
# 
# cleandata = clean(rawdata)
# 
# def write(L):
#     file = open("data.txt", mode ='w')
#     for i in range(len(L)):
#         file.write(L[i] + '\n')
#     file.close()
# 
# write(cleandata)

def main():
    try:
        # Change the string to whatever serial port your Arduino is connected to on the bottom right corner in the Arduino sketch
        arduino = serial.Serial("COM3", 115200, timeout=1)  
    except:
        print('Please check the port')
    
    fig = plt.gcf()
    fig.show()
    fig.canvas.draw()
    
    ydata = [0] * 100
    ax1 = plt.axes()
    
    # make plot
    line, = plt.plot(ydata)
    plt.ylim([10,40])
    ymin = 0
    ymax = 5
    plt.ylim([ymin,ymax])
    
    # start data collection
    while True:
        dummydata = arduino.readline()      # Debug variable to see serial data sent
        data = dummydata.rstrip()
        while Is_Number(data) != True:      # Necessary to check since first serial data sent is not always valid
            dummydata = arduino.readline()
            data = dummydata.rstrip()
        data = float(data) * (5.0 / 1023.0)
        ydata.append(data)
        del ydata[0]
        line.set_xdata(np.arange(len(ydata)))
        line.set_ydata(ydata)  # update the data
        fig.canvas.draw() # update the plot
    
if __name__ == "__main__":
    main()