import cv2
import numpy as np
import streamlit as st
from PIL import Image
import tensorflow as tf
import os
import urllib.request
import requests
import subprocess
import matplotlib.pyplot as plt

# # Function to load the model
model_url = 'https://github.com/zhiliny2/mltest/raw/master/bmi_model_finetuned3.h5'
model_path = 'model.h5'

if not os.path.isfile(model_path):
    response = requests.get(model_url)
    with open(model_path, 'wb') as f:
        f.write(response.content)
# model_path = 'bmi_model_finetuned3.h5'

# custom_resnet50_model = tf.keras.models.load_model(model_path, compile=False)


# # Function to load the model
custom_resnet50_model = tf.keras.models.load_model(model_path, compile=False)

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')

def preprocess_image(image):
    image = cv2.resize(image, (224, 224))
    image = image / 255.0
    return image

def predict_bmi(image, model):
    image = preprocess_image(image)
    image = np.expand_dims(image, axis=0)
    bmi_prediction = model.predict(image)[0][0]
    return bmi_prediction

def bmi_category(bmi):
    if bmi <= 18.5:
        return 'underweight'
    elif bmi <= 25:
        return 'normal'
    elif bmi <= 30:
        return 'overweight'
    elif bmi <= 35:
        return 'moderately obese'
    elif bmi <= 40:
        return 'severely obese'
    else:
        return 'very severely obese'

def main():
    st.title("BMI Estimation Using Fine-Tuned VGGFace Model")
    st.text("Upload an image to estimate BMI.")
    # add author
    st.text("Developer: Richard Yang")
    # add image url: C:\Users\Richa\MLcode\FinalProject\body-mass-index-bmi-chart.jpg
    image_path = os.path.join(os.getcwd(), ' body_mass_index_bmi_chart.jpg')
    st.image(image_path, use_column_width=True)


    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) == 0:
            st.error("No face detected in the uploaded image.")
        else:
            # Display a loading spinner
            with st.spinner('Processing image and estimating BMI...'):
                bmi_values = []
                for (x, y, w, h) in faces:
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    face_region = image[y:y + h, x:x + w]
                    bmi_prediction = predict_bmi(face_region, custom_resnet50_model)
                    bmi_values.append(bmi_prediction)
                    text = "BMI: {:.2f}".format(bmi_prediction)
                    cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            st.image(image, channels="RGB", use_column_width=True)

            # Show BMI range
            min_bmi = np.min(bmi_values)
            max_bmi = np.max(bmi_values)
            st.info(f"Estimated BMI range: {min_bmi:.2f} - {max_bmi:.2f}")

            # Show BMI category and recommendations
            bmi_category_text = bmi_category

            bmi_category_text = bmi_category(min_bmi)  # Assuming the minimum BMI represents the overall BMI category

            st.info(f"BMI Category: {bmi_category_text}")

            # Provide recommendations based on BMI category
            recommendations = {
                'underweight': 'Consider consulting with a healthcare professional for a personalized plan to achieve a healthy weight.',
                'normal': 'Maintain a balanced diet and engage in regular physical activity to sustain a healthy weight.',
                'overweight': 'Focus on adopting a nutritious eating plan and increasing physical activity to reach a healthier weight.',
                'moderately obese': 'Consult with a healthcare professional to develop a comprehensive weight management plan.',
                'severely obese': 'Seek medical guidance to address weight-related health concerns and explore appropriate interventions.',
                'very severely obese': 'Urgently consult with a healthcare professional for immediate assistance in managing weight and related health risks.'
            }

            if bmi_category_text in recommendations:
                st.info(f"Recommendation: {recommendations[bmi_category_text]}")
            else:
                st.warning("Unable to provide specific recommendations for the estimated BMI category.")

if __name__ == "__main__":
    main()

