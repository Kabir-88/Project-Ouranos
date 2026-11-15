"""Small U-Net for terrain segmentation. Same architecture as notebooks/train_kaggle.ipynb."""

import tensorflow as tf
from tensorflow.keras import layers

from src.config import IMG_SIZE, NUM_CLASSES


def conv_block(x, filters):
    x = layers.Conv2D(filters, 3, padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(filters, 3, padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    return x


def build_unet(img_size=IMG_SIZE, num_classes=NUM_CLASSES, base=16):
    """Input: grayscale image (img_size, img_size, 1) in [0, 1]. Output: per-pixel class probabilities."""
    inputs = layers.Input((img_size, img_size, 1))

    c1 = conv_block(inputs, base)
    p1 = layers.MaxPooling2D()(c1)
    c2 = conv_block(p1, base * 2)
    p2 = layers.MaxPooling2D()(c2)
    c3 = conv_block(p2, base * 4)
    p3 = layers.MaxPooling2D()(c3)

    b = conv_block(p3, base * 8)

    u3 = layers.UpSampling2D()(b)
    u3 = conv_block(layers.Concatenate()([u3, c3]), base * 4)
    u2 = layers.UpSampling2D()(u3)
    u2 = conv_block(layers.Concatenate()([u2, c2]), base * 2)
    u1 = layers.UpSampling2D()(u2)
    u1 = conv_block(layers.Concatenate()([u1, c1]), base)

    outputs = layers.Conv2D(num_classes, 1, activation="softmax")(u1)
    return tf.keras.Model(inputs, outputs, name="terrain_unet")


def load_model(path):
    return tf.keras.models.load_model(path, compile=False)
