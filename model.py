# model.py

import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.efficientnet import EfficientNetB0, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

# STEP 1: Simulated Training Data (Replace with real data)
X_train = np.random.rand(100, 224, 224, 3)
y_train = np.random.randint(0, 2, size=(100,))

# STEP 2: Feature Extractor Setup
base_model = EfficientNetB0(weights='imagenet', include_top=False, pooling='avg', input_shape=(224, 224, 3))
feature_extractor = Model(inputs=base_model.input, outputs=base_model.output)

def extract_features(images):
    images = preprocess_input(images)
    features = feature_extractor.predict(images)
    return features.reshape(features.shape[0], -1)

# STEP 3: Extract Features from Simulated Dataset
X_train_features = extract_features(X_train)

# STEP 4: Train KNN and SVM Classifiers
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train_features, y_train)

svm = SVC(kernel='linear', probability=True)
svm.fit(X_train_features, y_train)

# STEP 5: Define the prediction function
def predict_combined(image_path):
    # Load and preprocess the image
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    # Extract features
    features = feature_extractor.predict(img_array).reshape(1, -1)

    # Get predictions
    knn_pred = knn.predict(features)[0]
    svm_pred = svm.predict(features)[0]

    # Use majority voting or SVM tie-breaker
    if knn_pred == svm_pred:
        final_pred = knn_pred
    else:
        final_pred = svm_pred

    result = 'Cancerous (Malignant)' if final_pred == 1 else 'Non-cancerous (Benign)'
    return result
