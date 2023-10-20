import depthai as dai
import cv2
import blobconverter
import numpy as np
from datetime import datetime
import time


def frameNorm(frame, bbox):
    normVals = np.full(len(bbox), frame.shape[0])
    normVals[::2] = frame.shape[1]
    return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)


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
    # Wipe the file with the outputs:
    fname = "detection_results.txt"
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

    # Connect color camera preview to nn input
    cam_rgb.preview.link(detection_nn.input)

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

    xout_1_rgb = pipeline_1.create(dai.node.XLinkOut)
    xout_1_rgb.setStreamName("rgb")
    cam_rgb_1.preview.link(xout_1_rgb.input)

    xout_1_nn = pipeline_1.create(dai.node.XLinkOut)
    xout_1_nn.setStreamName("inference")
    yolo_nn.out.link(xout_1_nn.input)

    ## Execution Loop (use each model for 20 seconds, then switch)
    while True:
        # Create DepthAI device
        t_mn_start = time.time()
        with dai.Device(pipeline) as device:
            # Define queue for nn output - blocking=False will make only the most recent info available
            queue_nn = device.getOutputQueue(
                name="inference", maxSize=1, blocking=False
            )
            # queue_nn = device.getOutputQueue(name="inference")

            queue_rgb = device.getOutputQueue("rgb", maxSize=1, blocking=False)
            # queue_rgb = device.getOutputQueue("rgb")

            # NOTE: setting blocking=False makes inference quicker, as everytime the
            # loop is repeated there will be no backlogged detections (old ones are
            # discarded)

            # Initialize placeholders for results:
            frame = None  # Probably not used
            detections = []

            # Create a text file to store inference results
            with open(fname, "a") as output_file:
                print("MobileNet started")
                while time.time() - t_mn_start < 20:
                    # Timestamp
                    ts = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

                    # Try to get an element from the output nn queue
                    in_nn = queue_nn.tryGet()

                    # frame = None
                    if DISPLAY:
                        in_rgb = queue_rgb.tryGet()

                        if in_rgb is not None:
                            frame = in_rgb.getCvFrame()

                    flg_disp = False
                    if frame is not None and DISPLAY:
                        flg_disp = True

                    # Get the detection results from the frame (if any)
                    if in_nn is not None:
                        detections = in_nn.detections

                        for detection in detections:
                            # Get boundary coordinates of detected object
                            x1, y1, x2, y2 = (
                                int(detection.xmin),
                                int(detection.ymin),
                                int(detection.xmax),
                                int(detection.ymax),
                            )
                            # Notice that the values of x and y are normalized to [0, 1]
                            object_centroid = (0.5 * (x1 + x2), 0.5 * (y1 + y2))

                            out_str = "{}: Label: {} - {}, Confidence: {}; Position: {}\n".format(
                                ts,
                                detection.label,
                                MN_CLASSES[detection.label],
                                detection.confidence,
                                object_centroid,
                            )

                            if VERB:
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

        # Switch model
        t_yolo_start = time.time()
        with dai.Device(pipeline_1) as device:
            # Define queue for nn output - blocking=False will make only the most recent info available
            queue_nn = device.getOutputQueue(
                name="inference", maxSize=1, blocking=False
            )
            # queue_nn = device.getOutputQueue(name="inference")

            queue_rgb = device.getOutputQueue("rgb", maxSize=1, blocking=False)
            # queue_rgb = device.getOutputQueue("rgb")

            # NOTE: setting blocking=False makes inference quicker, as everytime the
            # loop is repeated there will be no backlogged detections (old ones are
            # discarded)

            # Initialize placeholders for results:
            frame = None  # Probably not used
            detections = []

            # Create a text file to store inference results
            with open(fname, "a") as output_file:
                print("YOLO started")
                while time.time() - t_yolo_start < 20:
                    # Timestamp
                    ts = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

                    # Try to get an element from the output nn queue
                    in_nn = queue_nn.tryGet()

                    # frame = None
                    if DISPLAY:
                        in_rgb = queue_rgb.tryGet()

                        if in_rgb is not None:
                            frame = in_rgb.getCvFrame()

                    flg_disp = False
                    if frame is not None and DISPLAY:
                        flg_disp = True

                    # Get the detection results from the frame (if any)
                    if in_nn is not None:
                        detections = in_nn.detections

                        for detection in detections:
                            # Get boundary coordinates of detected object
                            x1, y1, x2, y2 = (
                                int(detection.xmin),
                                int(detection.ymin),
                                int(detection.xmax),
                                int(detection.ymax),
                            )
                            # Notice that the values of x and y are normalized to [0, 1]
                            object_centroid = (0.5 * (x1 + x2), 0.5 * (y1 + y2))

                            out_str = "{}: Label: {} - {}, Confidence: {}; Position: {}\n".format(
                                ts,
                                detection.label,
                                YOLO_CLASSES[detection.label],
                                detection.confidence,
                                object_centroid,
                            )

                            if VERB:
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

        if cv2.waitKey(1) == ord("q"):
            # This part of the code is not working!
            break
