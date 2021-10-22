#from picamera import PiCamera
import time
import logging
#import serial
from transitions import Machine
import datetime as DT
#import RPi.GPIO as GPIO

#ser = serial.Serial("/dev/ttyUSB2",115200)
#ser.flushInput()
#GPIO.setmode(GPIO.BCM)
logging.basicConfig(filename='Log.txt',filemode='w',
                    level=logging.CRITICAL,format='%(asctime)s -- %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S') #Change filemode to 'a' at presentation

phone_number = '0526920307' #Designated phone number
text_message = ''
rec_buff = ''
NMEA = ''
override_flag = False

def System_Working_Hours(startTime, endTime, nowTime):
    if (startTime < endTime): return nowTime >= startTime and nowTime <= endTime
    else: return nowTime >= startTime or nowTime <= endTime

#if (System_Working_Hours(DT.time(19,00), DT.time(6,00), DT.datetime.now().time())):
    #override_flag = True #Toggle before presenation

def Send_AT_SMS(command,back,timeout):
    rec_buff = ''
    ser.write((command+'\r\n').encode())
    time.sleep(timeout)
    if ser.inWaiting():
        time.sleep(0.01 )
        rec_buff = ser.read(ser.inWaiting())
    if back not in rec_buff.decode(): #If we havent receieved a proper response via the keyword
        print(command + ' ERROR')
        print(command + ' back:\t' + rec_buff.decode())
        return 0
    else:
        reply = rec_buff.decode()
        if ('Unlock' in reply):
            global override_flag
            override_flag = True
        elif ('+CMGD' not in back):
            override_flag = False
        print(rec_buff.decode())
        return 1

def Send_AT_GPS(command,back,timeout):
    rec_buff = ''
    ser.write((command+'\r\n').encode())
    time.sleep(timeout)
    if ser.inWaiting():
        time.sleep(0.01 )
        rec_buff = ser.read(ser.inWaiting())
    if rec_buff != '':
        if back not in rec_buff.decode():
            print(command + ' ERROR')
            print(command + ' back:\t' + rec_buff.decode())
            return 0
        else:
            NMEA = rec_buff.decode()
            global Coords
            Coords = NMEA2Latlong(NMEA)
            return 1
    else:
        print('GPS is not ready')
        return 0

def Send_Coords_Message(phone_number,text_message):
    Send_AT_SMS("AT+CMGF=1","OK",1)
    answer = Send_AT_SMS("AT+CMGS=\""+phone_number+"\"",">",2)
    if 1 == answer:
        text_message = 'One or more ignition tests have failed.\n\n' + Coords
        ser.write(text_message.encode())
        ser.write(b'\x1A')
        answer = Send_AT_SMS('','OK',20)
        if (1 == answer): print('send successfully')
        else: print('error')
    else: print('error%d'%answer)

def Send_Unlock_SMS (phone_number,text_message):
    Send_AT_SMS("AT+CMGF=1","OK",1)
    answer = Send_AT_SMS("AT+CMGS=\""+phone_number+"\"",">",2)
    if 1 == answer:
        text_message = 'To bypass the system and authorize ignition, reply with "Unlock" (case sensitive).'
        ser.write(text_message.encode())
        ser.write(b'\x1A')
        answer = Send_AT_SMS('','OK',20)
        if 1 == answer:
            print('send successfully')
        else:
            print('error')
    else:
        print('error%d'%answer)

def ReceiveShortMessage():
    rec_buff = ''
    print('Setting SMS mode...')
    Send_AT_SMS('AT+CMGF=1','OK',2) #Set SMS read stage
    Send_AT_SMS('AT+CPMS=\"SM\",\"SM\",\"SM\"', 'OK', 1) #Specify location to read messages from
    answer = Send_AT_SMS('AT+CMGR=0','+CMGR:', 2) #Read the incoming message
    Send_AT_SMS('AT+CMGD=,4', '+CMGD', 2) #Delete all messages
    if 1 == answer:
        answer = 0
        if 'OK' in rec_buff:
            answer = 1
            print(rec_buff)
    else:
        print('error%d'%answer)
        return False
    return True

def get_gps_position():
    rec_null = True
    answer = 0
    print('Start GPS session...')
    rec_buff = ''
    Send_AT_GPS('AT+CGPS=1,1','OK',1)
    time.sleep(1)
    for i in range (2):
        answer = Send_AT_GPS('AT+CGPSINFO','+CGPSINFO: ',1)
        if 1 == answer:
            answer = 0
            if ',,,,,,' in rec_buff:
                print('GPS is not ready')
                rec_null = False
                time.sleep(1)
        else:
            print('error %d'%answer)
            rec_buff = ''
            Send_AT_GPS('AT+CGPS=0','OK',1)
            return False
        time.sleep(1)

def NMEA2Latlong (NMEA): #Convert from NMEA word format to Lat & Long coordinates
    print (NMEA)
    pos1 = NMEA.find(":")
    pos2 = NMEA.find("\n", pos1)
    loc  = NMEA[pos1+2:pos2]
    data = loc.split(',')
    DD_Lat = int(float(data[0])/100)
    MM_Lat = float(data[0])-DD_Lat*100
    Lat_Coor = DD_Lat+MM_Lat/60
    if (data[1] == 'S'):
        Lat_Coor = Lat_Coor*-1
    DD_Long = int(float(data[2])/100)
    MM_Long = float(data[2])-DD_Long*100
    Long_Coor = DD_Long+MM_Long/60
    if (data[3] == 'W'):
        Long_Coor = Long_Coor*-1
    Coords = 'The current location is Lat %f, Long %f.'%(Lat_Coor, Long_Coor)
    return Coords

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
    def on_exit_Initial(self):
        pass
        #if (override_flag): machine.set_state('Passed')
    def on_enter_Start(self):
        print("We've just entered Start") #For debugging purposes
        Log_Event('System initialized.') #Log the bootup
        if (override_flag):
            Log_Event("System disarmed between 0600-1900.")
            SBS.Timeframe()
         #Display "calibrating sensors via tkinter"
         #after 10s
    def on_enter_Measurement(self):
        print("We've just entered Measurement")
        global Alc_Flag
        #Alc_Flag = Take_Alcohol_Reading()
        Alc_Flag = 0
        if (Alc_Flag): output_msg = 'Measurement taken, alcohol level above threshold.'
        else: output_msg = 'Measurement taken, alcohol level below threshold'
        Log_Event(output_msg)
    def on_exit_Measurement(self):
        print("Exiting Measurement")
        #get_gps_position()
    def on_enter_Verification(self):
        #Image verification stuff
        print("We've just entered Verification")
        global Ident_Flag
        Ident_Flag = 1
        if (Ident_Flag): output_msg = 'Face not detected or unauthorized driver.'
        else: output_msg = 'Authorized driver identified.'
        Log_Event(output_msg)
    def on_enter_Passed(self):
        print("We've just entered Passed")
        #Authorize_Ignition()
        Log_Event('Ignition authorizd, activating starter relay.')
        Log_Event('System shutting down.')
        print ("exiting")
        exit()
    def on_enter_Failed(self):
        print("We've just entered Failed")
        #Display tkinter message according to which flag failed.
        Log_Event('One or more verification methods have failed, ignition remains locked.\n\t\t\tSending SMS to 0526920307.')
        #Send_Coords_Message(phone_number,text_message) #Send the first message, containing warning & lat long coordinates.
        #Send_Unlock_SMS(phone_number,text_message) #Send the subsequent message, containing bypass information.
    def on_enter_Awaiting_Reply(self):
        print("Waiting 5 minutes for a reply SMS from 0526920307.")
        for attempts in range (5):
            override_flag = False
            #ReceiveShortMessage() #Wait for "Unlock"
            if (override_flag):
                Log_Event("Override SMS received from 0526920307.")
                SBS.to_Passed() #Force to switch states due to override_flag
            else:
                time.sleep(3) #change to 5 for presentation
                print ("Waiting " + str(attempts))




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
    { 'trigger': 'Timeframe', 'source': 'Start', 'dest': 'Passed' },
    { 'trigger': 'System_Ready', 'source': 'Start', 'dest': 'Measurement' },
    { 'trigger': 'Measurement_Successful', 'source': 'Measurement', 'dest': 'Verification'},
    { 'trigger': 'Measurement_Failed', 'source': 'Measurement', 'dest': 'Failed'},
    { 'trigger': 'Verification_Successful', 'source': 'Verification', 'dest': 'Passed' },
    { 'trigger': 'Verification_Failed', 'source': 'Verification', 'dest': 'Failed' },
    { 'trigger': 'SMS_Sent', 'source': 'Failed', 'dest': 'Awaiting_Reply' }
    #Success to restart
    #Failed to restart
]

machine = Machine(SBS, states=states, transitions = transitions, initial='Initial')

SBS.TrigToStart()
    #Start stage, calibrate sensors, show messages, log system bootup
SBS.System_Ready()
    #Measurement stage, take alcohol reading, log alcohol status. If failed go to 'Failed'
if (Alc_Flag):
     SBS.Measurement_Failed()
     SBS.SMS_Sent()
else:
    #Measurement completed, go to facial 'Verification'
    SBS.Measurement_Successful()
    if (Ident_Flag):
         SBS.Verification_Failed()
         SBS.SMS_Sent()
    else:
         #Both verification methods successful, go to 'Passed'
         SBS.Verification_Successful()
GPIO.cleanup()
print ('GPIO reset')
print (override_flag)
