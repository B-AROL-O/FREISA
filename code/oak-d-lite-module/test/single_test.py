# Initialize DepthAI pipeline
import depthai as dai
import cv2
import blobconverter
import numpy as np
from datetime import datetime
import os
import sys
import time


DISP = False
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


def frameNorm(frame, bbox):
    normVals = np.full(len(bbox), frame.shape[0])
    normVals[::2] = frame.shape[1]
    return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)


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
# detection_nn.input.setBlocking(False)
# detection_nn.setNumInferenceThreads(2)

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

with dai.Device(pipeline) as device:
    # Define queue for nn output - blocking=False will make only the most recent info available
    queue_nn = device.getOutputQueue(name="inference", maxSize=1, blocking=False)

    # Define queue for depth estimation
    queue_depth = device.getOutputQueue(name="depth", maxSize=1, blocking=False)
    # Queue for RGB image
    queue_rgb = device.getOutputQueue("rgb", maxSize=1, blocking=False)

    # NOTE: setting blocking=False makes inference quicker, as everytime the
    # loop is repeated there will be no backlogged detections (old ones are
    # discarded)

    # Initialize placeholders for results:
    frame = None  # Containing the output of the camera block
    detections = []  # Containing the inference results

    in_depth = None

    # Create a text file to store inference results
    print("{} started".format("Pipeline"))
    while True:
        # Timestamp
        ts = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

        # Get queue items
        in_nn = queue_nn.tryGet()
        in_depth = queue_depth.tryGet()
        if DISP:
            in_rgb = queue_rgb.tryGet()
            if in_rgb is not None:
                frame = in_rgb.getCvFrame()

        # Get the detection results from the frame (if any)
        if in_nn is not None:  # and in_depth is not None:
            print("•")
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
                # depth_frame = in_depth.getFrame()
                print()

                out_str = "{}: Label: {} - {}, Confidence: {}; Position: {}\n".format(
                    ts,
                    detection.label,
                    MN_CLASSES[detection.label],
                    detection.confidence,
                    object_centroid,
                )

                print(out_str)

                if DISP and in_rgb is not None:
                    bbox = frameNorm(frame, (x1, y1, x2, y2))
                    cv2.rectangle(
                        frame,
                        (bbox[0], bbox[1]),
                        (bbox[2], bbox[3]),
                        (255, 0, 0),
                        2,
                    )
            if DISP and in_rgb is not None:
                cv2.imshow("preview", frame)

        else:
            print("No queue item!")
            # output_file.write("{}\n".format(ts))

        # wait for some time before next capture
        time.sleep(1)
