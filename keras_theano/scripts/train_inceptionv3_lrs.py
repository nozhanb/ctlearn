import argparse
import os
from shutil import copyfile
import sys

import numpy as np

from keras.models import Model
from keras.optimizers import SGD, RMSprop, Nadam
from keras.layers.core import Dense, Flatten
from keras.applications.inception_v3 import InceptionV3
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import CSVLogger, ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

# pSCT image dimensions
image_x_dim= 120
image_y_dim= 120

#number of samples
training_samples = 20000
validation_samples = 10000

# parse command line arguments

parser = argparse.ArgumentParser(description='Train a given network on data from the indicated directories. Produce log file (.csv) for training run and save plots.')
parser.add_argument('--weights', help='path to saved model weights')
parser.add_argument('train_data_dir', help='path to training data directory (containing subdir for each type)')
parser.add_argument('val_data_dir', help='path to validation data directory (containing subdir for each type)')
parser.add_argument('run_name', help='name of run (used to name log file, plot images,etc)')
parser.add_argument('save_dir', help='directory to save run files in (directory must exist)')
parser.add_argument('epochs',help='number of epochs to train for', type=int)
parser.add_argument('--batch_size',help='image generator batch size', default=96, type=int)
#parser.add_argument('--l',help='log results to file',action="store_true")
#parser.add_argument('--c',help='save checkpoints',action="store_true")

args = parser.parse_args()

train_data_path = os.path.abspath(args.train_data_dir)
val_data_path = os.path.abspath(args.val_data_dir)

## Load saved weights
#if args.weights is not None:
#    model_weights_path = os.path.abspath(args.weights)
#    model.load_weights(model_weights_path)

# Create required directories
############################

abs_path = os.path.normcase(os.path.abspath(args.save_dir))
run_dir = os.path.join(abs_path, args.run_name)
checkpoint_dir = os.path.join(run_dir, 'checkpoints')

if not os.path.exists(run_dir):
    os.makedirs(run_dir)

if not os.path.exists(checkpoint_dir):
    os.makedirs(checkpoint_dir)

#count number of images in directories, count number of classes
##############################################################

#data augmentation/preprocessing
################################

#processing training data
training_preprocess = ImageDataGenerator(
        horizontal_flip=False,
        vertical_flip=False)

#processing validation data
validation_preprocess = ImageDataGenerator()

#generator for training data
training_generator = training_preprocess.flow_from_directory(
        train_data_path,
        target_size=(image_x_dim*2, image_y_dim*2),
        color_mode='rgb',
        batch_size=args.batch_size,
        class_mode='binary')

#generator for validation data
validation_generator = validation_preprocess.flow_from_directory(
        val_data_path,
        target_size=(image_x_dim*2, image_y_dim*2),
        color_mode='rgb',
        batch_size=args.batch_size,
        class_mode='binary')


#train model
############

checkpoint = ModelCheckpoint(os.path.join(checkpoint_dir,
    args.run_name + '-{epoch:04d}-{val_loss:.5f}.h5'),
    monitor='val_loss',
    verbose=0,
    save_best_only=False,
    save_weights_only=True,
    mode='auto')
earlystoploss = EarlyStopping(monitor='val_loss', min_delta=0.00001, patience=10, verbose=0, mode='auto')
earlystopacc = EarlyStopping(monitor='val_binary_accuracy', min_delta=0.001, patience=5, verbose=0, mode='auto')
reducelr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5, verbose=0, mode='auto', epsilon=0.0001, cooldown=0, min_lr=0)

num_samples = 20

lrs = np.random.uniform(0.00009,0.0004,num_samples)
#lrs = 10**lrs
beta_1s = np.random.uniform(0.88,0.95,num_samples)
beta_2s = np.random.uniform(0.92,1.0,num_samples)
accs = []
samples = []

for lr,beta_1,beta_2 in zip(lrs,beta_1s,beta_2s):
    # Create the InceptionV3 model
    initial_model = InceptionV3(
            include_top=False, 
            weights=None, 
            input_shape=(3, image_x_dim*2, image_y_dim*2), 
            pooling=None)
    last = initial_model.output
    x = Flatten()(last)
    prediction = Dense(1, activation='sigmoid', name='prediction')(x)
    model = Model(initial_model.input, prediction)
    
    model.compile(
            optimizer=Nadam(lr=lr,beta_1=beta_1,beta_2=beta_2,epsilon=1e-08, schedule_decay=0.004),
            loss='binary_crossentropy',
            metrics=['binary_accuracy'])
    
    logger = CSVLogger(os.path.join(run_dir, args.run_name + '_' + '{:.7f}_{:f}_{:f}'.format(lr,beta_1,beta_2) + '.log'),
            separator=',', append=True)
    history = model.fit_generator(
            generator=training_generator,
            steps_per_epoch=int(training_samples/args.batch_size),
            epochs=args.epochs,
            callbacks=[logger],
            validation_data=validation_generator,
            validation_steps=int(validation_samples/args.batch_size),
            class_weight='auto')
    accs.append(history.history["val_binary_accuracy"][-1])

sorted_results = [(lr,beta_1,beta_2, acc) for (acc, lr, beta_1, beta_2) in sorted(zip(accs, lrs, beta_1s, beta_2s), reverse=True)]
for sorted_result in sorted_results:
    print(sorted_result)

