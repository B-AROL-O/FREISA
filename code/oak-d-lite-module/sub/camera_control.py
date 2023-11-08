import depthai as dai
import cv2
import blobconverter
import numpy as np
from datetime import datetime
import os
import sys
import time

from sub.config import DEBUG, VERB, CONF_THRESH_NN

"""
Camera control library
---
This library contains functions used for controlling the operation of 
the OAK-D lite camera.
"""


class VisionController:
    """
    VisionController
    ---
    Control the OAK-D lite camera, allowing to switch between different
    pipelines to execute different operations.

    ### Attributes
    - models (dict): dictionary containing as keys the model names, and as values dictionaries
    with the keys:
      - path: path of the JSON file of the model
      - n_classes: number of classes
      - classes_map: mapping between the classes and the associated index (list)
    - model_names (list): list containing the names of the models.
    - model_paths (list): list of paths where the corresponding model is found.
    - n_models (int): number of models
    - curr_model_ind (int): index (in the list of models) of the current active model
    if set to -1, no model is active.
    - pipelines (list): list of depthai.Pipeline objects associated with each model.

    ### Methods
    - __init__: constructor; it also initializes the pipelines (Depthai)
    given the paths to the models to be used
    -
    """

    def __init__(self, models: dict):
        """
        Initialize VisionController object.

        ### Input parameters
        - models:
        TODO
        """
        if not isinstance(models, dict):
            raise ValueError("The models must be stored inside a dictionary!")

        self.models = models
        self.model_names = list(models.keys())
        self.model_paths = [str(models[k]["path"]) for k in self.model_names]
        self.n_models = len(self.model_names)
        self.current_model_ind = -1

        self.pipelines = []
        self._initPipelines()

    def _initPipelines(self):
        """Initialize the `depthai.Pipeline` objects for each model.
        The method modifies the attribute `pipelines`."""
        for i in range(self.n_models):
            new_pipeline = dai.Pipeline()

            # Camera node
            cam_rgb = new_pipeline.create(dai.node.ColorCamera)
            cam_rgb.setPreviewSize(416, 416)
            cam_rgb.setInterleaved(False)
            cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

            # YOLO detection model
            yolo_nn = new_pipeline.create(dai.node.YoloDetectionNetwork)
            yolo_nn.setBlobPath(self.model_paths[i])
            yolo_nn.setConfidenceThreshold(CONF_THRESH_NN)
            # Settings:
            yolo_nn.setNumClasses(self.models[self.model_names[i]]["n_classes"])
            yolo_nn.setCoordinateSize(4)
            yolo_nn.setAnchors([10, 14, 23, 27, 37, 58, 81, 82, 135, 169, 344, 319])
            yolo_nn.setAnchorMasks({"side26": [1, 2, 3], "side13": [3, 4, 5]})
            yolo_nn.setIouThreshold(0.5)
            yolo_nn.setNumInferenceThreads(2)
            yolo_nn.input.setBlocking(False)

            cam_rgb.preview.link(yolo_nn.input)  # Camera is NN input

            xout_rgb = new_pipeline.create(dai.node.XLinkOut)
            xout_rgb.setStreamName("rgb")
            cam_rgb.preview.link(xout_rgb.input)  # Output RGB (debugging)

            xout_nn = new_pipeline.create(dai.node.XLinkOut)
            xout_nn.setStreamName("inference")
            yolo_nn.out.link(xout_nn.input)  # Output inference results

            # Add this new pipeline to the list of pipelines
            self.pipelines.append(new_pipeline)

    # +-----------+
    # + UTILITIES
    # +-----------+

    def current_model(self):
        """Get the name of the current active model."""
        return self.model_names[self.current_model_ind]


if __name__ == "__main__":
    pass
