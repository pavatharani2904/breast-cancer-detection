import os
import numpy as np
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
import joblib

# Paths
BASE_DIR = os.getcwd()
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
TRAIN_DIR = os.path.join(DATASET_DIR, 'train')
VAL_DIR = os.path.join(DATASET_DIR, 'validation')
MODEL_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

IMG_SIZE = 224
BATCH_SIZE = 16
EPOCHS = 5  # Increase for better performance

# Data generators
train_datagen = ImageDataGenerator(rescale=1./255)
val_datagen = ImageDataGenerator(rescale=1./255)

train_gen = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True
)

val_gen = val_datagen.flow_from_directory(
    VAL_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)

# ✅ EfficientNetB0 model
print("🔧 Building EfficientNetB0 model...")
base_model = EfficientNetB0(weights='imagenet', include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
x = base_model.output
x = GlobalAveragePooling2D()(x)
predictions = Dense(3, activation='softmax')(x)
model = Model(inputs=base_model.input, outputs=predictions)

model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

# ✅ Train model
print("🏋️ Training CNN...")
model.fit(train_gen, epochs=EPOCHS, validation_data=val_gen)

# ✅ Save model
cnn_model_path = os.path.join(MODEL_DIR, 'efficientnetb0_model.h5')
model.save(cnn_model_path)
print(f"✅ CNN model saved to {cnn_model_path}")

# ✅ Feature extraction for KNN and SVM
print("📈 Extracting features for KNN and SVM...")
feature_extractor = Model(inputs=base_model.input, outputs=GlobalAveragePooling2D()(base_model.output))

def extract_features(generator):
    features = []
    labels = []
    for i in range(len(generator)):
        x_batch, y_batch = generator[i]
        if len(features) * BATCH_SIZE >= generator.n:
            break
        feature_batch = feature_extractor.predict(x_batch)
        features.append(feature_batch)
        labels.append(np.argmax(y_batch, axis=1))
    return np.vstack(features), np.concatenate(labels)

X_train, y_train = extract_features(train_gen)
X_val, y_val = extract_features(val_gen)

# ✅ Train and save KNN
print("🧠 Training KNN...")
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train, y_train)
joblib.dump(knn, os.path.join(MODEL_DIR, 'knn_model.pkl'))
print("✅ KNN model saved.")

# ✅ Train and save SVM
print("🧠 Training SVM...")
svm = SVC(kernel='linear', probability=True)
svm.fit(X_train, y_train)
joblib.dump(svm, os.path.join(MODEL_DIR, 'svm_model.pkl'))
print("✅ SVM model saved.")
