import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
#Imports for pycaw usage
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 1280, 720

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

#initializing pychaw for controlling the volume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
#volume.SetMasterVolumeLevel(-96, None)
minVol = volRange[0]
maxVol = volRange[1]

detector = htm.handDetector(detectionConfidence=0.9)

while True:
    #reading each frame of the video
    success, frame = cap.read()

    #reading the hand
    frame = detector.findHands(frame)
    lmlist = detector.findPosition(frame, draw=False)
    if lmlist:
       #print(lmlist[4], lmlist[8])

        #drawing a circle around the index finger and thumb
        x1, y1 = lmlist[4][1], lmlist[4][2]
        x2, y2 = lmlist[8][1], lmlist[8][2]

        frame = cv2.circle(frame, (x1,y1),10, (255,0,255), cv2.FILLED)
        frame = cv2.circle(frame, (x2, y2),10, (255, 0, 255), cv2.FILLED)
        frame = cv2.line(frame, (x1,y1), (x2,y2), (255,0,255), 3)

        #calculating the length between the fingers
        length = math.hypot(x2-x1, y2-y1)
        #print(length)

        #Hand range was from 30 to 280
        #Volume range is from -96 to 0

        vol = np.interp(length, [30,280],[minVol,maxVol])
        print(length, vol)
        volume.SetMasterVolumeLevel(vol, None)

        #giving cool effects to the movement
        if length<30:
            frame = cv2.circle(frame, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
            frame = cv2.circle(frame, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
        elif length>280:
            frame = cv2.circle(frame, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            frame = cv2.circle(frame, (x2, y2), 10, (0, 0, 255), cv2.FILLED)


    #Inserting framerate into each frame
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    frame = cv2.putText(frame, str(int(fps)), (10,70), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 2, (255, 255, 0),3)

    #displaying each frame of the video
    cv2.imshow('frame', frame)

    keyboard = cv2.waitKey(1)
    if keyboard == 27:
        cap.release()
        cv2.destroyAllWindows()