# HOWTO: Run FREISA-GPT

This guide shows how to run a demo of FREISA-GPT on your local machine (no need for the Mini Pupper 2 robot).

## Requirements

- A computer with Docker installed

## Demo

Steps:

1. Launch [ROS2 container](https://github.com/Tiryoh/docker-ros2-desktop-vnc) for simulating robot.
2. Install [Mini Pupper 2 ROS](https://github.com/mangdangroboticsclub/mini_pupper_ros) and FREISA-GPT dependencies.
3. Run [Puppy State API](/code/puppy-state-api).
4. Launch [FREISA-GPT](/code/FREISA-GPT) (MCP server + Whisper), connecting to the State API.

### Running ROS2 Container (w/ VNC)

In order to simulate the robot, we will use the container image described [here](https://github.com/Tiryoh/docker-ros2-desktop-vnc), which launches an Ubuntu 22.04 desktop environment with ROS2 (Humble) installed.

To launch the container, go to the [FREISA-GPT directory](/code/FREISA-GPT/) and run:

```bash
docker compose -f ./puppy-sim/docker-compose.yml up -d
```

This will start the container and map the ports 6080, 8080, and 9090.

To check that the container works, visit <http://localhost:6080>.
From there, it is possible to log into the "ubuntu" user with the password `ubuntu`.

Now, let's set up the environment.

Open a Terminal window (Terminator), and run the following:

```bash
source /opt/ros/humble/setup.bash

mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/mangdangroboticsclub/mini_pupper_ros.git -b ros2-dev

vcs import < mini_pupper_ros/.minipupper.repos --recursive

cd ~/ros2_ws
sudo apt update
rosdep install --from-paths src --ignore-src -r -y
sudo apt install -y ros-humble-teleop-twist-keyboard ros-humble-teleop-twist-joy
sudo apt install -y ros-humble-v4l2-camera ros-humble-image-transport-plugins
sudo apt install -y ros-humble-rqt*
sudo apt install -y ros-humble-rosbridge-server
pip3 install simple-pid

# Remove problematic packages (alternatively, create an empty file `COLCON_IGNORE` inside their directory)
rm -rf ./src/mini_pupper_ros/mini_pupper_simulation  # Not working due to deprecated Gazebo classic
rm -rf ./src/mini_pupper_ros/mini_pupper_dance
rm -rf ./src/champ/champ/champ_gazebo

colcon build --symlink-install
```

> [!note]
>
> If the `colcon build` command fails, you can work around the issues by either deleting failing packages (`rm -rf` of the corresponding directory), or by creating an empty file `COLCON_IGNORE` inside the directories.
>
> In order to run our simulation, we just need the `mini_pupper_bringup` package.

Then, in 3 separate terminal windows, run the following:

1. Launch `mini_pupper_bringup`:

   ```bash
   # Terminal 1
   . ~/ros2_ws/install/setup.bash
   ros2 launch mini_pupper_bringup bringup.launch.py hardware_connected:=False
   ```

2. Launch RViz (this should open a window with the simulated mini-pupper)

   ```bash
   # Terminal 2
   . ~/ros2_ws/install/setup.bash
   ros2 launch mini_pupper_bringup rviz.launch.py
   ```

3. Launch `rosbridge_server`:

   ```bash
   # Terminal 3
   . ~/ros2_ws/install/setup.bash
   ros2 launch rosbridge_server rosbridge_websocket_launch.xml
   ```

> [!note]
>
> This opens up a websocket on port 9090, which is mapped to the host.
> On this websocket, we can send commands to the robot.

### Running puppy-state-api

The [puppy-state-api](https://github.com/B-AROL-O/FREISA/code/puppy-state-api) is a webserver that allows to control the puppy facial expressions and sounds.

To run the state api, simply go to the [directory](/code/puppy-state-api), and run

```bash
uv run main.py --port 5080
```

### Running FREISA-GPT

Change directory to [FREISA-GPT](/code/FREISA-GPT).

Make sure you set the correct value for the environment variable `OPENAI_API_KEY` (token for your LLM endpoint), if needed, then, run the following:

```bash
uv run main.py --llm-base-url "http://<your_llm_api_url>" --puppy-api-url "http://localhost:5080"
```

> [!note]
>
> Run `uv run main.py --help` for all the possible command line arguments, including the possibility to specify the microphone used by Whisper.

After running this command, it is possible to start talking with the puppy!

Say "Hello puppy" to invoke it, and then say what you would like the puppy to do!
