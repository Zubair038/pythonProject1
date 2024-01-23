import time
from cvzone.HandTrackingModule import HandDetector
import cv2
import os
import numpy as np

# Parameters
width, height = 1080,720
abc = 0
# Camera Setup
cap = cv2.VideoCapture(0)

cap.set(3, width)
cap.set(4, height)

folderPath = "Presentation"
# Hand Detector
detectorHand = HandDetector(detectionCon=0.8, maxHands=1)

# Variables
clr = [(0, 0, 255), (255, 0, 0), (0, 255, 0)] # color
clr_cng = 0
imgList = [] #image list
delay = 5
delay1 = 25
buttonPressed = False #condition1
buttonPressed1 = False #condition2
counter = 0  # for drawing
counter1 = 0  # for forward and backword
drawMode = False
imgNumber = 0
delayCounter = 0
annotations = [[]]
annotationNumber = -1
annotationStart = False
hs, ws = int(120 * 1), int(213 * 1)  # height and width of sided camera view

# Get list of presentation images
pathImages = sorted(os.listdir(folderPath), key=len)
print(pathImages)

while True:
    # Get image frame
    success, img = cap.read()
    img = cv2.flip(img, 1)
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])  #adddress
    imgCurrent = cv2.imread(pathFullImage)  # open

    # Find the hand and its landmarks
    hands, img = detectorHand.findHands(img)  # with draw
    # Draw Gesture Threshold line
    cv2.line(img, (0, 650), (width+300, 650), (0, 255, 0), 10)
    cv2.line(img, (600, 0), (600, height), (255, 0, 0), 10)
    if hands and buttonPressed is False:     # When hand is detected

        hand = hands[0]
        cx, cy = hand["center"]
        lmList = hand["lmList"]  # List of 21 Landmark points
        fingers = detectorHand.fingersUp(hand)  # List of which fingers are up

        # Constrain values for easier drawing
        xVal = int(np.interp(lmList[8][0], [width // 2, width], [0, width]))
        yVal = int(np.interp(lmList[8][1], [150, height - 150], [0, height]))
        indexFinger = xVal, yVal

        if fingers == [1, 1, 1, 0, 0] and buttonPressed1 is False and cy < 650:
            if clr_cng < 2:
                clr_cng = clr_cng + 1
                buttonPressed1 = True
            else:
                clr_cng = 0
                buttonPressed1 = True

        if cx < 600 and buttonPressed1 is False:  # If hand is at the height of the face
            if fingers == [0, 1, 1, 1, 1]:
                print("Left")
                buttonPressed1 = True
                if imgNumber > 0:
                    imgNumber -= 1
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False

        if cx > 600 and buttonPressed1 is False:
            if fingers == [0, 1, 1, 1, 1]:
                print("Right")
                buttonPressed1 = True
                if imgNumber < len(pathImages) - 1:
                    imgNumber += 1
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False

        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 12, clr[clr_cng], cv2.FILLED)



        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            annotations[annotationNumber].append([indexFinger, clr[clr_cng]])
            print(annotations)

            cv2.circle(imgCurrent, indexFinger, 12, clr[clr_cng], cv2.FILLED)

        else:
            annotationStart = False

        if fingers == [1, 1, 0, 0, 0]:
            if annotations:
                annotations.pop(-1)
                annotationNumber -= 1
                buttonPressed = True

    else:
        annotationStart = False

    if buttonPressed:
        counter += 1
        if counter > delay:
            counter = 0
            buttonPressed = False

    if buttonPressed1:
        counter1 += 1
        if counter1 > delay1:
            counter1 = 0
            buttonPressed1 = False

    for i, annotation in enumerate(annotations):
        for j in range(1, len(annotation)):
            # if j != 0:
            cv2.line(imgCurrent, annotation[j - 1][0], annotation[j][0], annotation[j][1], 12)


    imgSmall = cv2.resize(img, (ws, hs))
    h, w, _ = imgCurrent.shape
    imgCurrent[0:hs, w - ws: w] = imgSmall

    cv2.imshow("Slides", imgCurrent)
    cv2.imshow("Image", img)

    key = cv2.waitKey(1)
    if key == ord('w'):
        break