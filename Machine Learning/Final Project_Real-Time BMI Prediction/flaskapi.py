import cv2
import numpy as np
import streamlit as st
from keras.models import load_model

# Load the trained model
custom_resnet50_model = load_model("bmi_model_finetuned3.h5")

# Load the Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')

def preprocess_image(image):
    image = cv2.resize(image, (224, 224))
    image = image / 255.0
    return image

def predict_bmi(image):
    # Preprocess the image
    image = preprocess_image(image)

    # Expand dimensions to match model input shape
    image = np.expand_dims(image, axis=0)

    # Perform the prediction
    bmi_prediction = custom_resnet50_model.predict(image)[0][0]
    return bmi_prediction

# Create a Streamlit app
def main():
    st.title("BMI Estimation from Webcam")
    st.text("Press 'q' to stop the webcam stream.")

    # Open the video stream
    cap = cv2.VideoCapture(0)

    # Create a placeholder to display the frames
    video_placeholder = st.empty()

    # Loop over the frames
    while True:
        # Capture a frame from the video stream
        ret, frame = cap.read()

        # Convert the frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the grayscale frame
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Iterate over the detected faces
        for (x, y, w, h) in faces:
            # Draw bounding boxes around the faces
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Extract the face region
            face_region = frame[y:y + h, x:x + w]

            # Make a BMI prediction for the face region
            bmi_prediction = predict_bmi(face_region)

            # Add the BMI prediction text to the frame
            text = "BMI: {:.2f}".format(bmi_prediction)
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Display the frame in Streamlit
        video_placeholder.image(frame, channels="BGR", use_column_width=True)

        # Stop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture
    cap.release()

if __name__ == "__main__":
    main()
