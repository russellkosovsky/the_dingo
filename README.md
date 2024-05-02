# Dingo Quadruped

<p align="center">
    <img src="assets/JEL05566.jpg" style="align:centre" width="50%">
</p>

## Overview
This repository hosts the code for the Dingo Quadruped, a robot designed to be low-cost but capable of conducting research and being extensively modified with additional actuators and sensors. CAD for the Dingo can be found [here](https://grabcad.com/library/dingo-robot-quadruped-2). A full Bill of materials for purchasable components can be found within this repo.

This code is based on the [Stanford Pupper](https://github.com/stanfordroboticsclub/StanfordQuadruped) and [notspot](https://github.com/lnotspotl/notspot_sim_py) codebases, with extensive modifications, including integration into ROS 1 Noetic.

The repository includes a driver node, dingo_driver.py, which should be used anytime the code is run. This file enables joystick control of the Dingo, and allows joint and/or task space commands generated by any other code to be passed through the driver via the appropriate ROS command topics. The joystick can also be toggled on and off to override commands received via ROS command topics

The repo also includes a gazebo simulation of the Dingo, based on URDF file and meshes which are also provide.

## How Dingo_driver Works
The following flow diagram shows a simplified overview of how a joystick command is handled by the driver to affect joint movements:
<p align="center">
    <img src="assets/Dingo_driver flow diagram.png" style="align:centre" width="50%">
</p>

## Project Structure
```.
├── assets                                    Images used in the readme file
├── dingo_nano                                Code for the Arduino Nano V3 to read sensor data and send it to the Raspberry Pi
└── dingo_ws                                  ROS workspace containing all required packages
   └── src
     ├── dingo                                Package containing node and launch files for running the robot
     ├── dingo_control                        Package containing all files related to control, including kinematics and default trot controller
     ├── dingo_description                    Package containing simulation files (URDF file and meshes)
     ├── dingo_gazebo                         Package containing gazebo files
     ├── dingo_hardware_interfacing
     |  ├── dingo_input_interfacing           Package containing files for receiving and interpreting commands (From a joystick or keyboard)
     |  ├── dingo_peripheral_interfacing      Package containing files for interfacing with the Arduino Nano, LCD screen and IMU
     |  └── dingo_servo_interfacing           Package containing the hardware interface for sending joint angles to the servo motors
     └── dingo_utilities                      Package containing useful utilities
```

## Installation of Code
### Natively
- Install Ubuntu 20.04 onto the Pi's SD card via the [Raspberry Pi Imager](https://www.raspberrypi.com/software/), and setup username, password and network information.
- Install [ros-noetic](http://wiki.ros.org/noetic/Installation/Ubuntu)
- Install necessary packages via `sudo apt-get install python3-catkin-tools git python3-rosdep python3-rosinstall python3-rosinstall-generator python3-wstool python3-pip build-essential wireless-tools libraspberrypi-bin ros-noetic-joy ros-noetic-catkin python3-catkin-tools i2c-tools libi2c-dev python3-smbus`
- Install necessary python packages via `pip install spidev transforms3d adafruit-circuitpython-bno055 pillow rpi.gpio pyserial`
- Change directory to the home folder: `cd ~`
- Clone this (the Dingo Quadruped) repository using git: `git clone ...`
- Move into the dingo_ws folder: `cd /DingoQuadruped/dingo_ws`
- Initialise rosdep: `sudo rosdep init`
- Fetch dependencies with rosdep: `rosdep update`
- Build the workspace: `catkin build`
- Source the workspace: `source devel/setup.bash`
- (Optional) Add a line to .bashrc to automatically source the workspace: `echo "source ~/DingoQuadruped/dingo_ws/devel/setup.bash" >> ~/.bashrc`, `source ~/.bashrc`

### Additional Installation Steps
#### Bluetooth Setup
For getting bluetooth controller working (for instance PS4 controller)
- More info here: https://www.makeuseof.com/manage-bluetooth-linux-with-bluetoothctl/
- Install bluetooth: 
    - `sudo apt-get install bluetooth bluez bluez-tools`
    - `sudo apt-get install pi-bluetooth`
- To pair and connect a controller:
    - `bluetoothctl scan on`
    - `bluetoothctl pair AA:BB:CC:11:22:33` (example device)
    - `bluetoothctl connect AA:BB:CC:11:22:33`
    - `bluetoothctl trust AA:BB:CC:11:22:33`
- To test the controller
    - `jstest /dev/input/js0`

At this stage, the controller will only connect if you run `bluetoothctl` in the terminal, and then press the pair button on the controller. To bypass the step of running `bluetoothctl`, do the following:
- Create a shell script called connect_controller.sh (Make a note of where you create it) with the following contents:
```.
#!/bin/bash

# Replace 'XX:XX:XX:XX:XX:XX' with your controller's MAC address
controller_mac="XX:XX:XX:XX:XX:XX"

# Use bluetoothctl to connect the controller
bluetoothctl <<EOF
connect $controller_mac
exit
EOF`
```
- Make it executable by running `chmod +x connect_controller.sh`
- Create a UDEV rule to run this script every time the controller attempts to pair: `SUBSYSTEM=="bluetooth", KERNEL=="hci0", ACTION=="add", ENV{DEVTYPE}=="adapter", TAG+="systemd", SYMLINK+="bluetooth", RUN+="/bin/sleep 10", RUN+="/path/to/connect_controller.sh"`
- reload the UDEV rules: `sudo udevadm control --reload`
The controller should now autopair every time the pair button is pressed, without needing to do anything on the Pi

#### Wifi Setup
To get WiFi working
- Edit the file /etc/netplan/50-cloud-init.yaml 
- Add the following to the bottom of the file
```.   
    wifis:
        wlan0:
            optional: true
            dhcp4: true
            access-points:
                "<wifi SSID>":
                    password: "<wifi password>"
```  

If getting an error with "rounded_rectangle", need to install later version of Pillow.
- Upgrade pillow with `pip3 install --upgrade Pillow`

#### LCD Node Additional Setup
The LCD node has been created following the waveshare tutorial here: https://www.waveshare.com/wiki/1.47inch_LCD_Module. Apart from installing the libraries listed there, the fonts also need to be moved into the ubuntu fonts folder to be used by executing the following lines:
- `cd ~`
- `sudo apt-get install unzip -y`
- `sudo wget https://files.waveshare.com/upload/8/8d/LCD_Module_RPI_code.zip`
- `sudo unzip ./LCD_Module_RPI_code.zip`
- `cd ~/LCD_Module_RPI_code/RaspberryPi/python/Font`
- `sudo mv Font00.ttf /usr/share/fonts/truetype/Font00.ttf`
- `sudo mv Font01.ttf /usr/share/fonts/truetype/Font01.ttf`
- `sudo mv Font02.ttf /usr/share/fonts/truetype/Font02.ttf`

#### Setting necessary permissions for ROS
To run ROS as non-root, must set permissions correctly via udev for several /dev files.
- Add the following to /etc/udev/rules.d/99-ROS.rules
```.   
       KERNEL=="ttyS0", OWNER="root", GROUP="ros", MODE="0660"
       KERNEL=="spi", OWNER="root", GROUP="ros", MODE="0660"
       KERNEL=="i2c", OWNER="root", GROUP="ros", MODE="0660"
       KERNEL=="gpiomem", OWNER="root", GROUP="ros", MODE="0660"
       KERNEL=="mem", OWNER="root", GROUP="ros", MODE="0660"
```
- Add new group to user account: `sudo groupadd ros && sudo adduser <username> ros`
- Reload udev rules: `sudo udevadm control --reload-rules && sudo udevadm trigger`

#### Setting up I2C
- First, run this command to check whether i2c is working for root: `sudo i2cdetect -y 1`. If this doesnt work, try replacing the 1 with a 0. If this works, replace the 1 with a 0 in all subsequent steps.
- Now try for your user: `i2cdetect -y 1`. If the same matrix appears, all is good. Otherwise, run the following:
```.
    sudo groupadd i2c
    sudo chown :i2c /dev/i2c-1
    sudo chmod g+rw /dev/i2c-1
    sudo usermod -aG i2c [INSERT YOUR USERNAME]
```
- Reboot or logout and back in and then check if i2c is working by running `i2cdetect -y 1`. The matrix should now appear for your user.

#### Setting up SPI
Please run the code first before following these steps. If you do not receive an SPI permission error, there is no need to do the following SPI setup steps. Proceed if you receive an error
- Run `ls -la /dev/spidev*` to list SPI devices
- Then, run the following to give your user SPI permissions, repeating the last two lines for all SPI devices listed from previous command:
```.
    sudo groupadd spi
    sudo usermod -aG spi <yourusername>
    sudo chown :spi <put the spi device name here>
    sudo chmod g+rw <put the spi device name here>
```
- Try running the code again. If it works, reboot the device and run the code again immediately after logging in. If it still works after reboot, no need to continue, but it if does not, keep going below:
- Run `sudo nano /etc/systemd/system/spi-permissions.service` and put the following into the file, saving and exiting afterwards:
```.
    [Unit]
    Description=Set SPI Permissions
     
    [Service]
    ExecStart=/path/to/your/script.sh
    User=root
    Group=root
    Restart=on-failure
    RestartSec=5s
     
    [Install]
    WantedBy=multi-user.target
```
- Now, run `nano ~/startspi.sh` and put the following into the file, saving and exiting afterwards. Note: If your SPI device names are different, please update them accordingly:
```.
    #!/bin/bash
    sudo usermod -aG spi <yourusername>
    sudo chown :spi /dev/spidev0.0
    sudo chmod g+rw /dev/spidev0.0
    sudo chown :spi /dev/spidev0.1
    sudo chmod g+rw /dev/spidev0.1
```
- Run the following in the terminal:
    - `sudo chmod +x /path/to/your/script.sh`
    - `sudo systemctl daemon-reload`
    - `sudo systemctl enable spi-permissions.service`
    - `sudo systemctl start spi-permissions.service`

SPI should now work across restarts

#### Setting up Serial Comms
Serial communications was one of the hardest parts of this project to get working. Unfortunately Ubuntu 20.04 in particular seems to have trouble on Raspberry Pi with serial communications via the tx and rx pins. If the following steps do not work for you, further research/trial and error may be required. 

Do the following:
- Run the following to install ROS serial
    - `sudo apt-get update`
    - `sudo apt-get install ros-noetic-rosserial ros-noetic-rosserial-python ros-noetic-rosserial-arduino`
- Disable the Ubuntu serial console or it will conflict with serial comms
    - `sudo systemctl disable serial-getty@ttyS0.service --now`
    - `sudo systemctl stop serial-getty@ttyS0.service`
    - `sudo systemctl mask serial-getty@ttyS0.service`
 
Test whether serial is working by running the Dingo code. It should attempt to connect to the Arduino and successfully do so, which can be seen via the code printing to the terminal that publishers have been established. If it errors, first check your wiring to the arduino, and that the arduino has been flashed correctly. If this does not work, further research and trial/error will be needed. Look for articles like [this one](https://devicetests.com/enabling-uart-communication-raspberry-pi-4-ubuntu-20-04)

#### SD Card Backup
It's a good idea to backup the sdcard every so often. Here is how to do that on linux.
- Take out the sdcard from the Raspberry Pi and mount it into another linux system.
- Run these commands to backup/restore. Replace source/destination appropriately.
    - Backup to file: `sudo dd if=/dev/sdb of=~/dingo_backup.img bs=4M status=progress`
    - Restore back to sdcard: `sudo dd if=dingo_backup of=/dev/sdb bs=4M status=progress`

#### Servo Calibration
Help with getting the servos calibrated
 - View the CalibrateServos script itself for additional instructions on dialing in servos.
 - (dingo_hardware_interfacing/dingo_servo_interfacing/src/dingo_servo_interfacing/CalibrateServos.py)
 - Example commands:
    - `rosrun dingo_servo_interfacing CalibrateServos all cal` (move all servos to calibration position)
    - `rosrun dingo_servo_interfacing CalibrateServos fr high` (move front right servo to high position)

### Docker Container
The files inside the base directory enable a docker container to be built and the code to inspected and debugged in visual studio code. This is mostly for debugging purposes, and is best for an external device debugging or adding to the code, rather than being used on the quadruped itself. Note: These instructions assume a linux OS.
#### Preparing vscode
- Install [docker](https://docs.docker.com/engine/install/ubuntu/)
- Install [vscode](https://code.visualstudio.com/docs/setup/linux)
- Open vscode and add the following extensions: [C/C++ Extension Pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools-extension-pack), [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker), [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers), [ROS](https://marketplace.visualstudio.com/items?itemName=ms-iot.vscode-ros)
- close vscode once extensions are installed

#### Building and/or opening the container in vscode
- In terminal, open the base folder containing the dingo quadruped code: `cd ~/any_folder_name/DingoQuadruped`
- run `code .` to open the dingo quadruped base folder in vscode
- A prompt will appear saying either to build the container or run it, click "build" or "run"
- Wait for the container to be built and initialised
- (First time only) Once the container is built, Check that "ROS1.noetic" appears in the bottom left to indicate that the ros extension has correctly detected the ros version inside the container. If it does not appear, follow [these steps](https://youtu.be/JbBMF1aot5k?t=356)

## Running the code
### Dingo_Driver
The Dingo_Driver should be started before any other code is launched on the Dingo. It starts joystick control of the robot and allows joint and task space commands to be received from other code or controllers via command ROS topics, as long as joystick control is disabled. If enabled, joystick control will override any commands sent through the command topics. To launch it, run the following line:
`roslaunch dingo dingo.launch`

Arguments are:
- is_physical (0/1): Is the code being run on the Dingo itself? Default: "1" (Yes)
- is_sim (0/1): Should the code publish joint values to the simulator? Default: "0" (No)
- use_joystick (0/1): Is a joystick being used for control? Default: "1" (Yes)
- use_keyboard (0/1): Is the keyboard being used for control? Default: "0" (No)
- (currently not used) serial_port (name of port): The serial port that the nano is connected to. Default: "/dev/ttyS0"
- use_imu (0/1): Should IMU data be used to correct the robots joint angles? Default: "0" (No)

With no arguments specified, it will assume a joystick controller is used for control and it will launch the hardware interface with IMU feedback disabled. No joint data will be published for Gazebo to use to simulate the robot.

As an example of how the arguments can be used, if the code is to be run purely in simulation with joystick control, you would launch the driver with the following arguments: 
`roslaunch dingo dingo.launch is_physical:=0 is_sim:=1`

### Dingo Joystick Controls
<p align="center">
    <img src="assets/joystick control map.jpg" style="align:centre" width="50%">
</p>

The diagram above shows the mapping of joystick commands for the Dingo. These instructions are based on a PS4 type controller. An alternative, more general description of joystick commands is below:

The Dingo has two main states: Rest and Trot. 
- While in the TROT state: Left stick controls the robot's movement. Right stick controls the robot's tilt and turning.
- While in the REST state: Left stick is disabled. Right stick controls the robot's gaze while staying in place.

Buttons:
- Joystick Control Toggle (L1 Button): Pause/Resume control from the joystick.
- Gait Toggle (R1 Button): Toggles between trotting and resting modes.
- Hop Request (X button): Perform a hop (Currently not implemented).

Movement: (Speed proportional to how far stick is moved)
- Left Stick (Horizontal): Pushing left or right strafes the robot in that direction.
- Left Stick (Vertical): Push up to move forward, down to move backward.

Gaze:
- Right Stick (Horizontal): Pushing left or right turns the robot in that direction.
- Right Stick (Vertical): Push up to raise front of robot, down to raise back of robot.

Orientation:
- D-pad (Vertical): Pressing up or down adjusts the height of the robot.
- D-pad (Horizontal): Pressing left or right tilts the robot in that direction.

### Launching the gazebo simulation
Make sure dingo_driver is running first, then:
`roslaunch dingo_gazebo simulation.launch`

### Extra Notes on Running in the Docker Container
#### Using the ros workspace in vscode
The ROS extension provides options to roslaunch and rosrun files inside vscode via the inbuilt terminal without needing to use the native linux terminal. The commands to do so are the same as natively. 

To start/stop a roscore daemon inside vscode, you can type `ctrl+shift+P` in vscode, and then type `ROS: Start` to start and `ROS: Stop` to stop the roscore daemon.

To build or rebuild the ros workspace, type `ctrl+shift+B`. If this does not work, you may need to edit the tasks.json file which tells vscode how to build the container. Ensure that the catkin build task defined in tasks.json includes the option `-DCMAKE_BUILD_TYPE=Debug`, as without this the vscode debugger will not work correctly.

An important note, as the entire ros workspace is volume mounted, files can be edited inside the container and reflected in your native linux filesystem and vice versa. This means the code can be changed and debugged in the vscode container but run natively, with all changes being reflected. 

#### Debugging with vscode
The ROS extension has two options to enable debugging. The first is to attach to a running node which you start via the terminal with `rosrun package_name node_name`. The second is to debug from a launch file, where you use the debugger menu in vscode to launch a launch file and then set waypoints in any nodes which the launch file starts. To set this up, please watch [this video](https://youtu.be/N2vqBvPQdhE?list=PL2dJBq8ig-vihvDVw-D5zAYOArTMIX0FA)

If the debugger is not stopping at breakpoints, you may need to edit the tasks.json file which tells vscode how to build the container. Ensure that the catkin build task defined in tasks.json includes the option `-DCMAKE_BUILD_TYPE=Debug`.




