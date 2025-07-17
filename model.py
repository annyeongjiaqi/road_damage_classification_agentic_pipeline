import tensorflow as tf
import numpy as np
from PIL import Image

model = tf.keras.models.load_model("damage_classifier.h5")
classes = ['D00', 'D10', 'D20', 'D40']

def predict_damage(image: Image.Image):
    img = image.resize((224, 224))
    img = np.array(img) / 255.0
    img = np.expand_dims(img, axis=0)
    pred = model.predict(img)[0]
    return dict(zip(classes, pred))
