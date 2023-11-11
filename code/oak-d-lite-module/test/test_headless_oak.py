import depthai as dai
import cv2
import blobconverter
import numpy as np
from datetime import datetime
import os
import sys
import time

LOG = True


def frameNorm(frame, bbox):
    normVals = np.full(len(bbox), frame.shape[0])
    normVals[::2] = frame.shape[1]
    return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)


def runInferencePipeline(
    pipeline: dai.Pipeline,
    labels_list: list,
    max_time: float,
    res_path: str,
    pipeline_name: str = "Neural network",
    disp: bool = False,
    verb: bool = False,
):
    """
    runInferencePipeline
    ---
    Run a specific inference pipeline on the OAK device.

    The steps of the pipeline are the following:
    - Initialize queues for communication with the camera
    - Open the file (created if not existing)
    - Start the capture
    - Write on output file the detected objects only (with timestamp
    and position in the field of view)

    ### Input parameters
    - pipeline: depthai.Pipeline object with initialized nodes; need
    output streams (XLinkOut) "rgb" and "inference" to be initialized
    - labels_list: list of labels for provided NN; the indices must
    match the output value of the model
    - max_time: time duration for the use of the pipeline
    - res_path: path of the output file
    - pipeline_name: name of the pipeline (string) - used for printing
    on stdout
    - disp: flag to determine whether to reproduce video stream (not
    the intended use case)
    - verb: flag for printing runtime information
    """
    # If the output path does not exist, create it.
    if not os.path.exists(res_path):
        if verb:
            print(f"Creating file {res_path}")
        with open(res_path, "w") as f:
            f.close()

    t_start = time.time()
    with dai.Device(pipeline) as device:
        if LOG:
            device.setLogLevel(dai.LogLevel.DEBUG)
            device.setLogOutputLevel(dai.LogLevel.DEBUG)

        # Define queue for nn output - blocking=False will make only the most recent info available
        queue_nn = device.getOutputQueue(name="inference", maxSize=1, blocking=False)
        # Define queue for camera output - only if 'disp' flag is true
        if disp:
            queue_rgb = device.getOutputQueue("rgb", maxSize=1, blocking=False)

        # Define queue for depth estimation
        queue_depth = device.getOutputQueue(name="depth", maxSize=1, blocking=False)

        # NOTE: setting blocking=False makes inference quicker, as everytime the
        # loop is repeated there will be no backlogged detections (old ones are
        # discarded)

        # Initialize placeholders for results:
        frame = None  # Containing the output of the camera block
        detections = []  # Containing the inference results

        in_depth = None

        # Create a text file to store inference results
        with open(res_path, "a") as output_file:
            print("{} started".format(pipeline_name))
            while time.time() - t_start < max_time:
                # Timestamp
                ts = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

                # Try to get an element from the output nn queue
                # in_nn = queue_nn.tryGet()
                in_nn = queue_nn.get()
                if verb:
                    print("•")
                in_depth = queue_depth.tryGet()

                if disp:
                    in_rgb = queue_rgb.tryGet()

                    if in_rgb is not None:
                        frame = in_rgb.getCvFrame()

                flg_disp = False
                if frame is not None and disp:
                    flg_disp = True

                # Get the detection results from the frame (if any)
                if in_nn is not None:  # and in_depth is not None:
                    detections = in_nn.detections

                    for detection in detections:
                        # Get boundary coordinates of detected object
                        x1, y1, x2, y2 = (
                            detection.xmin,
                            detection.ymin,
                            detection.xmax,
                            detection.ymax,
                        )
                        # Notice that the values of x and y are normalized to [0, 1]
                        object_centroid = (0.5 * (x1 + x2), 0.5 * (y1 + y2))

                        # Evaluating the distance of the centroid object from the camera:
                        depth_frame = in_depth.getFrame()
                        print()

                        out_str = (
                            "{}: Label: {} - {}, Confidence: {}; Position: {}\n".format(
                                ts,
                                detection.label,
                                labels_list[detection.label],
                                detection.confidence,
                                object_centroid,
                            )
                        )

                        if verb:
                            print(out_str)

                        output_file.write(out_str)

                        if flg_disp:
                            bbox = frameNorm(frame, (x1, y1, x2, y2))
                            cv2.rectangle(
                                frame,
                                (bbox[0], bbox[1]),
                                (bbox[2], bbox[3]),
                                (255, 0, 0),
                                2,
                            )

                    if flg_disp:
                        print("here")
                        cv2.imshow("preview", frame)
                else:
                    pass
                    # output_file.write("{}\n".format(ts))

                # wait for some time before next capture
                time.sleep(0.5)


VERB = True
DISPLAY = False
MN_CLASSES = [
    "background",
    "aeroplane",
    "bicycle",
    "bird",
    "boat",
    "bottle",
    "bus",
    "car",
    "cat",
    "chair",
    "cow",
    "diningtable",
    "dog",
    "horse",
    "motorbike",
    "person",
    "pottedplant",
    "sheep",
    "sofa",
    "train",
    "tvmonitor",
]
YOLO_CLASSES = [
    "person",
    "bicycle",
    "car",
    "motorbike",
    "aeroplane",
    "bus",
    "train",
    "truck",
    "boat",
    "traffic light",
    "fire hydrant",
    "stop sign",
    "parking meter",
    "bench",
    "bird",
    "cat",
    "dog",
    "horse",
    "sheep",
    "cow",
    "elephant",
    "bear",
    "zebra",
    "giraffe",
    "backpack",
    "umbrella",
    "handbag",
    "tie",
    "suitcase",
    "frisbee",
    "skis",
    "snowboard",
    "sports ball",
    "kite",
    "baseball bat",
    "baseball glove",
    "skateboard",
    "surfboard",
    "tennis racket",
    "bottle",
    "wine glass",
    "cup",
    "fork",
    "knife",
    "spoon",
    "bowl",
    "banana",
    "apple",
    "sandwich",
    "orange",
    "broccoli",
    "carrot",
    "hot dog",
    "pizza",
    "donut",
    "cake",
    "chair",
    "sofa",
    "pottedplant",
    "bed",
    "diningtable",
    "toilet",
    "tvmonitor",
    "laptop",
    "mouse",
    "remote",
    "keyboard",
    "cell phone",
    "microwave",
    "oven",
    "toaster",
    "sink",
    "refrigerator",
    "book",
    "clock",
    "vase",
    "scissors",
    "teddy bear",
    "hair drier",
    "toothbrush",
]

if __name__ == "__main__":
    # Allow to pass output file name (relative path) as command line arg
    if len(sys.argv) > 1:
        output_path_rel = str(sys.argv[1])
    else:
        output_path_rel = "detection_results.txt"
    # Wipe the file with the outputs:
    fname = os.path.join(os.path.dirname(__file__), output_path_rel)
    with open(fname, "w") as f:
        f.close()

    # Initialize DepthAI pipeline
    pipeline = dai.Pipeline()

    # Create camera node
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    cam_rgb.setPreviewSize(300, 300)
    cam_rgb.setInterleaved(False)

    # Configure the YOLO detection model (use MobileNet for testing)
    # pipeline.add(depthai.YoloDetectionNetwork().setBlobPath("path/to/your/yolo_model.blob").setConfidenceThreshold(0.5))
    detection_nn = pipeline.create(dai.node.MobileNetDetectionNetwork)
    detection_nn.setBlobPath(blobconverter.from_zoo(name="mobilenet-ssd", shaves=6))
    detection_nn.setConfidenceThreshold(0.5)
    detection_nn.input.setBlocking(False)
    detection_nn.setNumInferenceThreads(2)

    # Connect color camera preview to nn input
    cam_rgb.preview.link(detection_nn.input)

    # Depth estimation
    mono_l = pipeline.create(dai.node.MonoCamera)
    mono_l.setCamera("left")
    mono_l.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

    mono_r = pipeline.create(dai.node.MonoCamera)
    mono_r.setCamera("right")
    mono_r.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

    stereo = pipeline.create(dai.node.StereoDepth)
    stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
    # Options: MEDIAN_OFF, KERNEL_3x3, KERNEL_5x5, KERNEL_7x7 (default)
    stereo.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
    stereo.setLeftRightCheck(True)
    stereo.setExtendedDisparity(False)
    stereo.setSubpixel(False)

    # Link mono cameras to stereo view
    mono_l.out.link(stereo.left)
    mono_r.out.link(stereo.right)

    # Create XLink objects and link the specific node outputs
    # to the corresponding stream
    # Video
    xout_rgb = pipeline.create(dai.node.XLinkOut)
    xout_rgb.setStreamName("rgb")
    cam_rgb.preview.link(xout_rgb.input)

    # Inference
    xout_nn = pipeline.create(dai.node.XLinkOut)
    xout_nn.setStreamName("inference")
    detection_nn.out.link(xout_nn.input)

    # Link depth estimation
    xout_stereo = pipeline.create(dai.node.XLinkOut)
    xout_stereo.setStreamName("depth")
    stereo.depth.link(xout_stereo.input)

    #
    #
    #
    ###### Create second pipeline with different model
    pipeline_1 = dai.Pipeline()

    cam_rgb_1 = pipeline_1.create(dai.node.ColorCamera)
    cam_rgb_1.setPreviewSize(416, 416)
    cam_rgb_1.setInterleaved(False)
    cam_rgb_1.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

    yolo_nn = pipeline_1.create(dai.node.YoloDetectionNetwork)
    # yolo_nn.setBlobPath(
    #    "/home/dmacario/github/luxonis/depthai/resources/nn/yolo-v3-tiny-tf/yolo-v3-tiny-tf.json"
    # )
    yolo_nn.setBlobPath(blobconverter.from_zoo(name="yolo-v3-tiny-tf", shaves=6))
    yolo_nn.setConfidenceThreshold(0.5)
    # Additional settings needed for YOLOv3
    yolo_nn.setNumClasses(80)
    yolo_nn.setCoordinateSize(4)
    yolo_nn.setAnchors([10, 14, 23, 27, 37, 58, 81, 82, 135, 169, 344, 319])
    yolo_nn.setAnchorMasks({"side26": [1, 2, 3], "side13": [3, 4, 5]})
    yolo_nn.setIouThreshold(0.5)
    yolo_nn.setNumInferenceThreads(2)
    yolo_nn.input.setBlocking(False)

    cam_rgb_1.preview.link(yolo_nn.input)

    # Depth estimation
    mono_l_1 = pipeline_1.create(dai.node.MonoCamera)
    mono_l_1.setCamera("left")
    mono_l_1.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

    mono_r_1 = pipeline_1.create(dai.node.MonoCamera)
    mono_r_1.setCamera("right")
    mono_r_1.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

    stereo_1 = pipeline_1.create(dai.node.StereoDepth)
    stereo_1.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
    # Options: MEDIAN_OFF, KERNEL_3x3, KERNEL_5x5, KERNEL_7x7 (default)
    stereo_1.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
    stereo_1.setLeftRightCheck(True)
    stereo_1.setExtendedDisparity(False)
    stereo_1.setSubpixel(False)

    # Link mono cameras to stereo view
    mono_l_1.out.link(stereo_1.left)
    mono_r_1.out.link(stereo_1.right)

    # Output streams
    xout_1_rgb = pipeline_1.create(dai.node.XLinkOut)
    xout_1_rgb.setStreamName("rgb")
    cam_rgb_1.preview.link(xout_1_rgb.input)

    xout_1_nn = pipeline_1.create(dai.node.XLinkOut)
    xout_1_nn.setStreamName("inference")
    yolo_nn.out.link(xout_1_nn.input)

    # Link depth estimation
    xout_stereo_1 = pipeline_1.create(dai.node.XLinkOut)
    xout_stereo_1.setStreamName("depth")
    stereo_1.depth.link(xout_stereo_1.input)

    ## Execution Loop (use each model for 20 seconds, then switch)
    while True:
        runInferencePipeline(
            pipeline, MN_CLASSES, 1000000, fname, "MobileNet", disp=DISPLAY, verb=VERB
        )
        # Switch model
        # runInferencePipeline(
        #     pipeline_1, YOLO_CLASSES, 40, fname, "YOLOv3", disp=DISPLAY, verb=VERB
        # )

        if cv2.waitKey(1) == ord("q"):
            # This part of the code is not working!
            break
