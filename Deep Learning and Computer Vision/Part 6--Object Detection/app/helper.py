import os
import numpy as np
import pickle
import pandas as pd

import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.layers import Lambda, Input
from tensorflow.keras.models import Model
from tensorflow.keras.applications.resnet_v2 import ResNet50V2, preprocess_input as resnet_preprocess
from tensorflow.keras.applications.densenet import DenseNet121, preprocess_input as densenet_preprocess

current_path = os.getcwd()
dog_breeds_category_path = os.path.join(
    current_path, 'static/dog_breeds_category.pickle')
predictor_model = load_model(r'static/dogbreed.h5')

print("Weights loaded")

with open(dog_breeds_category_path, 'rb') as handle:
    dog_breeds = pickle.load(handle)

input_shape = (331, 331, 3)
input_layer = Input(shape=input_shape)

# first extractor ResNet50V2
preprocessor_resnet = Lambda(resnet_preprocess)(input_layer)
inception_resnet = ResNet50V2(weights='imagenet',
                              include_top=False, input_shape=input_shape, pooling='avg')(preprocessor_resnet)

# second extractor DenseNet121
preprocessor_densenet = Lambda(densenet_preprocess)(input_layer)
densenet = DenseNet121(weights='imagenet',
                       include_top=False, input_shape=input_shape, pooling='avg')(preprocessor_densenet)

# concatenate the two extractors
merge = layers.concatenate([inception_resnet, densenet])
feature_extractor = Model(inputs=input_layer, outputs=merge)

print("Models loaded")


def predictor(img_path):
    img = load_img(img_path, target_size=(331, 331))
    print(img_path)
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    features = feature_extractor.predict(img)
    prediction = predictor_model.predict(features)*100
    prediction = pd.DataFrame(np.round(prediction, 1),
                              columns=dog_breeds).transpose()
    prediction.columns = ['values']
    prediction = prediction.nlargest(5, 'values')
    prediction = prediction.reset_index()
    prediction.columns = ['name', 'values']
    return (prediction)
