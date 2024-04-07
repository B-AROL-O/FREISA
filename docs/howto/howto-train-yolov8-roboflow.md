# Training YOLOv8 on Roboflow data set

This guide shows how to train a YOLOv8 model for object detection on a data set imported from Roboflow.
This guide assumes you set up your working environment as described in the [training environment setup guide](./howto-set-up-training-workstation.md).

## Requirements

- A PC running Linux (Ubuntu 22.04 LTS)
- Preferably, an [NVIDIA&trade;](https://nvidia.com/) GPU (or any other GPU that can be used for hardware acceleration in PyTorch)
  - If using a GPU, make sure to have the latest drivers installed.
- A running instance of JupyterLab (see [guide](./howto-set-up-training-workstation.md))
- Since the JupyterLab container can potentially be deployed on a remote server, make sure it is possible to connect to that server from your host machine.
- A valid [Roboflow](https://www.roboflow.com) account.
  - It is possible to use a pre-existing data set, but we will use a custom one.

## Preparing the data set

First, it is necessary to create a new data set on Roboflow, i.e., gather all images and tag the elements that should be recognized by the model.
To do so, log into Roboflow with your account and, in the left-hand-side menu, select your workspace.

Select “create new project” and choose the type of model, or choose an existing one.

When prompted to add images, either upload your own, or look for them among the free data sets already available on the website.
Roboflow allows to import images from public data sets on the website.
Just make sure to create the project beforehand, then you can browse existing data sets and select the images to be imported.

Then, annotate the images and split them in training/test/validation sets.
**This part is crucial!**
A good quality of the data and of annotations can make the difference in the final model performance.

Roboflow also allows to create different versions of the same data set by applying image processing and image augmentation techniques (rotations, addition of noise, filtering).
This can be useful to increase the number of images in the set, allowing for better training.

The data set on which to train the model is now ready to be exported.

## Importing the data set into the workspace

After preparing the data set, it is possible to train a selected model on the images.
Roboflow also allows to train models on their servers, but in this case we will instead use our computer to perform training.

On Roboflow, having selected the correct data set version on which to train the model, click on ‘Custom Train and Upload’, then select the desired model (YOLOv8 in this case) and then click on ‘Get Snippet’.
This will provide you with different possibilities on how to import the data set into your environment.

We suggest to import the data set from terminal (opening a terminal session inside Jupyter Lab and navigating to the right folder).
This will download the images on the server to be used for training, so make sure there is enough disk space for them.
When downloading the images from Roboflow, make sure to save them on the Docker volume that is bound to the container.
This way if for any reason you need to recreate the container you will not lose any data, and additionally, it will be possible to export the trained model more easily since it will be stored in the computer disk.

Then, simply copy-paste the command given by Roboflow and wait for the files to be downloaded.
Once the process is finished you should be able to see/navigate to the files in the Jupyter Lab file explorer.

## Launching the training

A Jupyter notebooc containing the code for training can be found at [this link](https://colab.research.google.com/github/roboflow-ai/notebooks/blob/main/notebooks/train-yolov8-object-detection-on-custom-dataset.ipynb), while the code used by us is in the [`training-yolo` folder] (../../code/training-yolo).

Relatively to the folder where the images have been downloaded to, the training results (model weights, graphs, validation results) can be found in the `runs/detect/train/` folder.

The weights of the best performing model (accuracy evaluated on the validation set) are in the file `runs/detect/train/weigths/best.pt`.
Those model parameters can then be exported and loaded to perform inference.

## References

- [Getting started with Roboflow](https://blog.roboflow.com/getting-started-with-roboflow/)
