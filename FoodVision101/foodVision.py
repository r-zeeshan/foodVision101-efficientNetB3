# -*- coding: utf-8 -*-
"""FoodVision.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OcMpOl0-6QUo8Dp8VYJ3e5YSVXDIRxLo

## Checking the GPU
"""

!nvidia-smi

# from google.colab import drive
# drive.mount('/content/drive')

"""## Getting the helper functions"""

!wget https://raw.githubusercontent.com/r-zeeshan/deep-learning/main/helper_functions.py

"""## Get Tensorflow datasets"""

import tensorflow_datasets as tfds

(train_data, test_data), ds_info = tfds.load(name="food101",
                                             split=["train", "validation"],
                                             shuffle_files=False,
                                             as_supervised=True,
                                             with_info=True)

ds_info.features

class_names = ds_info.features["label"].names
class_names[:5]

"""## Becoming One with the Data"""

# Take one sample of the training data
train_one_sample = train_data.take(1)

for image, label in train_one_sample:
    print(f"""
    Image Shape: {image.shape}
    Image dtype : {image.dtype}
    Target class : {label}
    Class name : {class_names[label.numpy()]}
    """)

import tensorflow as tf
# What are minimum and maximum values of the "image"
tf.reduce_min(image), tf.reduce_max(image)

"""## Plot an Image from Tensorflow Dataset"""

import matplotlib.pyplot as plt
plt.imshow(image)
plt.title(class_names[label.numpy()])
plt.axis(False)

"""## Creating preprocessing functions for our data"""

# Making a function for preprocessing images
def preprocess_image(image, label, img_shape=224):
    image = tf.image.resize(image, [img_shape, img_shape])
    return tf.cast(image,tf.float32), label

preprocessed_img = preprocess_image(image, label)[0]
plt.imshow(preprocessed_img/255.)
plt.title(class_names[label])
plt.axis(False)

"""## Batch and Prepare Dataset"""

# Map preprocessing function on training data (and parallelize it)
train_data = train_data.map(map_func=preprocess_image,
                            num_parallel_calls=tf.data.AUTOTUNE)
train_data = train_data.shuffle(1000).batch(32).prefetch(tf.data.AUTOTUNE)

# Map preprocessing function to the test dataset
test_data = test_data.map(map_func=preprocess_image,
                          num_parallel_calls=tf.data.AUTOTUNE)
test_data = test_data.batch(32).prefetch(tf.data.AUTOTUNE)

train_data, test_data

"""## Creating the modelling callbacks"""

# from google.colab import drive
# drive.mount('/content/drive')

# Tensorboard Callback
from my_helper_functions import create_tensorboard_callback

# Model Checkpoint Callback
checkpoint_path = "/content/drive/MyDrive/new_model_checkpoints/cp.ckpt"
model_checkpoint = tf.keras.callbacks.ModelCheckpoint(checkpoint_path,
                                                       monitor="val_accuracy",
                                                       save_best_only=True,
                                                       save_weights_only=True,
                                                       verbose=0,
                                                      save_freq='epoch')

# Early Stopping
early_stopping = tf.keras.callbacks.EarlyStopping(monitor="val_loss",
                                                  patience=3)

# Reduce Learning rate
reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss",
                                                 factor=0.2,
                                                 patience=2,
                                                 verbose=1,
                                                 min_lr=1e-7)

# Creating callbacks list
callbacks = [early_stopping, reduce_lr, model_checkpoint,
             create_tensorboard_callback("food_vision", "efficientnetb3")]

"""## Setup Mixed Precision Training"""

from tensorflow.keras import mixed_precision
mixed_precision.set_global_policy(policy="mixed_float16")

"""## Building an EfficientNetB3 Fine Tuning Model"""

base_model = tf.keras.applications.EfficientNetB1(include_top=False)
base_model.trainable=True

"""## Creating a food vision model"""

from tensorflow.keras import layers

inputs = layers.Input(shape=(224, 224, 3), name="input_layer")
x = base_model(inputs)
x = layers.GlobalAveragePooling2D(name="GlobalAveragePooling2D")(x)
x = layers.Dense(len(class_names))(x)
outputs = layers.Activation("softmax", dtype=tf.float32, name="output_layer")(x)

model = tf.keras.Model(inputs, outputs)

model.load_weights("/content/drive/MyDrive/model_checkpoints/cp.ckpt")

# Compiling the model
model.compile(loss="sparse_categorical_crossentropy",
              optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
              metrics=["accuracy"])

"""## Checking the summary of my model """

model.summary()

"""## Fitting the model"""

efficientnet_b3_history = model.fit(train_data,
                                    epochs=50,
                                    steps_per_epoch=len(train_data),
                                    validation_data=test_data,
                                    validation_steps=int(0.1 * len(test_data)),
                                    callbacks=callbacks)

model.save("/content/drive/MyDrive/models/eff_net_b1.h5")
model.save("/content/drive/MyDrive/models/eff_net_b1_model")

model.evaluate(test_data)

preds = model.predict(test_data)

from my_helper_functions import make_predictions, get_class_f1_scores, plot_f1_scores, make_confusion_matrix

def lake_predictions(model, data):
    """
    Makes predictions on the data using the given model.

    Args:
        model (obj) : Trained model
        data (BatchDataset) : Data to make predictions on.

    Returns: 
        y_labels and pred_classes of the given data.

    Example usage:
        make_predictions(model = cnn_model,
                         data = test_data)
    """
    # Make Predictions on test data using the given model
    pred_prob = model.predict(data)

    # Get pred classes of each label
    pred_classes = pred_prob.argmax(axis=1)

    # To get our test labels we need to unravel our test data batch Dataset
    y_labels = []
    for images, labels in data.unbatch():
        y_labels.append(labels.numpy())

    return y_labels, pred_classes

y_labels, pred_classes = lake_predictions(model, test_data)

f1_scores = get_class_f1_scores(y_labels, class_names, pred_classes)

plot_f1_scores(f1_scores)

make_confusion_matrix(y_labels, pred_classes, class_names, (100,100), 20, savefig=True)

"""## Predicting on Custom Images"""

!wget https://raw.githubusercontent.com/r-zeeshan/deep-learning/main/helper_functions.py

from my_helper_functions import load_and_prep_image , pred_and_plot

import tensorflow as tf
def load_and_prep_image(filename, img_shape=224, scale=False):
    """
    Reads in an image from filename, turns it into a tensor and reshapes into
    (224, 224, 3).
    Parameters
    ----------
    filename (str): string filename of target image
    img_shape (int): size to resize target image to, default 224
    scale (bool): whether to scale pixel values to range(0, 1), default True
    """
    # Read in the image
    img = tf.io.read_file(filename)
    # Decode it into a tensor
    img = tf.image.decode_jpeg(img)
    # Resize the image
    img = tf.image.resize(img, [img_shape, img_shape])
    if scale:
        # Rescale the image (get all values between 0 and 1)
        return img/255.
    else:
        return img

def pred_and_plot(model, filename, class_names):
    """
    Imports an image located at filename, makes a prediction on it with
    a trained model and plots the image with the predicted class as the title.
    """
    # Import the target image and preprocess it
    img = load_and_prep_image(filename)

    # Make a prediction
    pred = model.predict(tf.expand_dims(img, axis=0))

    # Get the predicted class
    if len(pred[0]) > 1: # check for multi-class
        pred_class = class_names[pred.argmax()] # if more than one output, take the max
    else:
        pred_class = class_names[int(tf.round(pred)[0][0])] # if only one output, round

    # Plot the image and predicted class
    plt.imshow(img/255.)
    plt.title(f"Prediction: {pred_class}")
    plt.axis(False);

pred_and_plot(model, "download (10).jpeg", class_names)