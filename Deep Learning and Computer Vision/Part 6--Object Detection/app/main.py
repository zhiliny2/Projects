import streamlit as st
import os
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from helper import *

sns.set()

# Configure logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

def save_uploaded_file(uploaded_file):
    try:
        with open(os.path.join('uploaded', uploaded_file.name), 'wb') as f:
            f.write(uploaded_file.getbuffer())
        return 1    
    except:
        return 1        

def main():
    st.title('Dog Breed Classifier')

    uploaded_file = st.file_uploader("Upload Image")

    if uploaded_file is not None:
        logging.info("File uploaded: %s", uploaded_file.name)
        if save_uploaded_file(uploaded_file):
            # Display the file
            display_image = Image.open(uploaded_file)
            display_image = display_image.resize((500, 300))
            st.image(display_image)

            prediction = predictor(os.path.join('uploaded', uploaded_file.name))
            logging.info("Prediction: %s", prediction)

            # Drawing graphs
            st.markdown('**Predictions**')
            fig, ax = plt.subplots()
            ax = sns.barplot(y='name', x='values', data=prediction, order=prediction.sort_values('values', ascending=False).name)
            ax.set(xlabel='Confidence %', ylabel='Breed')
            st.pyplot(fig)

if __name__ == '__main__':
    main()