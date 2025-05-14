# models/predictor.py

import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

# Dummy training data (replace with real)
X_train = np.random.rand(50, 224, 224, 3).astype(np.float32)
y_train = np.random.randint(0, 2, size=(50,))

# Load feature extractor
base_model = MobileNetV2(weights='imagenet', include_top=False, pooling='avg', input_shape=(224, 224, 3))
feature_extractor = Model(inputs=base_model.input, outputs=base_model.output)

def extract_features(images, batch_size=8):
    images = preprocess_input(images)
    return feature_extractor.predict(images, batch_size=batch_size, verbose=0)

# Extract and train
X_train_features = extract_features(X_train)
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train_features, y_train)
svm = SVC(kernel='linear')
svm.fit(X_train_features, y_train)

def predict_combined(image_path):
    try:
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img).astype(np.float32)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        features = feature_extractor.predict(img_array, verbose=0).reshape(1, -1)
        knn_pred = knn.predict(features)[0]
        svm_pred = svm.predict(features)[0]

        if knn_pred == svm_pred:
            final_pred = knn_pred
            method = "KNN + SVM Agreement"
        else:
            final_pred = svm_pred
            method = "Disagreement – SVM used"

        label = 'Cancerous (Malignant)' if final_pred == 1 else 'Non-cancerous (Benign)'
        return f"{label} ({method})"
    except Exception as e:
        return f"Prediction Error: {str(e)}"
