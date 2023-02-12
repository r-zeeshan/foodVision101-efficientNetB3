<h1>FoodVision</h1>
	This code is a Food Classification system that uses TensorFlow and TensorFlow Datasets. It uses a pre-trained EfficientNetB3 model and trains it on the food101 dataset. The code performs various pre-processing operations on the dataset and fine-tunes the pre-trained model to classify images of food into 101 classes.

<h1>Clone this repository</h1>
`git clone https://github.com/r-zeeshan/foodVision101-efficientNetB3.git`

<h1>Setup</h1>
	The code starts by checking the GPU and downloading the helper functions from a GitHub repository. The food101 dataset is then loaded and a sample image is plotted.

<h1>Preprocessing</h1>
	The images in the dataset are preprocessed by resizing them to a specified shape and converting the data type to float32. The preprocessed images are then batched and the dataset is prepared.

<h1>Callbacks</h1>
	The code sets up several callbacks to be used during the training of the model. These include TensorBoard, Model Checkpoint, Early Stopping, and ReduceLROnPlateau.

<h1>Mixed Precision Training</h1>
	The code sets up mixed precision training by using the mixed_float16 policy from TensorFlow's mixed_precision module.

<h1>Model Building</h1>
	The code builds the model using the pre-trained EfficientNetB3 model and adds some additional layers for fine-tuning. The model is then trained on the preprocessed dataset using the specified callbacks.

<h1>Conclusion</h1>
	This code provides a complete end-to-end solution for food image classification using TensorFlow and TensorFlow Datasets. The code performs various pre-processing operations, sets up callbacks, and trains a deep learning model for food image classification.
