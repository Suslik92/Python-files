import RPi.GPIO as GPIO

def Authorize_Ignition(): #Opens the relay
    GPIO.setup(2, GPIO.OUT)
    print ('Setting 2 high')
    GPIO.output(2, GPIO.LOW)
    time.sleep(5) #Time to allow ignition
    print ('Setting 2 low')
    GPIO.output(2, GPIO.High)

Authorize_Ignition()
GPIO.cleanup()
