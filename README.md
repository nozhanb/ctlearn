# CTLearn: Deep Learning for IACT Analysis

[![Build Status](https://travis-ci.org/ctlearn-project/ctlearn.svg?branch=master)](https://travis-ci.org/ctlearn-project/ctlearn) [![Coverage Status](https://coveralls.io/repos/github/ctlearn-project/ctlearn/badge.svg?branch=master)](https://coveralls.io/github/ctlearn-project/ctlearn?branch=master) [![Code Health](https://landscape.io/github/ctlearn-project/ctlearn/master/landscape.svg?style=flat)](https://landscape.io/github/ctlearn-project/ctlearn/master)


Deep learning models for IACT event analysis and classification. Designed to work with [CTA](https://www.cta-observatory.org/) (the Cherenkov Telescope Array) and [VERITAS](https://veritas.sao.arizona.edu/) data.

## Example

The following plots were produced with ctlearn v0.1 using the "Basic" single-telescope classification model to classify gamma-ray and proton showers using CTA prod3b simulated data after training for ~4.5 hours.

![Loss](https://github.com/ctlearn-project/ctlearn/blob/master/misc/images/v0_1_benchmark_loss.png)
![Accuracy](https://github.com/ctlearn-project/ctlearn/blob/master/misc/images/v0_1_benchmark_accuracy.png)
![AUC](https://github.com/ctlearn-project/ctlearn/blob/master/misc/images/v0_1_benchmark_auc.png)

## Installation

### Package cloning w/ Git  (Recommended)

Clone CTLearn repository with:

```bash
mkdir /path/to/ctlearn; cd /path/to/ctlearn
git clone https://github.com/ctlearn-project/ctlearn.git
```

### Package Install w/ Anaconda

Setup Anaconda environment with:

```bash
conda config --add channels conda-forge
conda create -n [ENV_NAME] --file requirements-[mode].txt
source activate [ENV_NAME]
```

Where [mode] can be either 'cpu' or 'gpu', denoting the TensorFlow version to be installed. Prior to installing the GPU version of TensorFlow please verify that your system fulfills all the necessary requirements [here](https://www.tensorflow.org/install/install_linux#NVIDIARequirements).

Install package into the conda environment with pip:

```bash
/path/to/anaconda/install/envs/[ENV_NAME]/bin/pip install .
```

where /path/to/anaconda/install is the path to your anaconda installation directory and ENV\_NAME is the name of your environment. The path can be omitted if pip is called from the environment created above.

NOTE for developers: If you wish to fork/clone the respository and make changes to any of the ctlearn modules, the package should be reinstalled for the changes to take effect.

The path to the environment directory for the environment you wish to install into can be found quickly by running

```bash
conda env list
```

## Dependencies

- Python 3.6
- Tensorflow 1.8
- Pytables
- Numpy
- OpenCV
- ConfigObj
- SciPy

## Configuration

All options for training a model are set by a single configuration file. 
See example_config.ini for an explanation of all available options.

**Data**
The only currently accepted data format is HDF5/Pytables.
A file list containing the paths to a set of HDF5 files containing the data must be provided. The [ImageExtractor](https://github.com/cta-observatory/image-extractor) package is available to process, calibrate, and write CTA simtel files into the HDF5 format required by the scripts here. HDF5 files should be in the standard format specified by ImageExtractor.

For instructions on how to download the full pre-processed Prod3b dataset in ImageExtractor HDF5 format, see the wiki page [here](https://forge.in2p3.fr/projects/cta_analysis-and-simulations/wiki/Machine_Learning_for_Event_Reconstruction). (NOTE: requires a CTA account). 

**Data Processing**
Because the size of the full dataset may be very large, only a set of event indices is held in memory.
During each epoch of training, a specified number of event examples is randomly drawn from the training dataset.
Until the total number is reached, batches of a specified size are loaded and used to train the model.
Batch loading of data may be parallelized using a specified number of threads.
After each training epoch, the model is evaluated on the validation set.

**Model**
Several higher-level model types are provided to train networks for single-telescope classification (single_tel_model) and array (multiple image) classification (variable_input_model, cnn_rnn_model)

Available CNN Blocks: Basic, AlexNet, MobileNet, ResNet, DenseNet

Available Network Heads: AlexNet (fully connected telescope combination), AlexNet (convolutional telescope combination), MobileNet, ResNet, Basic (fully connected telescope combination), Basic (convolutional telescope combination)

**Training**
Training hyperparameters including the learning rate and optimizer can be set in the configuration file.

**Logging**
Tensorflow checkpoints and summaries are saved to the specified model directory, as is a copy of the configuration file.

## Usage

To train a model, run `python train.py myconfig.ini`. 
The following flags may be set: `--debug` to set DEBUG logging level, `--log_to_file` to save logger messages to a file in the model directory.
The model's progress can be viewed in real time using Tensorboard: `tensorboard --logdir=/path/to/my/model_dir`.

## Package Removal

### Package Removal w/ Anaconda

If the package was installed into a virtual environment follow the instructions below to remove the virtual environment and all the packages for the dependencies:

```bash
conda remove --name [ENV_NAME] --all
```

To completely remove CTLearn from your system do:

```bash
rm -f /path/to/ctlearn
```

Where /path/to/ctlearn is the directory CTLearn was downloaded into in the first place.


## Links

- [Cherenkov Telescope Array (CTA)](https://www.cta-observatory.org/)
- [ImageExtractor](https://github.com/cta-observatory/image-extractor) 
