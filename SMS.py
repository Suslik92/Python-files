#!/usr/bin/python

import serial
import time
import re

ser = serial.Serial("/dev/ttyUSB2",115200)
ser.flushInput()

phone_number = '0526920307' #********** change it to the phone number you want to call
text_message = ''
rec_buff = ''
NMEA = ''

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
        if 1 == answer:
            print('send successfully')
        else:
            print('error')
    else:
        print('error%d'%answer)

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
    time.sleep(2)
    #while rec_null:
    for i in range (3):
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
        time.sleep(1.5)

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

try:
    print('Getting GPS position')
    get_gps_position() #Save GPS position to coords
    print('Sending Short Message Test:')
    Send_Coords_Message(phone_number,text_message) #Send the first message, containing warning & lat long coordinates.
    Send_Unlock_SMS(phone_number,text_message) #Send the subsequent message, containing bypass information.
    print('Receive Short Message Test:\n')
    time.sleep(2)
    ReceiveShortMessage()#Wait for "Unlock"
    print(override_flag)#Verify bypass state
    del override_flag
except :
    if ser != None:
        ser.close()
