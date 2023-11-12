import depthai as dai
import cv2
import blobconverter
import numpy as np
from datetime import datetime
import json
import os
import sys
import threading
import time

from .config import (
    DEBUG,
    VERB,
    CONF_THRESH_NN,
    EXTENDED_DISPARITY,
    SUBPIXEL,
    LR_CHECK,
)
from .utilities import frameNorm

"""
Camera control library
---
This library contains functions used for controlling the operation of 
the OAK-D lite camera.

TODO:
- Find way to import class-label mapping
- Fix depth evaluation
- Import YOLOv8 model
- Test locally
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
    - json_paths (list): list of paths where the jsons of the models are found.
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
        - models: dict containing as keys the model names, and as values dict with model_path
        and json_path
        TODO
        """
        if not isinstance(models, dict):
            raise ValueError("The models must be stored inside a dictionary!")

        self.models = models
        self.model_names = list(models.keys())
        self.model_paths = [str(models[k]["model_path"]) for k in self.model_names]
        self.json_paths = [str(models[k]["json_path"]) for k in self.model_names]
        self.model_settings = []  # Will contain the JSONs stored as dict
        self.model_mappings = []  # Will contain labels list
        self.n_models = len(self.model_names)
        self.current_model_ind = -1

        self.pipelines = []
        self._initPipelines()

        # TODO: add other possible variables (e.g., store outputs of running models)
        self._thread_started = False
        self.vision_thread = None  # Placeholder for the threading.Thread object

        # The last inference result consists in a dict
        self.last_inference_result = {}

    def _initPipelines(self):
        """Initialize the `depthai.Pipeline` objects for each model.
        The method modifies the attribute `pipelines`."""
        for i in range(self.n_models):
            new_pipeline = dai.Pipeline()

            # Get JSON with configuration
            with open(self.json_paths[i]) as f:
                curr_settings = json.load(f)
                self.model_settings.append(curr_settings)

            self.model_mappings.append(curr_settings["mappings"]["labels"])
            input_size = curr_settings["nn_config"]["input_size"].split("x")
            input_size = [int(n) for n in input_size]

            # Camera node
            cam_rgb = new_pipeline.create(dai.node.ColorCamera)
            cam_rgb.setPreviewSize(input_size[0], input_size[1])
            cam_rgb.setInterleaved(False)
            cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
            cam_rgb.setFps(40)

            # YOLO detection model (extract info from JSON config)
            yolo_nn = new_pipeline.create(dai.node.YoloDetectionNetwork)
            yolo_nn.setBlobPath(self.model_paths[i])
            yolo_nn.setConfidenceThreshold(
                curr_settings["nn_config"]["NN_specific_metadata"][
                    "confidence_threshold"
                ]
            )
            # Settings:
            yolo_nn.setNumClasses(
                curr_settings["nn_config"]["NN_specific_metadata"]["classes"]
            )
            yolo_nn.setCoordinateSize(
                curr_settings["nn_config"]["NN_specific_metadata"]["coordinates"]
            )
            yolo_nn.setAnchors(
                curr_settings["nn_config"]["NN_specific_metadata"]["anchors"]
            )
            yolo_nn.setAnchorMasks(
                curr_settings["nn_config"]["NN_specific_metadata"]["anchor_masks"]
            )
            yolo_nn.setIouThreshold(
                curr_settings["nn_config"]["NN_specific_metadata"]["iou_threshold"]
            )
            yolo_nn.setNumInferenceThreads(2)
            yolo_nn.input.setBlocking(False)

            cam_rgb.preview.link(yolo_nn.input)  # Camera is NN input

            # Depth estimation
            mono_l = new_pipeline.create(dai.node.MonoCamera)
            mono_l.setCamera("left")
            mono_l.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

            mono_r = new_pipeline.create(dai.node.MonoCamera)
            mono_r.setCamera("right")
            mono_r.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

            stereo = new_pipeline.create(dai.node.StereoDepth)
            stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
            # Options: MEDIAN_OFF, KERNEL_3x3, KERNEL_5x5, KERNEL_7x7 (default)
            stereo.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
            stereo.setLeftRightCheck(LR_CHECK)
            stereo.setExtendedDisparity(EXTENDED_DISPARITY)
            stereo.setSubpixel(SUBPIXEL)

            # Link mono cameras to stereo view
            mono_l.out.link(stereo.left)
            mono_r.out.link(stereo.right)

            ## NOTE: if on, the program breaks unless the queue is used
            # xout_rgb = new_pipeline.create(dai.node.XLinkOut)
            # xout_rgb.setStreamName("rgb")
            # cam_rgb.preview.link(xout_rgb.input)  # Output RGB (debugging)

            # Link inference node
            xout_nn = new_pipeline.create(dai.node.XLinkOut)
            xout_nn.setStreamName("inference")
            yolo_nn.out.link(xout_nn.input)  # Output inference results

            # Output stereo depth - TODO: check if `depth` is the best output
            xout_stereo = new_pipeline.create(dai.node.XLinkOut)
            xout_stereo.setStreamName("depth")
            stereo.depth.link(xout_stereo.input)

            # Add this new pipeline to the list of pipelines
            self.pipelines.append(new_pipeline)

    def selectModel(self, new_model: str | int):
        """
        Change the currently active model.

        This method triggers the change in the pipeline which is being ran.

        ### Input parameters
        - new_model: string or integer number indicating the new model to be launched.
        If it is a string, it is the name of the model; if it is an int, it is the
        index of the model in the list.
        """
        if isinstance(new_model, str):
            if new_model.lower() not in self.model_names:
                raise ValueError(f"Model {new_model} does not exist!")
            else:
                mod = new_model
                mod_ind = self.model_names.index(new_model)
        elif isinstance(new_model, int):
            mod = self.model_names[new_model]
            mod_ind = new_model
        else:
            raise ValueError("The new model should be a string or an int")

        # Stop the thread
        if self._thread_started:
            self.vision_thread.join()

        # Change the active model info
        self.current_model_ind = mod_ind

        # Restart the thread
        self.vision_thread = threading.Thread(
            target=self._runInferencePipeline(
                self.pipelines[self.current_model_ind], pipeline_name=mod
            )
        )

        self.vision_thread.start()

    def _runInferencePipeline(
        self, pipeline: dai.Pipeline, pipeline_name: str, sync_frame: bool = True
    ):
        """
        Run the specified pipeline.
        This method is only called by `selectModel`, and should be ran as an
        independent thread.

        ### Input parameters
        - pipeline: the pipeline to be ran
        - pipeline_name: the name (string) of the pipeline (for packaging results)
        """
        t_start = time.time()

        with dai.Device(pipeline) as device:
            # Define queue for nn output - blocking=False will make only the most recent info available
            queue_nn = device.getOutputQueue(
                name="inference", maxSize=1, blocking=False
            )
            # Define queue for depth
            queue_depth = device.getOutputQueue(name="depth", maxSize=1, blocking=False)

            # Initialize placeholders for results:
            depth_frame = None  # Containing the output of the camera block
            detections = []  # Containing the inference results
            distances = []

            in_nn = None
            in_depth = None

            # Do the thing
            while True:
                ts = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
                inf_result_new = {}
                inf_result_new["detections"] = []
                inf_result_new["timestamp"] = ts

                if sync_frame:
                    in_nn = queue_nn.get()
                    in_depth = queue_depth.get()
                else:
                    in_nn = queue_nn.tryGet()
                    in_depth = queue_depth.tryGet()

                if in_nn is not None:
                    # depth_frame should contain the distances for each pixel
                    depth_frame = in_depth.getFrame()
                    for det in in_nn.detections:
                        x1, y1, x2, y2 = (
                            int(det.xmin),
                            int(det.ymin),
                            int(det.xmax),
                            int(det.ymax),
                        )
                        det_centroid = (0.5 * (x1 + x2), 0.5 * (y1 + y2))
                        # TODO: improve distance evaluation
                        det_dist = depth_frame

                    # Package solution
                    inf_result_new["detections"].append(
                        {
                            "position": det_centroid,
                            "depth": det_dist,
                            "label": det.label,
                            "class": "",
                        }  # FIXME: add conversion to class label
                    )

                # Need to place this here so that if no objects are found, the
                # program will return an empty solution
                self.last_inference_result = inf_result_new

                # TODO: Add distance estimation

    # +-----------+
    # + UTILITIES
    # +-----------+

    def getCurrentModelName(self):
        """Get the name of the current active model."""
        return self.model_names[self.current_model_ind]


if __name__ == "__main__":
    # Init the dictionary
    script_dir = os.path.dirname(__file__)
    models_folder = os.path.join(script_dir, "..", "models")
    mod = {}
    mod["trunk"] = {
        "model_path": os.path.join(models_folder, "trunk", "trunk_yolo.pt"),
        "json_path": os.path.join(models_folder, "trunk", "trunk_yolo.json"),
    }
    vc = VisionController()
