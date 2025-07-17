import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import pandas as pd
import os

# === Configuration ===
DATASET_PATH = "dataset"  # Folder with /D00, /D10, /D20, /D40 subfolders
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10
MODEL_PATH = "model/damage_classifier.h5"
METRICS_PATH = "model/training_metrics.csv"

# === Ensure output directory ===
os.makedirs("model", exist_ok=True)

# === Data Pipeline ===
train_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

train_gen = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    subset='training',
    class_mode='categorical',
    shuffle=True
)

val_gen = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    subset='validation',
    class_mode='categorical',
    shuffle=False
)

# === Model Architecture ===
base_model = EfficientNetB0(include_top=False, input_shape=(224, 224, 3), pooling='avg', weights='imagenet')
x = tf.keras.layers.Dense(128, activation='relu')(base_model.output)
output = tf.keras.layers.Dense(4, activation='softmax')(x)  # 4 damage types

model = tf.keras.models.Model(inputs=base_model.input, outputs=output)

# === Compile ===
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# === Callbacks ===
callbacks = [
    EarlyStopping(patience=3, restore_best_weights=True),
    ModelCheckpoint(MODEL_PATH, save_best_only=True)
]

# === Train ===
history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=EPOCHS,
    callbacks=callbacks
)

# === Save model again just in case ===
model.save(MODEL_PATH)

# === Export metrics for CI report ===
pd.DataFrame(history.history).to_csv(METRICS_PATH, index=False)

print(f"Training complete. Model saved to {MODEL_PATH}")
