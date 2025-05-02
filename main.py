# Import necessary libraries
import cv2
import cvzone
import pickle
import numpy as np
import firebase_admin
from firebase_admin import credentials, db
import time

# Load Firebase credentials
cred = credentials.Certificate("parkdata-12c63-firebase-adminsdk-x3u51-e150f6dbff.json")

# Initialize Firebase
firebase_admin.initialize_app(cred)
database_url = "https://parkdata-12c63-default-rtdb.firebaseio.com/"  # Replace with your URL
firebase_admin.initialize_app(cred, {
    'databaseURL': database_url
}, name='parking_app')  # Set a unique app name

desired_fps = 5
start_time = time.time() 

# Video feed
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 255)

# Set the focus value (range is typically 0-255)
focus_value = 255
cap.set(cv2.CAP_PROP_FOCUS, focus_value)

if not cap.isOpened():
    print("Unable to read the scanner")

# Load parking spots positions
with open('CarParkPos2', 'rb') as f:
    posList2 = pickle.load(f)
with open('CarParkPos3', 'rb') as f:
    posList3 = pickle.load(f)

width1, height1 = 180, 87
width2, height2 = 92, 160

# Define IDs for parking spots
id_list1 = list(range(1, 9))
id_list2 = list(range(9, 14))
parking_updates = {}

# Function to check parking space for the first set of parking spots
def checkParkingSpace2(imgPro2):
    global spaceCounter2

    for i, pos in enumerate(posList2):
        x, y = pos
        spot_id = id_list1[i]

        imgCrop = imgPro2[y:y + height1, x:x + width1]
        count = cv2.countNonZero(imgCrop)
        if count < 980:
            color = (0, 255, 0)
            thickness = 1
            spaceCounter2 += 1
            status = 1
        else:
            color = (0, 0, 255)
            thickness = 1
            status = 0

        # Update status dictionary only with status change (0/1)
        if str(spot_id) not in parking_updates or parking_updates[str(spot_id)] != status:
            parking_updates[str(spot_id)] = status

        cv2.rectangle(result, pos, (pos[0] + width1, pos[1] + height1), color, thickness)
        cvzone.putTextRect(result, f' {spot_id}: {status}', (pos[0], pos[1] + 10), scale=1, thickness=1,
                           offset=2, colorR=(0, 1, 0))

# Function to check parking space for the second set of parking spots
def checkParkingSpace3(imgPro3):
    global spaceCounter3

    for i, pos in enumerate(posList3):
        x, y = pos
        spot_id = id_list2[i]

        imgCrop = imgPro3[y:y + height2, x:x + width2]
        count = cv2.countNonZero(imgCrop)
        if count <= 450:
            color = (0, 255, 0)
            thickness = 1
            spaceCounter3 += 1
            status = 1
        else:
            color = (0, 0, 255)
            thickness = 1
            status = 0

        # Update status dictionary only with status change (0/1)
        if str(spot_id) not in parking_updates or parking_updates[str(spot_id)] != status:
            parking_updates[str(spot_id)] = status

        cv2.rectangle(result, pos, (pos[0] + width2, pos[1] + height2), color, thickness)
        cvzone.putTextRect(result, f' {spot_id}: {status}', (pos[0], pos[1] + 10), scale=1, thickness=1,
                           offset=2, colorR=(0, 1, 0))

# Main loop for processing video feed and checking parking spots
while True:
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    success, img = cap.read()
    new = cv2.resize(img, (900, 600))
    pts1 = np.float32([[235,97], [646,78], [0,571], [900,529]])
    pts2 = np.float32([[0, 0], [500, 0], [0, 600], [500, 600]]) 
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    result = cv2.warpPerspective(new, matrix, (500, 600))
    imgGray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)

    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    spaceCounter2 = 0
    spaceCounter3 = 0

    checkParkingSpace2(imgDilate)
    checkParkingSpace3(imgDilate)
    
    # Display the result
    cv2.imshow("Image", result)
    
    # Update Firebase database with parking updates
    ref = db.reference(f'/parking1', app=firebase_admin.get_app(name='parking_app'))
    ref.update(parking_updates)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video feed and close all windows
cap.release()
cv2.destroyAllWindows()
