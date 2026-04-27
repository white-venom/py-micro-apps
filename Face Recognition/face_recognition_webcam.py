import cv2

# Loading The Cascade File
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Accessing the Webcam
cap = cv2.VideoCapture(0)

print("Press 'q' to quit the webcam.")

while True:
    # Reading the frame from webcam
    ret, frame = cap.read()
    if not ret:
        break

    # Converting to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detecting The Faces
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    # Drawing Rectangles
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, 'Face Detected', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Displaying The Output
    cv2.imshow('Real-time Face Recognition', frame)

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
