from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import datetime

#Set paths to the cascade & encodings files
cascade_file_loc = "haarcascade_frontalface_default.xml"
encodings_file_loc = "encodings.pickle"
Ident_Flag = 1 #Initialize the authorized driver flag to "Unauthorized"

#Load face encodings & Haar Cascades face detection
data = pickle.loads(open(encodings_file_loc, "rb").read())
detector = cv2.CascadeClassifier(cascade_file_loc)
print("Face encodings & Haar cascades detector loaded successfly.")

#Boot up camera and begin video streaming
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0) #To account for proper sensor calibration

#Iterate over frames from video stream for 10 seconds
Start_Time = datetime.datetime.now()
End_Time = Start_Time + datetime.timedelta(seconds=10)
while (End_Time > datetime.datetime.now()):
    #Sample frame and resize to 500px to quicken identification
    frame = vs.read()
    frame = imutils.resize(frame, width=500)
    #Convert sampled frame from BGR to Grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #Convert sampled frame from BGR to RGB for face recognition
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #Detect faces via Haar cascades, save their bounding box coords to rects
    rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
        minNeighbors=5, minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE)

    #Convert bounding box coords from OpenCV's (xpos, ypos, width, height)
    #to (top, right, bottom, left)
    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

    #For each bounding box - calculate respective facial embeddings
    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []

    #Iterate over the generated facial embeddings and find matches based
    #on our existing database
    for encoding in encodings:
        matches = face_recognition.compare_faces(data["encodings"],
            encoding)
        name = "Unknown"

        #If a successful match was found
        if True in matches:
            #Generate a list of indexes for all successful matches
            #and create a dict to count how many time each facial
            #embedding was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            #Iterate over the matched indexes and count how many times
            #each face was matched
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            #Declare the most matched face based on number of matchings
            #if 2 faces are tied, the first one is selected
            #If a face was recognized, pull Ident_Flag low to signify
            #an authorized driver
            name = max(counts, key=counts.get)
            if name in ['Ruslik', 'gal_gadot']:
                #global Ident_Flag
                Ident_Flag = 0
        
        #Update the list of names
        names.append(name)
        
    #Iterate over the recognized faces and label them
    #according to their identified names (if there are any)
    for ((top, right, bottom, left), name) in zip(boxes, names):
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        if (top-15 > 15): y = top - 15
        else: y = top + 15
        #y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_PLAIN, 0.75, (0, 255, 0), 2)

    #Display frame on screen for debugging purposes, comment for presentation
    #cv2.imshow("Frame", frame)
        
#For debugging purposes, comment for presentation
if (not Ident_Flag): print("Face authorized.")
else: print("Face not detected or unauthorized.")
#Terminate all windows
cv2.destroyAllWindows()
vs.stop()