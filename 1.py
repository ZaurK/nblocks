import cv2  # Import OpenCV library (version 4.11)

# Initialize video capture from default camera (index 0)
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Main loop to continuously read frames
while True:
    # Read a frame from the camera
    # - 'ret' is a boolean indicating if the frame was captured correctly
    # - 'frame' contains the image data in BGR format
    ret, frame = cap.read()

    # If frame reading failed, break the loop
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the original and grayscale frames
    cv2.imshow('Original (BGR)', frame)

    # Exit the loop if 'q' key is pressed
    if cv2.waitKey(1) == ord('q'):
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()