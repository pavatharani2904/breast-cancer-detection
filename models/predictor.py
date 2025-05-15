import cv2
import numpy as np
import joblib
import os
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet import preprocess_input

# Load pre-trained ML models
knn_model = joblib.load('models/knn_model.pkl')
svm_model = joblib.load('models/svm_model.pkl')

# Load EfficientNetB0 model for feature extraction
effnet_model = EfficientNetB0(weights='imagenet', include_top=False, pooling='avg')  # output: (1280,)

# Preprocess the input image and extract features using EfficientNet
def extract_features(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)              # shape: (224, 224, 3)
    img_array = np.expand_dims(img_array, axis=0)    # shape: (1, 224, 224, 3)
    img_array = preprocess_input(img_array)          # Normalize using EfficientNetB0 rules
    features = effnet_model.predict(img_array)       # shape: (1, 1280)
    return features

# Combined prediction from KNN and SVM
def predict_combined(image_path):
    features = extract_features(image_path)          # shape: (1, 1280)

    knn_result = knn_model.predict(features)[0]
    svm_result = svm_model.predict(features)[0]

    return f"KNN Prediction: {knn_result} | SVM Prediction: {svm_result}"
