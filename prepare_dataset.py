import os
import zipfile
import shutil
from collections import defaultdict
from sklearn.model_selection import train_test_split

# Paths
BASE_DIR = os.getcwd()
ZIP_PATH = os.path.join(BASE_DIR, 'breast-ultrasound-images-dataset.zip')
EXTRACTED_DIR = os.path.join(BASE_DIR, 'Breast-Ultrasound-Images')
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
TRAIN_DIR = os.path.join(DATASET_DIR, 'train')
VAL_DIR = os.path.join(DATASET_DIR, 'validation')

# Step 1: Unzip
print("🔓 Unzipping dataset...")
with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
    zip_ref.extractall(EXTRACTED_DIR)

# Step 2: Gather images by class
print("📂 Gathering images...")
class_counts = defaultdict(list)
VALID_CLASSES = ['benign', 'malignant', 'normal']

for label in VALID_CLASSES:
    class_dir = os.path.join(EXTRACTED_DIR, 'Dataset_BUSI_with_GT', label)
    if not os.path.exists(class_dir):
        print(f"❌ Directory not found: {class_dir}")
        continue
    for file in os.listdir(class_dir):
        if file.lower().endswith(('.jpg', '.png', '.jpeg')) and 'mask' not in file.lower():
            class_counts[label].append(os.path.join(class_dir, file))

# Filter out classes with <2 images
filtered_image_paths = []
for label, files in class_counts.items():
    print(f"📊 {label}: {len(files)} images")
    if len(files) < 2:
        print(f"⚠️ Skipping class '{label}' (only {len(files)} image)")
        continue
    for path in files:
        filtered_image_paths.append((path, label))

# Step 3: Train-validation split
train_data, val_data = train_test_split(
    filtered_image_paths, test_size=0.2, random_state=42, stratify=[label for _, label in filtered_image_paths]
)

# Step 4: Create output folders
for base in [TRAIN_DIR, VAL_DIR]:
    for label in class_counts.keys():
        os.makedirs(os.path.join(base, label), exist_ok=True)

# Step 5: Copy files
def copy_files(data_list, destination):
    for src, label in data_list:
        dst = os.path.join(destination, label, os.path.basename(src))
        shutil.copy(src, dst)

print("📦 Copying training files...")
copy_files(train_data, TRAIN_DIR)

print("📦 Copying validation files...")
copy_files(val_data, VAL_DIR)

print("✅ Done! Dataset is ready in 'dataset/train' and 'dataset/validation'.")
