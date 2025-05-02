import cv2
import pickle
import numpy as np

# Define the width and height of parking spots for both sets
width1, height1 = 175, 85
width2, height2 = 92, 160

# Load previously saved parking spot positions if available
try:
    with open('CarParkPos2', 'rb') as f:
        posList2 = pickle.load(f)
except:
    posList2 = []

try:
    with open('CarParkPos3', 'rb') as f:
        posList3 = pickle.load(f)
except:
    posList3 = []

# Open the default camera (0)
cap = cv2.VideoCapture(0)

# Function to handle mouse click events for the first set of parking spots
def mouseClick2(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:
        posList2.append((x, y))
    if events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(posList2):
            x1, y1 = pos
            if x1 < x < x1 + width1 and y1 < y < y1 + height1:
                posList2.pop(i)
    with open('CarParkPos2', 'wb') as f:
        pickle.dump(posList2, f)

# Function to handle mouse click events for the second set of parking spots
def mouseClick3(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:
        posList3.append((x, y))

    if events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(posList3):
            x1, y1 = pos
            if x1 < x < x1 + width2 and y1 < y < y1 + height2:
                posList3.pop(i)
    with open('CarParkPos3', 'wb') as f:
        pickle.dump(posList3, f)

# Main loop to capture frames and handle mouse events
while True:
    ret, frame = cap.read()  # Capture frame-by-frame

    if not ret:
        print("Error: Unable to capture frame")
        break

    # Resize the captured frame
    newimg = cv2.resize(frame, (900, 600))

    # Define perspective transformation matrix
    pts1 = np.float32([[235,97], [646,78], [0,571], [900,529]])
    pts2 = np.float32([[0, 0], [500, 0], [0, 600], [500, 600]]) 
    matrix = cv2.getPerspectiveTransform(pts1, pts2)

    # Apply perspective transformation
    result = cv2.warpPerspective(newimg, matrix, (500, 600))

    # Draw rectangles for parking spots on the resulting image
    for pos in posList2:
        cv2.rectangle(result, pos, (pos[0] + width1, pos[1] + height1), (255, 0, 255), 1)
    for pos in posList3:
        cv2.rectangle(result, pos, (pos[0] + width2, pos[1] + height2), (255, 0, 255), 1)

    # Display the resulting image
    cv2.imshow("Image", result)

    # Register mouse callback function to handle mouse clicks
    #cv2.setMouseCallback("Image", mouseClick2)  # For the first set of parking spots
    cv2.setMouseCallback("Image", mouseClick3)  # For the second set of parking spots

    # Wait for a key press and check if 'q' is pressed to exit the loop
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
