
import cv2
import mediapipe as mp
import math 

# Define a class for hand detection and tracking.
class handDetector():
    # Initialize the handDetector class with default values.
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode                 # Static mode for hands detection.
        self.maxHands = maxHands         # Maximum number of hands to detect.
        self.detectionCon = detectionCon # Minimum confidence for detection.
        self.trackCon = trackCon         # Minimum confidence for tracking.

        # Initialize MediaPipe hands module and drawing utilities.
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20] # IDs for the tips of each finger.

    # Detect hands in the image.
    def findHands(self, img, draw=True):
        # Convert the image from BGR to RGB, as required by MediaPipe.
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)  # Process the image to find hands.
        
        handType = None  # Initialize variable to store hand type ("Left" or "Right")

        # If hands are detected, process each hand landmark.
        if self.results.multi_hand_landmarks:
            for i, handLms in enumerate(self.results.multi_hand_landmarks):
                if draw:
                    # Draw landmarks on the hand if `draw` is True.
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
                
                # Determine hand type (Left or Right).
                if self.results.multi_handedness:
                    handType = self.results.multi_handedness[i].classification[0].label
        return img, handType  # Return processed image and hand type.

    # Identify landmarks' positions on a specific hand.
    def findPosition(self, img, handNo=0, draw=True):
        xList, yList = [], []     # Lists to store x and y coordinates of landmarks.
        bbox = []                 # Initialize bounding box.
        
        self.lmList = []          # List to store landmarks' information.
        
        # Check if hands are detected in the image.
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]  # Get specific hand.
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape  # Get dimensions of the image.
                # Calculate landmark coordinates in pixels.
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                self.lmList.append([id, cx, cy])  # Append landmark to list.
                if draw:
                    # Draw a small circle at each landmark point.
                    cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
            
            # Calculate the bounding box for the detected hand.
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax
            
            if draw:
                # Draw a rectangle around the hand.
                cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20), (bbox[2] + 20, bbox[3] + 20), (0, 255, 0), 2)
            
        return self.lmList, bbox  # Return list of landmarks and bounding box.

    # Determine which fingers are up based on landmarks.
    def fingersUp(self): 
        fingers = []
        
        # Thumb
        if self.lmList[self.tipIds[0]][1] < self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)  # Thumb is up
        else: 
            fingers.append(0)  # Thumb is down
        
        # Other fingers
        for id in range(1, 5):
            # Check if each finger's tip is above the mid-joint.
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)  # Finger is up
            else: 
                fingers.append(0)  # Finger is down
        return fingers  # Return list with status of each finger.

    # Calculate the distance between two points on the hand.
    def findDistance(self, p1, p2, img, draw=True):
        # Get coordinates for the two points.
        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # Midpoint between the points.
        
        if draw:
            # Draw circles on the points and a line between them.
            cv2.circle(img, (x1, y1), 7, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 7, (0, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
            cv2.circle(img, (cx, cy), 7, (0, 0, 255), cv2.FILLED)
            
        # Calculate the Euclidean distance between points.
        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]  # Return distance and points info.

# Main function for real-time hand detection.
def main():
    cap = cv2.VideoCapture(0)  # Start video capture.
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    detector = handDetector()  # Create hand detector instance.

    while True:
        success, img = cap.read()  # Read frame from video.
        if not success:
            print("Failed to capture image")
            break

        img, handType = detector.findHands(img)  # Detect hands and get hand type.
        lmList, bbox = detector.findPosition(img)  # Get hand landmarks and bounding box.

        if len(lmList) != 0:
            fingers = detector.fingersUp()  # Check which fingers are up.
            print(f"Detected Hand Type: {handType}")
            print(f"Fingers Up: {fingers}")

            if handType == "Left":
                # Action for left hand.
                print("Executing Left Hand Code")

            elif handType == "Right":
                # Action for right hand.
                print("Executing Right Hand Code")

        cv2.imshow("Hand Detection", img)  # Display the image.
        
        # Exit on pressing 'q'.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()  # Release video capture.
    cv2.destroyAllWindows()  # Close display windows.

# Run the main function when script is executed directly.
if __name__ == "__main__":
    main()
