import cv2
import numpy as np
import joblib
import os

# Load pre-trained models (adjust the paths if needed)
knn_model = joblib.load('models/knn_model.pkl')
svm_model = joblib.load('models/svm_model.pkl')

# Preprocessing function for ultrasound image
def preprocess_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Grayscale
    img = cv2.resize(img, (224, 224))                   # Resize
    img = img.flatten() / 255.0                         # Normalize
    return np.array([img])                              # Return as batch

# Combined prediction from both models
def predict_combined(image_path):
    processed = preprocess_image(image_path)
    
    knn_result = knn_model.predict(processed)[0]
    svm_result = svm_model.predict(processed)[0]

    # You can customize the way both results are shown
    return f"KNN Prediction: {knn_result} | SVM Prediction: {svm_result}"
