#Import the tkinter library
from tkinter import *
import time

#Create an instance of tkinter frame
win = Tk()
intvar = StringVar() #A tkinter string variable for labels
cntdwn = 10
intvar.set = 10

def rdy():
    #label= Label(win, text= "Sensors fully calibrated, please blow on the sensor", font=('Times New Roman bold',50))
    label.pack(padx=10, pady=10)
    label.configure(text="Sensors fully calibrated, please blow on the sensor")

def cntdwn_update(secs):
    if (secs):
        label.configure(text="Greetings, calibrating sensors " +str(secs))
        win.after(1000, cntdwn_update, secs-1)
    

win.geometry("650x250") #Set the geometry
win.attributes('-fullscreen', True) #Create a fullscreen window
intvar.set = "Greetings, calibrating sensor (10s)"
#Add a text label and add the font property to it
label= Label(win, text= "Greetings, calibrating sensors " + str(cntdwn), font=('Times New Roman bold',50))
label.pack(padx=10, pady=10)
win.after(1000, cntdwn_update, cntdwn-1)
win.after(10000, rdy)

win.mainloop()