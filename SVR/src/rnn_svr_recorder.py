'''
Created on Jan 7, 2018

@author: James
So what needs to be done: need graph fixed, csv to wav, and do the RNN tutorial.
'''
# I swear I'm gonna go back to a C type language if I see another poorly documented python library.
# Honestly anything with better documentation like JS and php.net.

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import random
import numpy as np
import sys
import time
from datetime import datetime
import tkinter as tk        # tkinter is for python 3, Tkinter is for python 2.  Change if necessary
                            # Seriously, how is this a thing?

import serial
from matplotlib import pyplot as plt

ydata = [0] * 100
try:
    # Change the string to whatever serial port your Arduino is connected to on the bottom right corner in the Arduino sketch
    arduino = serial.Serial("COM3", 115200, timeout=1)
except:
    print('Please check the port')
    sys.exit(1)


class App():
    def __init__(self):
        
        
        self.root = tk.Tk()                     # instantiate tk class, the main window
        self.root.wm_title("Embedding in TK")   # Window name

        self.fig = plt.figure()                 # creates figure instance
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('X')         # adds axes labels, can't see them for some reason
        self.ax.set_ylabel('Y')
        self.ymin = 0
        self.ymax = 5
        self.ax.set_ylim([self.ymin,self.ymax])
        self.fig = function1(self.fig, self.ax)     # fills figure with data
        
            

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)  # No documentation, but a lot of matplot stuff have this.  Guessing it draws on it
        self.toolbar = NavigationToolbar2TkAgg( self.canvas, self.root )    # Toolbar for canvas
        self.toolbar.update()                                               # updates it                   
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)     # organizes widgets in blocks before placing in parent widget
                                                                            # it acts on _tkcanvas because of some weird back end of matplotlib
                                                                            # the dumpster fire
        self.label = tk.Label(text="")      # Makes empty label
        self.label.pack()                   # Adds it to the UI above the toolbar
        self.update_clock()                 # Calls clock update function
        self.root.mainloop()                # UI loop that blocks
                                            # Subsitute of following
                                            # while True:
                                            #    tk.update_idletasks()
                                            #    tk.update()

    def update_clock(self):
        self.fig = function1(self.fig,self.ax)      # updates fig instance with new fig
        self.canvas.show()                          # Refreshes canvas to show new fig
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)     # organizes widgets in blocks before placing in parent widget
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.label.configure(text=now)              # Updates time text
        self.root.after(10, self.update_clock)      # after 10ms, it runs update_clock again because it's now part of the mainloop update cycle

def function1(fig, ax):
    ax.cla()                                                            # Clear current axes
    dummydata = arduino.readline()      # Debug variable to see serial data sent
    data = dummydata.rstrip()
    while Is_Number(data) != True:      # Necessary to check since first serial data sent is not always valid
        dummydata = arduino.readline()
        data = dummydata.rstrip()
    data = float(data) * (5.0 / 1023.0)
    global ydata
    ydata.append(data)
    del ydata[0]
    ax.plot(ydata)
    return fig

def Is_Number(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
    
def Calculate_Average_Voltage(x):
    Average_Voltage = sum(x)/len(x)
    return Average_Voltage

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

    
if __name__ == "__main__":
    app = App()