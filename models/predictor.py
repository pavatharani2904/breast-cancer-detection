import cv2
import numpy as np
import joblib
import os
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet import preprocess_input

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow warnings

# Load pre-trained ML models
knn_model = joblib.load('models/knn_model.pkl')
svm_model = joblib.load('models/svm_model.pkl')

# Load EfficientNetB0 for feature extraction
effnet_model = EfficientNetB0(weights='imagenet', include_top=False, pooling='avg')  # Output: (1, 1280)

# Label mapping
label_map = {
    0: "Normal",
    1: "Benign",
    2: "Malignant"
}

# Extract features using EfficientNetB0
def extract_features(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    features = effnet_model.predict(img_array)
    return features

# Combined prediction using majority vote
def predict_combined(image_path):
    features = extract_features(image_path)

    knn_result = knn_model.predict(features)[0]
    svm_result = svm_model.predict(features)[0]

    # Majority voting logic
    votes = [knn_result, svm_result]
    final_prediction = max(set(votes), key=votes.count)

    return f"Final Diagnosis: {label_map[final_prediction]}"
