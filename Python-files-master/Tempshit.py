import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
#GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
def Authorize_Ignition(): #Opens the relay
    GPIO.setup(2, GPIO.OUT)
    print ('Setting 26 high')
    GPIO.output(2, GPIO.LOW)
    time.sleep(5) #Time to allow ignition
    print ('Setting 26 low')
    GPIO.output(2, GPIO.HIGH)
    
Authorize_Ignition()
GPIO.cleanup()