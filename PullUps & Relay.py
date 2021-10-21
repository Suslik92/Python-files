import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(2, GPIO.OUT)
for x in range (6):
    GPIO.output(2, GPIO.HIGH)
    print ("High")
    time.sleep(3)
    GPIO.output(2, GPIO.LOW)
    print ("Low")
    time.sleep(3)
# while True:
#     if GPIO.input(17):
#         print ("Offline")
#         time.sleep(0.25)
#     else:
#         print ("Online")
#         time.sleep(0.25)
#
# #if GPIO.input(17):
#     #print ("Online")
# #else:
#     #print ("Offline")
#
# GPIO.setup(18, GPIO.OUT)
# GPIO.output(18, GPIO.HIGH)

GPIO.cleanup() #cleans
