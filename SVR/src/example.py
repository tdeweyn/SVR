'''
Created on Jan 7, 2018

@author: James
'''

import serial
import numpy as np
from matplotlib import pyplot as plt

try:
    # Change the string to whatever serial port your Arduino is connected to on the bottom right corner in the Arduino sketch
    arduino = serial.Serial("COM3", 115200, timeout=1)  
except:
    print('Please check the port')

plt.ion() # animated plot
ydata = [0] * 50
ax1 = plt.axes()

# make plot
line, = plt.plot(ydata)
plt.ylim([10,40])
ymin = 0
ymax = 5
plt.ylim([ymin,ymax])

# start data collection
while True:  
    data = arduino.readline().rstrip()  # read data from serial 
                                        # port and strip line endings
    #if len(data.split(".")) == 2:
    #ymin = float(min(ydata))-10.0
    #ymax = float(max(ydata))+10.0
    #plt.ylim([ymin,ymax])
    ydata.append(data)
    del ydata[0]
    line.set_xdata(np.arange(len(ydata)))
    line.set_ydata(ydata)  # update the data
    plt.draw() # update the plot
    plt.pause(1)

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

# test test

#while True:
 #   print(str(arduino.readline()))

#if __name__ == '__main__':
#    print('This program is being run by itself')
#else:
#    print('Imported from another module')