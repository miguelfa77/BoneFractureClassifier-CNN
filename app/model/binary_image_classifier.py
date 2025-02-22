import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import keras
from PIL import Image
from keras.callbacks import CSVLogger
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Dense, Flatten, BatchNormalization, Dropout
from tensorflow import keras
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from utils.list_func import list_png_files
from utils.parse_func import parse_known, parse_unknown

class FractureImageClassifier:
    def __init__(self):
        """
        Creates datasets from existing directory files
        vars: 
        CNN: defines our Sequential model and layers
        """


        # mapping number with class
        self.classes = {0: 'not fractured', 1: 'fractured'}
        # define paths
        self.MODEL_PATH = '/Users/miguelfa/Desktop/BoneFractureClassifier-CNN/app/model/CNN-FractureImageClassifier.keras'
        self.MODEL_HISTORY_PATH = '/Users/miguelfa/Desktop/BoneFractureClassifier-CNN/app/model/training.log'
        self.data_dir = '/Users/miguelfa/Desktop/BoneFractureClassifier-CNN/app/model/data'
        self.train_dir = os.path.join(self.data_dir,'train')
        self.val_dir = os.path.join(self.data_dir,'val')
        self.test_dir = os.path.join(self.data_dir,'test')
        # read files into vars
        self.train_files, self.val_files, self.test_files = self.load_data()
        # list of files into tf.Dataset format
        self.train_dataset = self.create_dataset(self.train_files)
        self.val_dataset = self.create_dataset(self.val_files)
        self.test_dataset = self.create_dataset(self.test_files)

        self.CNN = keras.Sequential([Conv2D(32,(3,3),activation='relu',input_shape=(128,128,3)),
                                     MaxPooling2D(2,2),

                                     Conv2D(64,(3,3),activation='relu'),
                                     MaxPooling2D(2,2),

                                     Conv2D(128,(3,3),activation='relu'),
                                     MaxPooling2D(2,2),

                                     Conv2D(128,(3,3),activation='relu'),
                                     MaxPooling2D(2,2),

                                     Conv2D(128,(3,3),activation='relu'),
                                     MaxPooling2D(2,2),

                                     Flatten(),

                                     Dense(512,activation='relu'),

                                     Dense(1,activation='sigmoid')
                                     ])

        self.predictions = None

    def load_model(self, model_path='/Users/miguelfa/Desktop/BoneFractureClassifier-CNN/app/model/CNN-FractureImageClassifier.keras'):
        try:
            self.CNN = tf.keras.models.load_model(
                model_path, custom_objects=None, compile=True, safe_mode=True
                )
        except Exception as e:
            print(f'Failed to load model from path: {e}')
            
    def load_data(self):
        """
        Gets a list of png files from a directory of files
        returns: train_files, val_files, test_files
        """
        try:
            train_files = list_png_files(self.train_dir)
            val_files = list_png_files(self.val_dir)
            test_files = list_png_files(self.test_dir)
            return train_files, val_files, test_files
        except Exception as e:
            print(f'Failed to load/read image files: {e}')

    def create_dataset(self, files):
        """
        Converts a list of files into a tf.Dataset
        returns: dataset
        """
        try:
            # Creates dataset for each element in png list.
            dataset = tf.data.Dataset.from_tensor_slices(files)
            # Maps each dataset element to parse image function
            dataset = dataset.map(parse_known, num_parallel_calls=tf.data.experimental.AUTOTUNE)
            # buffered and batched
            dataset = dataset.shuffle(buffer_size=1000).batch(64).prefetch(tf.data.experimental.AUTOTUNE)
            return dataset
        except Exception as e:
            print(f'Failed to convert files into tf.Dataset: {e}')

    def train(self, train, validation):
        """
        Trains model, compiles and fits.
        params: 
        optimizer: adam,
        loss: binary_crossentropy,
        metrics: binary_accuracy 
        """
        # declare optimizer and loss function
        self.CNN.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['binary_accuracy'])
        # define log history
        csv_logger = CSVLogger(self.MODEL_HISTORY_PATH, separator=',', append=False)
        # train the model and validate
        training = self.CNN.fit(train,
                    validation_data=validation,
                    epochs=10,
                    callbacks=[csv_logger])
        # plot loss metrics and evaluate model performance on val set
        cnn_history = pd.DataFrame(training.history)
        cnn_history.loc[:, ['loss', 'val_loss']].plot()
        cnn_history.loc[:, ['binary_accuracy', 'val_binary_accuracy']].plot()

    def predict(self, dataset):
        """
        Predicts classes and labels
        predictions: sigmoid probability
        prediction_classes: label
        """
        try:
            # predict 0 or 1 ('not fracture' or 'fracture')
            self.predictions = self.CNN.predict(dataset)
            self.prediction_classes = np.where(self.predictions > 0.5, 'fractured', 'not fractured')
            return (self.predictions, self.prediction_classes)
        except Exception as e:
            print(f'Failed to make predictions: {e}')
        
    def evaluate(self, dataset):
        """
        Prints performance on dataset
        """    
        _, test_accuracy = self.CNN.evaluate(dataset)
        print(f"Test Accuracy: {test_accuracy}")



if __name__=="__main__":
    # create instance
    fic = FractureImageClassifier()

    # train/save or load model
    """
    fic.train(train=fic.train_dataset, validation=fic.val_dataset)
    fic.CNN.save(fic.MODEL_PATH)
    """
    fic.load_model(model=fic.MODEL_PATH)

    # read/parse image 
    filename = 'fracture5.jpeg'  # CHANGE THIS
    image_path = os.path.join(fic.data_dir,filename)
    image = parse_unknown(image_path)

    # make prediction
    prediction, prediction_class = fic.predict(image)  # CHANGE THIS
    print(prediction, prediction_class)

    # model evaluation
    fic.evaluate(fic.test_dataset)

    # show prediction
    plt.figure(figsize=(5,5))
    plt.title(f'{prediction}:{prediction_class}')
    plt.imshow(Image.open(image_path))
    plt.show()
    """
    plt.savefig(f'/Users/miguelfa/Desktop/BoneFractureClassifier-CNN/app/model/test_prediction_{filename}')
    """


