import numpy as np
import os
import cv2
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

# ---------------------------
# STEP 1: Simulated Dataset (Replace with real data)
# ---------------------------

X_train = np.random.rand(100, 224, 224, 3)
y_train = np.random.randint(0, 2, size=(100,))
X_test = np.random.rand(20, 224, 224, 3)
y_test = np.random.randint(0, 2, size=(20,))

# ---------------------------
# STEP 2: Load MobileNetV2 for Feature Extraction
# ---------------------------

base_model = MobileNetV2(weights='imagenet', include_top=False, pooling='avg', input_shape=(224, 224, 3))
feature_extractor = Model(inputs=base_model.input, outputs=base_model.output)

def extract_features(images):
    images = preprocess_input(images)
    features = feature_extractor.predict(images)
    return features.reshape(features.shape[0], -1)

# Extract features
X_train_features = extract_features(X_train)
X_test_features = extract_features(X_test)

# ---------------------------
# STEP 3: Train KNN and SVM
# ---------------------------

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train_features, y_train)

svm = SVC(kernel='linear', probability=True)
svm.fit(X_train_features, y_train)

# ---------------------------
# STEP 4: Combined Prediction Function
# ---------------------------

def predict_combined(image_path):
    # Load and preprocess image
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    # Extract features
    features = feature_extractor.predict(img_array).reshape(1, -1)

    # Predict with both models
    knn_pred = knn.predict(features)[0]
    svm_pred = svm.predict(features)[0]

    # Majority voting
    if knn_pred == svm_pred:
        final_pred = knn_pred
        method = "KNN + SVM Agreement"
    else:
        final_pred = svm_pred  # Prefer SVM in disagreement
        method = "Disagreement – SVM used"

    result = 'Cancerous (Malignant)' if final_pred == 1 else 'Non-cancerous (Benign)'

    # Display image with prediction
    plt.imshow(img)
    plt.title(f"Prediction: {result} ({method})")
    plt.axis('off')
    plt.show()

    return result

# ---------------------------
# STEP 5: Predict on Uploaded Image (for local testing only)
# ---------------------------

# uploaded_image_path = '/content/malignant10.png'  # Replace with real path when needed
# print("Final Result:", predict_combined(uploaded_image_path))
