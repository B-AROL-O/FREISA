# HOWTO: set up a training workstation

This guide will show you how to prepare a Linux (Ubuntu) workstation for training the YOLOv8 models used in FREISA.

We will go through the steps to create a Docker container with JupyterLab, which will allow us to remotely access a development environment where it is possible to train the vision models on a GPU.

## Requirements

- A computer running Ubuntu 22.04 LTS
- Preferrably, a GPU (the steps will assume an Nvidia GPU is used)
- Docker needs to be installed on the system.
  - Follow [these steps](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04) for a minimal, but effective Docker installation.

## Installation

### Installing Nvidia drivers

First, we need to install the Nvidia drivers.
If they are already installed, we suggest to follow this guide anyway, as the same commands can be used to upgrade them.

To check which version (if any) of the drivers is currently installed, run:

```bash
cat /proc/driver/nvidia/version
```

List all the available driver versions:

```bash
sudo ubuntu-drivers list
```

And note down these versions.
Then, visit the [Nvidia site](https://www.nvidia.com/Download/index.aspx?lang=en-us) to find out which is the latest (stable) driver version supported by your GPU.
We will install this driver version.

To install it automatically, run the command:

```bash
sudo ubuntu-drivers install
```

Assuming, instead, that we want to install the driver version 550 (replace the value with your own desired version):

```bash
sudo ubuntu-drivers install nvidia:550
```

After installing the drivers, perform a reboot:

```bash
sudo reboot
```

Once the computer has restarted, you should be able to run:

```bash
nvidia-smi
```

and get your GPU information as output.

_Note_ that at the time of writing we are using CUDA 12.4.

## Installing additional Nvidia toolkits

Next, we will install the **CUDA toolkit** following [this guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/#network-repo-installation-for-ubuntu).\
Carefully follow all the installation steps, including the [post-installation actions](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#post-installation-actions), as they are required to correctly set-up the environment.

Next, install **cuDNN**, the CUDA framework for Deep Neural Networks, follow [this guide](https://docs.nvidia.com/deeplearning/cudnn/installation/linux.html#install-linux).
Then reboot (`sudo reboot`).

To verify the installation, follow [this](https://docs.nvidia.com/deeplearning/cudnn/installation/linux.html#verifying-the-install-on-linux).

Next, install the **Nvidia Container Toolkit** following [this guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).
Specifically, you may want to follow [this section](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installing-with-apt).

## Setting up the work environment (JupyterLab container)

Now, we will create our work environment, consisting of a Docker container running JupyterLab.
We will use **Docker compose**, meaning that we need to create a `docker-compose.yaml` file, such as this one:

```yaml
# docker-compose.yaml

version: "3.9"

services:
  jupyter:
    image: "quay.io/jupyter/pytorch-notebook:cuda12-latest"
    user: root
    working_dir: "/home/jovyan"
    ports:
      - "8888:8888"
    volumes:
      - ./projects/:/home/jovyan/projects/
    container_name: jupyter-ml
    build:
      context: .
      shm_size: "8gb"
    shm_size: "8gb"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1  # Replace with the actual number of GPUs on your system
              capabilities: [gpu]
    environment:
      JUPYTER_ENABLE_LAB: "yes"
      GRANT_SUDO: "yes"
      CHOWN_HOME: "yes"
    command: "start-notebook.py --IdentityProvider.token='<YOUR-TOKEN>'"
    restart: unless-stopped
```

Here, we are defining a container based on the "pytorch-notebook" image from Jupyter (for CUDA 12, as this is the major version we are using).
The container will have the name 'jupyter-ml', and it will have access to the GPU (granted by the Container Toolkit we installed in previous section).\
We also increased the shared memory (SHM) size to 8 GB, as it could have limited the capabilities of the container if left to the default (small) value.
**Make sure to set an adequate amount of shared memory, and avoid exceeding 50% of your total system memory** as a rule of thumb.

To secure (to some extent) the connection, in case the container will run on a remote server, we set a **token** (see: `command: "start-notebook.py --IdentityProvider.token='<YOUR-TOKEN>'"`) that will be used to access Jupyter Lab the first time we will connect to the container.
It is possible to set the token to `''` to remove it, but we strongly suggest you to leave it set.

We also created a _Docker volume_ mapping the `./projects` directory (that will be created if not existing) to the container directory `/home/jovyan/projects/` (_note: `jovyan` is the default user of the container, if you wanna know why, read [this](https://jupyter-docker-stacks.readthedocs.io/en/latest/using/faq.html#who-is-jovyan)_).\
You can edit the host volume that gets mapped to the container as you prefer.

### Creating the container

To create and launch the container, go to the directory containing the `docker-compose.yaml` file and run:

```bash
docker compose up -d
```

### Connecting to JupyterLab

To connect to the container, visit the following address:

> http://<host-IP-address>:8888/lab?token=<YOUR-TOKEN>

The first time, you will be prompted to create a password.

### Important remarks

- The container uses its own Python runtime, which, according to the "quay.io/jupyter/pytorch-notebook:cuda12-latest" image definition, already contains many of the common deep-learning Python packages.
  If installing new packages (e.g., via pip from the internal terminal), these will persist, unless the container is _destroyed_, meaning that it is possible to _stop_ the container (`docker stop jupyter-ml`) without losing the installation.
- Make sure that the GPU is correctly accessed by the container by running `nvidia-smi` from a terminal session within JupyterLab; if errors are raised, most of the time it is just required to restart the container by running (from the host terminal) `docker restart jupyter-ml`.

## References

- <https://docs.nvidia.com/cuda/cuda-installation-guide-linux/contents.html>
- <https://towardsdatascience.com/deep-learning-gpu-installation-on-ubuntu-18-4-9b12230a1d31>
- <https://ubuntu.com/server/docs/nvidia-drivers-installation>
- <https://medium.com/@metechsolutions/setup-nvidia-gpu-in-ubuntu-22-04-for-llm-e181e473a3f4>
- <https://docs.nvidia.com/deeplearning/cudnn/installation/linux.html#install-linux>
