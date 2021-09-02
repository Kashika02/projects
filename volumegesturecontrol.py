import cv2
import time
import numpy as np
import HANDTRACKINGMODULE as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
################################
widthcam, heightcam = 640 , 480
################################

cap = cv2.VideoCapture(0)
cap.set(3, widthcam)  #propID of width of a camera is 3
cap.set(4, heightcam)
pTime = 0


detector = htm.handDetector(detectionCon=0.7)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
vol=0
volBar=400
volPer=0
minVol = volRange[0]
maxVol = volRange[1]

while True:
    success, img = cap.read()
    img= detector.findHands(img)
    lmlist= detector.findPosition(img, draw=False)
    if len(lmlist) != 0:
        #print(lmlist[4], lmlist[8])

        x1, y1 = lmlist[4][1], lmlist[4][2]
        x2, y2 = lmlist[8][1], lmlist[8][2]
        cx, cy = (x1+x2) // 2, (y1+y2) // 2
        cv2.circle(img, (x1,y1), 15 , (255,0,255),cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img ,(x1,y1),(x2,y2),(0,255,255),3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        #print(length)

        # hand range was from 50 to 300
        # volume range is from -65 t0 0

        vol = np.interp(length,[50,200],[minVol, maxVol])
        volBar = np.interp(length, [50, 200], [400, 150])
        volPer = np.interp(length, [50, 200], [0, 100])

        print(int(length),vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length<50:
            cv2.circle(img, (cx, cy), 15, (0, 255,0), cv2.FILLED)

    cv2.rectangle(img,(50,150), (85,400),(0,255,0),3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img,f'FPS: {int(volPer)} %', (40,450), cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img,f'FPS: {int(fps)}', (40,70), cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,255),2)

    cv2.imshow('Img', img)
    cv2.waitKey(1)