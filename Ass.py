#from picamera import PiCamera
import time
from transitions import Machine
import logging
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
logging.basicConfig(filename='Log.txt',filemode='a',
                    level=logging.CRITICAL,format='%(asctime)s -- %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')

def Log_Event(Event_MSG): #Logs Event_MSG to Log.txt upon request
    logging.critical(Event_MSG)

def Authorize_Ignition(): #Opens the relay
    GPIO.setup(26, GPIO.OUT)
    print ('Setting 26 high')
    GPIO.output(26, GPIO.HIGH)
    time.sleep(5) #Time to allow ignition
    print ('Setting 26 low')
    GPIO.output(26, GPIO.LOW)

def Take_Alcohol_Reading():
    GPIO.setmode(GPIO.BCM)
    #GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Setup the default pin for input
    GPIO.setup(21, GPIO.IN)
    Positive_Input = 0
    for i in range (3): #Take 3 readings 2 secs apart
        if (GPIO.input(21) == 0):
            Positive_Input +=1
        #print('attempt' + str(i))
        time.sleep(2)
    #GPIO.cleanup()
    if (Positive_Input >= 2):
        return 1 #Return 1 for abnormal values
    else:
        return 0 #Return 0 for normal values

class Matter(object):
    def say_hello(self): print("hello, new state!")
    def say_goodbye(self): print("goodbye, old state!")
    def on_enter_Start(self):
         print("We've just entered Start")
         Log_Event('System Started') #Log the bootup
         #Display "calibrating sensors via tkinter"
         #after 10s
    def on_enter_Measurement(self):
        print("We've just entered Measurement")
        Alc_Flag = Take_Alcohol_Reading()
        if (Alc_Flag): output_msg = 'Measurement taken, alcohol level above threshold'
        else: output_msg = 'Measurement taken, alcohol level below threshold'
        Log_Event(output_msg)
    def on_enter_Verification(self):
        print("We've just entered Verification")
        Authorize_Ignition()
SBS = Matter()

#Initial - Dummy state.
#Start - Sensor calibration and bootup stage
#Measurement - Measures the alcohol content
#Verification - Check the value from Measurement stage and cross-reference against known faces
#Passed - Passed both test, open relay.
#Failed - Failed one of the tests, send SMS and keep ignition locked.
#Awaiting_Reply - Wait for a response SMS for 5 minutes, then restart.
states = ['Initial', 'Start', 'Measurement', 'Verification', 'Passed', 'Failed', 'Awaiting_Reply']

transitions = [
    { 'trigger': 'TrigToStart', 'source': 'Initial', 'dest': 'Start' },
    { 'trigger': 'System_Ready', 'source': 'Start', 'dest': 'Measurement' },
    { 'trigger': 'Measurement_Complete', 'source': 'Measurement', 'dest': 'Verification' },
    { 'trigger': 'Verification_Successful', 'source': 'Verification', 'dest': 'Passed' },
    { 'trigger': 'Verification_Failed', 'source': 'Verification', 'dest': 'Failed' },
    { 'trigger': 'SMS_Sent', 'source': 'Failed', 'dest': 'Awaiting_Reply' }
    #Success to restart
    #Failed to restart
]

machine = Machine(SBS, states=states, transitions = transitions, initial='Initial')

# Callbacks can also be added after initialization using
# the dynamically added on_enter_ and on_exit_ methods.
# Note that the initial call to add the callback is made
# on the Machine and not on the model.
#machine.on_enter_gas('say_hello')

# Test out the callbacks...
#machine.set_state('solid')
#lump.sublimate()

SBS.TrigToStart()
#Start stage, calibrate sensors, show messages, log system bootup
SBS.System_Ready()
#Measurement stage, take alcohol reading, log alcohol status.
SBS.Measurement_Complete()
GPIO.cleanup()
print ('GPIO reset')
