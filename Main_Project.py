# cd /home/pi/Desktop/pi-face-recognition
# python pi_face_recognition.py --cascade haarcascade_frontalface_default.xml --encodings encodings.pickle

# import the necessary packages
import serial
import RPi.GPIO as GPIO
import imutils
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import logging
from tkinter import *
from random import randint


GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(2, GPIO.OUT)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(21, GPIO.IN)
#GPIO.setup(18, GPIO.OUT)
input_value = GPIO.input(17)
GPIO.output(18, GPIO.HIGH)
logging.basicConfig(filename='Logging.log',filemode='a',
                    level=logging.info,format='%(asctime)s -- %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logging.info('Testlog')

root = Tk()
lab = Label(root)
lab.pack()

def update():
   lab['text'] = randint(0,1000)
   root.after(1000, update) # run itself again after 1000 ms
   
def parseLine(self, line): #Converts NMEA to Lat/Long coords
        ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE, timeout=None,
        xonxoff=False, rtscts=False,
        writeTimeout=None, dsrdtr=False,
        interCharTimeout=None)

        #removes the newline
        line = line.rstrip()

        #validate the sentence using the checksum
        assert self.calcCheckSum(line) == int(line[-2:], 16)

        #tries a number of parsing functions
        parseFunc = {
            "$GPRMC": self.parseRMC,
        }[line[:6]]
        
def sendMessage(self,phone_number, message):
        flag = False
        parseFunc(string.split(line[:-3], ','))
        while( i > 0 ):		#delete any old data
		while( ser.inWaiting() ): 
			sys.stdout.write( ser.read() )
			i = 5 	# Keep timeout reset as long as stuff in flowing.
		sys.stdout.flush()
		i -= 1
		sleep( 1 )
        self.sendCommand('AT+CMGS=\"' + nmbr + '\"')
        print 'SUCCESS'
        self.serialPort.write(message)
        self.serialPort.write('\x1A')  # send messsage if prompt received
        flag = True
        
def readMessage(self):
        flag = False
        message = ''
        self.sendCommand('AT+CMGR=1')
        self.serialPort.flushInput()
        self.serialPort.flushOutput()
        self.serialPort.readline().rstrip()
        while True:
            response = self.serialPort.readline().rstrip()
            if len(response)>1:
                if response == 'OK':
                    break
                else:
                    message = message +" " + response
                    flag = True

        return flag,message
        # response = self.getResponse().rstrip()
        # if response == 'OK':
        #     flag = False
        # else:
        #     message = self.serialPort.readline().rstrip()
        #     flag = True
        #
        # return flag,message

# run first time
update()

#root.mainloop()

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True,
	help = "path to where the face cascade resides")
ap.add_argument("-e", "--encodings", required=True,
	help="path to serialized db of facial encodings")
args = vars(ap.parse_args())

class SmartBufferHandler(logging.handlers.MemoryHandler):
    def __init__(self, num_buffered, *args, **kwargs):
        kwargs["capacity"] = num_buffered + 2  # +2 one for current, one for prepop
        super().__init__(*args, **kwargs)

    def emit(self, record):
        if len(self.buffer) == self.capacity - 1:
            self.buffer.pop(0)
        super().emit(record)

handler = SmartBufferHandler(num_buffered=2, target=logging.StreamHandler(), flushLevel=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")
logger.addHandler(handler)

# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(args["encodings"], "rb").read())
detector = cv2.CascadeClassifier(args["cascade"])

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
#vs = VideoStream(src=0).start()
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

# start the FPS counter
fps = FPS().start()

# loop over frames from the video file stream
while True:
	# grab the frame from the threaded video stream and resize it
	# to 500px (to speedup processing)
	frame = vs.read()
	frame = imutils.resize(frame, width=500)
	
	# convert the input frame from (1) BGR to grayscale (for face
	# detection) and (2) from BGR to RGB (for face recognition)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	
	# detect faces in the input image using the haar cascade face
# detector
print("[INFO] performing face detection...")
rects = detector.detectMultiScale(gray, scaleFactor=1.05,
	minNeighbors=5, minSize=(30, 30),
	flags=cv2.CASCADE_SCALE_IMAGE)
print("[INFO] {} faces detected...".format(len(rects)))

	# detect faces in the grayscale frame
	rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
		minNeighbors=5, minSize=(30, 30),
		flags=cv2.CASCADE_SCALE_IMAGE)

	# OpenCV returns bounding box coordinates in (x, y, w, h) order
	# but we need them in (top, right, bottom, left) order, so we
	# need to do a bit of reordering
	boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

	# compute the facial embeddings for each face bounding box
	encodings = face_recognition.face_encodings(rgb, boxes)
	names = []

	# loop over the facial embeddings
	for encoding in encodings:
		# attempt to match each face in the input image to our known
		# encodings
		matches = face_recognition.compare_faces(data["encodings"],
			encoding)
		name = "Unknown"

		# check to see if we have found a match
		if True in matches:
			# find the indexes of all matched faces then initialize a
			# dictionary to count the total number of times each face
			# was matched
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}

			# loop over the matched indexes and maintain a count for
			# each recognized face face
			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1

			# determine the recognized face with the largest number
			# of votes (note: in the event of an unlikely tie Python
			# will select first entry in the dictionary)
			name = max(counts, key=counts.get)
		
		# update the list of names
		names.append(name)

	# loop over the recognized faces
	for ((top, right, bottom, left), name) in zip(boxes, names):
		# draw the predicted face name on the image
		cv2.rectangle(frame, (left, top), (right, bottom),
			(0, 255, 0), 2)
		y = top - 15 if top - 15 > 15 else top + 15
		cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
			0.75, (0, 255, 0), 2)

	# display the image to our screen
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

	# update the FPS counter
	fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()

power_key = 6
P_BUTTON = 24 # remove this before presentation

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(P_BUTTON, GPIO.IN, GPIO.PUD_UP)
    
#SERIAL_PORT = "/dev/ttyAMA0"  # test only
SERIAL_PORT = "/dev/ttyS0"    # Raspberry Pi 4 [B]

ser = serial.Serial(SERIAL_PORT, baudrate = 115200, timeout = 5)
setup()
ser.write("AT+CMGF=1\r") # set to text mode
time.sleep(3)
ser.write('AT+CMGDA="DEL ALL"\r') # delete all SMS
time.sleep(3)
reply = ser.read(ser.inWaiting()) # Clean buf
#changed to SIM7600x
gsm_ser = serial.Serial()
gsm_ser.port = "/dev/ttyUSB0"
gsm_ser.baudrate = 9600
gsm_ser.timeout = 3
gsm_ser.xonxoff = False
gsm_ser.rtscts = False
gsm_ser.bytesize = serial.EIGHTBITS
gsm_ser.parity = serial.PARITY_NONE
gsm_ser.stopbits = serial.STOPBITS_ONE


try:
    gsm_ser.open()
    gsm_ser.flushInput()
    gsm_ser.flushOutput()
except:
    print 'Cannot open serial port'
    sys.exit()

GSM = gsm(gsm_ser)

GSM.sendCommand("AT+IPR=9600;&W")
print GSM.getResponse()

time.sleep(.1)

GSM.sendCommand("AT+CMGF=1;&W")
print GSM.getResponse()

time.sleep(.1)

GSM.sendCommand("AT+CREG?")
print GSM.getResponse()

time.sleep(.1)

GSM.sendCommand("AT+CMGD=1")
print GSM.getResponse()

time.sleep(.1)

# if (GSM.sendMessage("8129025513", "HELLO MISTER") == True):
#     print 'Message sending Success'
# else:
#     print 'Message sending Failed'
# time.sleep(.1)

status,msg = GSM.readMessage()
if status == 0:
    print 'no new messages'
else:
    print 'new messages arrived: ' + ms

gsm_ser.close()

print "Listening for incomming SMS..."
while True:
    reply = ser.read(ser.inWaiting())
    if reply != "":
        ser.write("AT+CMGR=1\r") 
        time.sleep(3)
        reply = ser.read(ser.inWaiting())
        print "SMS received. Content:"
        print "reply:" + reply # fix this before presentation
        if "a" in reply:
            t = str(datetime.datetime.now())
            if GPIO.input(P_BUTTON) == GPIO.HIGH:
                state = "Button released"
            else:
                state = "Button pressed"
            ser.write('AT+CMGS="1234567890"\r')
            time.sleep(3)
            msg = "Sending status at " + t + ":--" + state
            print "Sending SMS with status info:" + msg
            ser.write(msg + chr(26))
        time.sleep(3)
        ser.write('AT+CMGDA="DEL ALL"\r') # delete all
        time.sleep(3)
        ser.read(ser.inWaiting()) # Clear buf
    time.sleep(5)    