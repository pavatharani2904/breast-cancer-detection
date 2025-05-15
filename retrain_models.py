import os
import cv2
import numpy as np
import joblib
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet import preprocess_input
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow warnings

# Paths and categories
dataset_path = os.path.join('dataset', 'train')
categories = ['normal', 'benign', 'malignant']

# Label mapping
label_map = {
    'normal': 0,
    'benign': 1,
    'malignant': 2
}

# Load EfficientNetB0 for feature extraction (no top layers, global average pooling)
effnet_model = EfficientNetB0(weights='imagenet', include_top=False, pooling='avg')

def extract_features(img_path):
    try:
        img = image.load_img(img_path, target_size=(224, 224))
    except Exception as e:
        print(f"Error loading image {img_path}: {e}")
        return None
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    features = effnet_model.predict(img_array)
    return features.flatten()

def load_dataset():
    features_list = []
    labels_list = []
    
    for category in categories:
        folder_path = os.path.join(dataset_path, category)
        if not os.path.exists(folder_path):
            print(f"Warning: Directory {folder_path} does not exist.")
            continue
        
        print(f"Loading images from {folder_path} ...")
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if not (filename.lower().endswith('.png') or filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg')):
                continue
            
            features = extract_features(file_path)
            if features is not None:
                features_list.append(features)
                labels_list.append(label_map[category])
    
    return np.array(features_list), np.array(labels_list)

def retrain_models():
    print("Loading and extracting features from dataset...")
    X, y = load_dataset()

    if len(X) == 0:
        print("No data found. Please check your dataset path and images.")
        return

    print(f"Extracted features from {len(X)} images.")
    
    # Split data into train and validation sets
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train KNN
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_train, y_train)
    y_pred_knn = knn.predict(X_val)
    knn_acc = accuracy_score(y_val, y_pred_knn)
    print(f"KNN Validation Accuracy: {knn_acc * 100:.2f}%")
    joblib.dump(knn, 'models/knn_model.pkl')
    
    # Train SVM
    svm = SVC(kernel='rbf', probability=True)
    svm.fit(X_train, y_train)
    y_pred_svm = svm.predict(X_val)
    svm_acc = accuracy_score(y_val, y_pred_svm)
    print(f"SVM Validation Accuracy: {svm_acc * 100:.2f}%")
    joblib.dump(svm, 'models/svm_model.pkl')
    
    print("Retraining complete and models saved.")

if __name__ == '__main__':
    retrain_models()
