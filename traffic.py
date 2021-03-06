import cv2
from cv2 import data
import numpy as np
import os
import sys
import tensorflow as tf
import time

from sklearn.model_selection import train_test_split
from tensorflow.python.keras.engine import input_spec

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.
    """

    # Empty list of images and labels
    images = []
    labels = []

    # Iterate over each folder in data_dir and each file in each folder
    for folder in os.listdir(data_dir):

        print("Loaded: ", os.path.join(data_dir, folder))
        
        for file in os.listdir(os.path.join(data_dir, folder)):
            
            image = os.path.join(data_dir, folder, file)
            image_array = cv2.imread(image)
            resized_image_array = cv2.resize(image_array, (IMG_WIDTH, IMG_HEIGHT))

            # Append the respective folder and array into labels and images
            labels.append(int(folder))
            images.append(resized_image_array)
    
    # Return the lists as a tuple
    return (images, labels)

def get_model():
    """
    Returns a compiled convolutional neural network model.
    """
    
    model = tf.keras.models.Sequential([

        # Get convolutional layer
        tf.keras.layers.Conv2D(
            32, (5, 5), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
        ),

        # Get MaxPooling layer
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

        tf.keras.layers.Conv2D(
            32, (3, 3), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
        ),

        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

        # Flatten for neural net
        tf.keras.layers.Flatten(),

        # Add hidden layer with dropout of 0.3
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dropout(0.3),

        # Add final output layer
        tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax"),
    ])

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model

if __name__ == "__main__":
    main()
