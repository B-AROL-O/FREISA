# Oak-d Lite module

This folder (will contain) the code necessary to launch the Docker container used to control the Oak-d lite camera in order to perform inference and communicate the results over specific APIs in order to guide the MiniPupper.

The module will be then deployed over Docker using the same process explained in the [depthai-docker](../depthai-docker/) folder.

## Sources and useful material

- TODO

## TODO

- [ ] Find guides on how to handle results of inference with DepthAI
- [ ] Read API specifications of DepthAI 
  - [ ] Understand how to change model on the Oak-d lite 'on the fly'
- [ ] Translate some Roboflow model to OpenVino or any format compatible with the camera.
- [ ] Read and understand application architecture
- [ ] Decide the APIs of this microservice

## DepthAI overview

The DepthAI API allows users to communicate and use OAK davices (OAK-D lite in our case).
We will use the Python API.

The following figure shows the architecture of DepthAI:

<img src="assets/images/depthai-api-diagram.png", alt="depthai-architecture" width="200"/>

The relevant points of the architecture are:

- XLink: middleware used to exchange data between device (camera) and host
  - XLinkIn: data goes from host to device
  - XLinkOut: data goes from device to host

### APIs

#### Device

`depthai.Device` object: OAK device.
Need to upload a *pipeline* (`depthai.Pipeline` - see [later](#pipeline)) to it and it will be executed on the on-board processor.
Notice that when initializing the `Device` object, it is needed to provide the pipeline as argument of the constructor.

```python
pipeline = depthai.Pipeline()

with depthai.Device(pipeline) as device:
    print(f"Connected cameras: {device.getConnectedCameras()}")

    # Init. input queue that will contain messages from host to device
    # Receive msg. with XLinkIn
    input_q = device.getInputQueue("input_name", maxSize=4, blocking=False)

    # Output queue, it will contain messages from device to host
    # Send msg. with XLinkOut
    output_q = device.getOutputQueue("output_name", maxSize=4, blocking=False)

    while True:
        # Get message from output queue
        output_q.get()

        # Send message to device
        cfg = depthai.ImageManipConfig()
        input_q.send(cfg)
```

It is also possible to pass as argument the device information of the specific device we want to connect too (not needed in our case).

The queues are used to store messages from camera/host to host/camera.
It is necessary to set the queue length and whether it will be blocking or not at initialization, but it is possible to modify these parameters afterwards (`queue.setMaxSize(10)` and `queue.setBlocking(True)`).
(*Note*: `blocking=False` means that the arrival of a message at full queue will make it drop the oldest packet to fit the new one in the buffer; with `blocking=True`, instead, incoming packets that cannot fit in the queue will be dropped).

Notice that queues will take up space in the host RAM.

Overview of class `depthai.Device`: [here](https://docs.luxonis.com/projects/api/en/latest/components/device/#reference).

#### Pipeline

`depthai.Pipeline`: collection of nodes (see [here](#nodes)) and links between them.
It specifies what the device does when powered up.

When passed to a `Device` object, it gets converted to JSON and sent to the camera with XLink.

Steps:

- Initialization: `pipeline = depthai.Pipeline()`
  - Possibility to specify OpenVINO version: `pipeline.setOpenVINOVersion(depthai.OpenVINO.Version.VERSION_2021_4)`
- Create and configure nodes
- Upload pipeline to device at its instantiation: `device = depthai.Device(pipeline)`

Overview of `depthai.Pipeline`: [here](https://docs.luxonis.com/projects/api/en/latest/components/pipeline/#reference).

#### Nodes

`depthai.node`: building block(s) of the pipeline.
Each node provides a specific functionality and a set of configurable inputs & outputs.

Nodes can be connected in order to communicate (unidirectional flows).
Need to ensure that the inputs are able to keep up with the outputs they receive data from (queues).
Also here it is necessary to decide whether to make inputs blocking or not.

Notable nodes:

- `depthai.node.ColorCamera`: provide as output the image frames captured by the color camera on the OAK device.
  - Creation: `cam = pipeline.create(depthai.node.ColorCamera)`.
  - Can extract different output formats (e.g., cropped). The following are all `ImageFrame` objects:
    - `raw` output: RAW10
    - `isp` output: YUV420
    - `still` output: NV12 (similar to taking photo)
    - `preview` output: RGB, used to feed image into `NeuralNetwork` (or other models analyzing RGB images)
    - `video` output: NV12 (bigger size frames)
  - [Full documentation](https://docs.luxonis.com/projects/api/en/latest/components/nodes/color_camera/#colorcamera)
- `depthai.node.ImageManip`: used to perform manipulations on images provided as inputs (`ImageFrame` objects).
  - Specific methods determine specific transformations
  - [Full documentation](https://docs.luxonis.com/projects/api/en/latest/components/nodes/image_manip/#imagemanip)
- `depthai.node.StereoDepth`: use the on-board stereo camera to get the disparity/depth.
  - Need configuration ([guide](https://docs.luxonis.com/projects/api/en/latest/tutorials/configuring-stereo-depth/#configuring-stereo-depth))
  - Among the outputs it is possible to find `depth` which is an `ImgFrame` indicating the distance of each point in millimeters.
  - The inputs are the left and right stereo camera flows, plus the configuration for the `StereoDepth` node.
  - Full [guide](https://docs.luxonis.com/projects/api/en/latest/components/nodes/stereo_depth/#stereodepth).
- `depthai.node.SpatialLocationCalculator`: used to provide the spatial coordinates of the specified region of interest.
  - Inputs: `inputConfig`, `inputDepth` (from `Stereodepth`)
  - Specifying ROI:
    - Initialize node: `spatialCalc = pipeline.create(depthai.node.SpatialLocationCalculator)`
    - Extract config: `config = depthai.SpatialLocationCalculatorConfigData()`
    - Modify settings: `config.depthThresholds.lowerThreshold = 100` (minimum value of depth to actually provide spatial location info)
    - Set ROI: `config.roi = depthai.Rect(topLeft, bottomRight)`
    - Update config of node: `spatialCalc.initialConfig(addROI())`
- `depthai.node.NeuralNetwork`: upload a NN in OpenVINO format (as long as all layers fit in memory)
  - Generic neural network block (more specialized ones exist - see `depthai.node.MobileNetDetectionNetwork`)
  - Input: any message type
  - [Full documentation](https://docs.luxonis.com/projects/api/en/latest/components/nodes/neural_network/#neuralnetwork)
- `depthai.node.MobileNetDetectionNetwork`: used to apply the MobileNet NN (with specific parameters, to be uploaded) to an image stream.
  - Procedure:
    - Create pipeline: `pipeline = dai.Pipeline()`
    - Add node: `mobilenetDet = pipeline.create(dai.node.MobileNetDetectionNetwork)`
    - Set confidence threshold: `mobilenetDet.setConfidenceThreshold(0.5)`
    - Pass model parameters: `mobilenetDet.setBlobPath(nnBlobPath)`
    - Set number of threads for inference: `mobilenetDet.setNumInferenceThreads(2)`
    - Customize output type (e.g., non-blocking - drop oldest): `mobilenetDet.input.setBlocking(False)`
