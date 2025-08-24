# Running DepthAI inside a Docker Container

The official Dockerfile is available at [this link](https://github.com/luxonis/depthai/blob/main/Dockerfile).
It builds on top of a Python image and it installs DepthAI by cloning the original [repository](https://github.com/luxonis/depthai) and running the installer.

## test-depthai

The subfolder contains a Python program that tests the installation of DepthAI inside the container.
It uses DepthAI to capture a single shot from the OAK-D lite camera.

**Notes**:

- The `depthai-test` image used in test-depthai/test_container.sh was obtained with the original [DepthAI Dockerfile](https://github.com/luxonis/depthai/blob/main/Dockerfile).
- It may be necessary to edit test-depthai/test_container.sh to match the names of folders with the host machine.
