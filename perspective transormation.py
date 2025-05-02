import cv2
import numpy as np

# Capture video from webcam
cap = cv2.VideoCapture(0)

# Read a frame from the video capture
success, img = cap.read()

# Resize the captured frame to desired dimensions
new = cv2.resize(img, (900, 600))

# Define source and destination points for perspective transformation
pts1 = np.float32([[235, 97], [646, 78], [0, 571], [900, 529]])
pts2 = np.float32([[0, 0], [500, 0], [0, 600], [500, 600]])

# Compute the perspective transformation matrix
matrix = cv2.getPerspectiveTransform(pts1, pts2)

# Apply perspective transformation to the resized image
result = cv2.warpPerspective(new, matrix, (500, 600))

# Mouse callback function to capture BGR coordinates when the mouse moves
def get_coordinates(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        # Extract BGR values from the mouse position
        blue, green, red = x, y, 0  # Assuming BGR color order
        colorsBGR = [blue, green, red]
        print(f"BGR Coordinates (Resized Image): X - {blue}, Y - {green}")

# Create a window to display the resized image
window_name = "Resized Image"
cv2.imshow(window_name, result)

# Register the mouse callback function with the window
cv2.setMouseCallback(window_name, get_coordinates)

# Wait for a key press indefinitely
cv2.waitKey(0)

# Close all OpenCV windows
cv2.destroyAllWindows()
