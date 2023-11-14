import json
import os
import threading
import time
import typing
from datetime import datetime

import depthai as dai

from sub.config import EXTENDED_DISPARITY, LR_CHECK, SUBPIXEL, VERB

"""
Camera control library
---
This library contains functions used for controlling the operation of
the OAK-D lite camera.

TODO:
- Fix depth evaluation
"""


class VisionController:
    """
    VisionController
    ---
    Control the OAK-D lite camera, allowing to switch between different
    pipelines to execute different operations.

    ### Attributes

    #### Public
    - models (dict): dictionary containing as keys the model names, and as values dictionaries
    with the keys:
      - model_path: path of the .blob file of the model
      - json_path: path of the JSON file of the model
    - model_names (list): list containing the names of the models.
    - model_paths (list): list of paths where the corresponding model is found.
    - json_paths (list): list of paths where the jsons of the models are found.
    - model_settings (list): list containing the dicts obtained from the JSON configuration
    files
    - model_mappings (list): list containing the mappings of each model (sublists)
    - n_models (int): number of models
    - curr_model_ind (int): index (in the list of models) of the current active model
    if set to -1, no model is active.
    - pipelines (list): list of depthai.Pipeline objects associated with each model.
    - info_dict (dict): dictionary containing the models' information that have been retrieved
    from the JSON configuration files passed at initialization
    - vision_thread (threading.Thread): thread on which the currently active pipeline is being
    executed; initialized to None at instantiation
    - last_inference_result (dict): result of the last inference performed by the currently
    active model; it contains the model name, the timestamp, and the detection information.
    - time_resolution (float): time step (in seconds) at which inference is performed.

    #### Private
    - _thread_started (bool): true if currently a pipeline is being executed (on separate
    thread)
    - _thread_stop (bool): when set to True, it will interrupt the currently active pipeline

    ### Methods
    - __init__: constructor; it also initializes the pipelines (Depthai) given the paths to
    the models to be used
    - _initPipelines: create the depthai.Pipeline objects for each of the models
    - selectModel: change the currently active inference model (modify active thread)
    - _runInferencePipeline: run a specific pipeline; this method should always be ran as an
    independent thread, and can only be stopped by modifying the value of _thread_stop
    - buildInfoDict: put together the dictionary containing the information of all available
    models
    - getCurrentModelName: get the name of the currently active model; will return an empty
    string if no model has been launched
    - stopThreads: stop the thread of the active pipeline for soft shutdown
    """

    script_folder = os.path.dirname(__file__)

    def __init__(self, models: dict, time_resolution: float = 1):
        """
        Initialize VisionController object.

        ### Input parameters
        - models: dict containing as keys the model names, and as values dict with 'model_path'
        and 'json_path' keys containing the paths of the `.blob` model and of the `.json`
        configuration file for each model; NOTE: the paths should be relative to the folder where
        this file is stored!
        - time_resolution: time interval between two inference results in seconds (default: 0.5 s)
        """
        if not isinstance(models, dict):
            raise ValueError("The models must be stored inside a dictionary!")

        self.models = models
        self.model_names = list(models.keys())
        self.model_paths = [
            os.path.join(self.script_folder, str(models[k]["model_path"]))
            for k in self.model_names
        ]
        self.json_paths = [
            os.path.join(self.script_folder, str(models[k]["json_path"]))
            for k in self.model_names
        ]
        self.model_settings: list[dict] = []  # Will contain the JSONs stored as dict
        self.model_mappings: list[list] = []  # Will contain labels list
        self.n_models = len(self.model_names)
        self.current_model_ind = -1

        self.pipelines: list[dai.Pipeline] = []
        self._initPipelines()

        self.info_dict: dict[str, dict] = {}
        self.buildInfoDict()

        self._thread_started = False
        self.vision_thread = threading.Thread()
        self._thread_stop = False  # Flag used to stop the current thread

        # The last inference result consists in a dict
        self.last_inference_result: dict[str, dict] = {}

        ###
        self.time_resolution = time_resolution

    def _initPipelines(self):
        """Initialize the `depthai.Pipeline` objects for each model.
        The method modifies the attribute `pipelines`."""
        for i in range(self.n_models):
            new_pipeline = dai.Pipeline()

            # Check the path of the JSON and BLOB exist
            if not os.path.exists(self.json_paths[i]):
                raise ValueError(f"File {self.json_paths[i]} does not exist!")
            if not os.path.exists(self.model_paths[i]):
                raise ValueError(f"Model {self.model_paths[i]} does not exist!")

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
            cam_rgb.setFps(30)

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

            # NOTE: if on, the program breaks unless the queue is used for some reason...
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
            self._thread_stop = True
            if self.vision_thread is not None:
                self.vision_thread.join()

        # Change the active model info
        self.current_model_ind = mod_ind
        self.current_model_settings = self.model_settings[mod_ind]
        self.current_model_mappings = self.model_mappings[mod_ind]

        # Reset stop flag
        self._thread_stop = False

        # Restart the thread
        self.vision_thread = threading.Thread(
            target=self._runInferencePipeline,
            args=(self.pipelines[self.current_model_ind], mod),
            daemon=True,
        )

        self.last_inference_result = {}  # Reset value!

        self.vision_thread.start()

        if VERB:
            print(f"Thread {mod} started!")

        self._thread_started = True

        # Give the pipeline some time to start without being interrupted
        time.sleep(2)

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
        if VERB:
            print(f"Starting model {pipeline_name}")

        model_name = self.getCurrentModelName()
        with dai.Device(pipeline) as device:
            # Define queue for nn output - blocking=False will make only the most recent info available
            queue_nn = device.getOutputQueue(
                name="inference", maxSize=1, blocking=False
            )
            # Define queue for depth
            queue_depth = device.getOutputQueue(name="depth", maxSize=1, blocking=False)

            # Initialize placeholders for results:
            # depth_frame = None  # Containing the output of the camera block

            in_nn = None
            in_depth = None

            # Do the thing
            while True and not self._thread_stop:
                ts = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
                inf_result_new: dict[str, typing.Any] = {}
                inf_result_new["model_name"] = model_name
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
                    _ = in_depth.getFrame()
                    for det in in_nn.detections:
                        x1, y1, x2, y2 = (
                            det.xmin,
                            det.ymin,
                            det.xmax,
                            det.ymax,
                        )
                        det_centroid = (0.5 * (x1 + x2), 0.5 * (y1 + y2))
                        # TODO: add distance evaluation
                        # det_dist = depth_frame

                        # TODO: with distance evaluated it is possible to calculate
                        # the angle of rotation to have the plant centered.

                        # Package solution
                        inf_result_new["detections"].append(
                            {
                                "position": det_centroid,
                                # "depth": det_dist,
                                "label": det.label,
                                "class": self.current_model_mappings[det.label],
                                "distance": 0,
                                "confidence": det.confidence,
                            }
                        )

                # Need to place this here so that if no objects are found, the
                # program will return an empty solution
                self.last_inference_result = inf_result_new

                # Wait before next capture
                time.sleep(self.time_resolution)

        if VERB:
            print(f"Pipeline '{model_name}' stopped")

    # +-----------+
    # + UTILITIES
    # +-----------+

    def buildInfoDict(self):
        """
        Assemble the dict containing the information of all available models.
        """
        for i in range(self.n_models):
            self.info_dict[self.model_names[i]] = self.model_settings[i]

    def getCurrentModelName(self) -> str:
        """
        Get the name of the current active model. If no model has been launched, it
        will return an empty string.
        """
        if self.current_model_ind == -1:
            # No model was launched yet!
            return ""
        return self.model_names[self.current_model_ind]

    def stopThreads(self):
        """Stop the active pipeline to prevent errors when shutting down."""
        self._thread_stop = True
        if VERB:
            print("Threads stopped!")
        return 1


if __name__ == "__main__":
    # Init the dictionary
    script_dir = os.path.dirname(__file__)
    models_folder = os.path.join(script_dir, "..", "models")
    mod = {}
    mod["trunk"] = {
        "model_path": os.path.join(models_folder, "trunk", "trunk_yolo.pt"),
        "json_path": os.path.join(models_folder, "trunk", "trunk_yolo.json"),
    }
    mod["leaves"] = {
        "model_path": os.path.join(models_folder, "leaves", "leaves_yolo.pt"),
        "json_path": os.path.join(models_folder, "leaves", "leaves_yolo.json"),
    }
    vc = VisionController(models=mod)

    t_start = time.time()
    models = list(mod.keys())
    i = 0
    while time.time() - t_start < 20:
        vc.selectModel(models[i % len(models)])
        i += 1
