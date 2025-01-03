
import cv2
import time
import numpy as np
import HandTrackingModule as htm
import serial

# Set camera resolution
wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
detector = htm.handDetector(detectionCon=0.7)

# Variables for controlling light with left hand
length = 0
barRange = 0
barPer = 0
area = 0
colorLight = (255, 0, 0)    # Default color for light status (off)

# Initialize serial communication with Arduino
arduino = serial.Serial('COM5', 9600)

while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture image")
        break

    img = cv2.flip(img, 1)
    img, handType = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    # Light control code for left hand (controls brightness)
    if handType == "Left" and lmList:
        # Calculate the area of the bounding box for hand scaling
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
        if 100 < area < 500:
            length, img, lineInfo = detector.findDistance(4, 8, img)
            barRange = np.interp(length, [15, 115], [400, 150])
            barPer = np.interp(length, [15, 115], [0, 100])

            smoothness = 10 # Step
            barPer = smoothness * round(barPer / smoothness)

            fingers = detector.fingersUp()
            #if not fingers[4]:  # Pinky down
             #   cv2.circle(img, (lineInfo[4], lineInfo[5]), 7, (0, 255, 0), cv2.FILLED)
              #  colorLight = (0, 255, 0)
            #else:
             #   colorLight = (255, 0, 0)

            # Send brightness level to Arduino
            brightness_level = int(barPer)
            arduino.write(f"B{brightness_level}\n".encode())  # Prefix 'B' to indicate brightness level

            cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
            cv2.rectangle(img, (50, int(barRange)), (85, 400), (255, 0, 0), cv2.FILLED)
            cv2.putText(img, f'{int(barPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
            cv2.putText(img, f'Light set: {int(barPer)}%', (380, 50), cv2.FONT_HERSHEY_PLAIN, 2, colorLight, 3)

            if length < 15 or length > 115:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 7, (0, 255, 0), cv2.FILLED)

    # Finger counting code for right hand (controls individual LEDs)
    elif handType == "Right" and lmList:
        fingers = detector.fingersUp()
        totalFingers = fingers.count(1)
        #print(fingers)

        # Send each finger status to Arduino
        for i, finger in enumerate(fingers):
            arduino.write(f"F{i}{finger}\n".encode())  # Prefix 'F' followed by finger index and status (0 or 1)

        cv2.rectangle(img, (20, 255), (160, 380), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(totalFingers), (45, 375), cv2.FONT_HERSHEY_PLAIN, 10, (255, 0, 0), 25)

    # Calculate frames per second (FPS) and display it
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    # Display the processed image
    cv2.imshow("Hand Detection", img)

    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close windows
cap.release()
cv2.destroyAllWindows()
