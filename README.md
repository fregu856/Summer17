# Summer17

Pictures from the build:  
https://goo.gl/photos/LKZvyXHjr5Y9rBLAA

https://drive.google.com/file/d/0B8u1-N9yBAQoOVZDZGI4dDNPdjQ/view

******

### Setup: Raspbian RPI (for video streaming, communication with the laptop and actuator control)

Install the latest verison of Raspian:
- Download Raspbian with desktop: https://www.raspberrypi.org/downloads/raspbian/
- Write the downloaded image to the micro-SD card: https://www.raspberrypi.org/documentation/installation/installing-images/
- Insert micro-SD into the RPI, power it up and follow the instructions (need HDMI cable and usb mouse & keyboard)

Enable SSH, the camera and I2C:
- Menu > Preferences > Raspberry Pi Config > Interfaces
- Click "Enabled" for Camera, SSH and I2C
- Restart the RPI

Setup the RPI as a wifi hotspot:
- https://frillip.com/using-your-raspberry-pi-3-as-a-wifi-access-point-with-hostapd

(If one would like to have the RPI and computer connected to the same router and send wifi data that way, you might have to make the following modifications in order to be able to connect to the RPI via ssh:  
- Add the line "IPQoS 0x00" to the bottom of the files "/etc/ssh/ssh_config" and "/etc/ssh/sshd_config" on the RPI and then reboot it.)

Another problem you might run into is that you can't install anything using pip on the RPI. The solution is, strangely, to set the date and time properly:  
- $ sudo date -s "Jul 7 18:31" (where you replace "Jul 7 18:31" with your current date and time)

*****

### Setup: Ubuntu RPI (for reading the LiDAR)

Install Ubuntu Mate:  
http://turtlebot3.robotis.com/en/latest/sbc_software.html (See 6.1) (Download the file, burn the image onto the micro-SD card using e.g. Etcher, insert micro-SD into RPI, power it up and follow the instructions (need HDMI cable and usb mouse & keyboard)) (Choose a username and password of your liking, you'll use it to SSH into the RPI)

Install ROS:
- $ sudo apt-get update
- $ sudo apt-get upgrade
- $ wget https://raw.githubusercontent.com/ROBOTIS-GIT/robotis_tools/master/install_ros_kinetic.sh && chmod 755 ./install_ros_kinetic.sh && bash ./install_ros_kinetic.sh

Setup and test the LiDAR:
- $ sudo apt-get install ros-kinetic-hls-lfcd-lds-driver
- $ sudo chmod a+rw /dev/ttyUSB0 (do this when the LiDAR is plugged into the RPI, YOU HAVE TO DO THIS EVERYTIME YOU RESTART THE UBUNTU RPI!) (make sure the USB cable connecting the LiDAR with the RPI is NOT charge-only)
- $ roslaunch hls_lfcd_lds_driver hlds_laser.launch (the LiDAR should now start turning and publish messages to /scan, check this with the command $ rostopic echo /scan)

Enable SSH:
- $ sudo apt-get install raspi-config rpi-update
- $ sudo raspi-config
- Select "Interfacing Options"
- Select "SSH", select "Yes"
- Reboot to confirm the changes

Make it connect to the WiFi network of the Raspian RPI on boot:  
- Press on the WiFi symbol and select "Edit Connections"
- Select the RPI network and click Edit
- Below "General", make sure that "Automatically connect to this network when it is available" is selected
- Edit any other networks you previously have connected to and make sure that "Automatically connect to this network when it is available" is NOT selected

*****

### Setup: Laptop

Install ROS:
- TODO!

Install needed ROS packages:
- Catkin:
- - TODO!
- rviz:
- - TODO!
- TODO!

Install required packages:
- OpenCV
- TODO!

Create and build a catkin workspace (placed in Summer17/Laptop/ROS_code):
- $ cd Summer17/Laptop/
- $ mkdir ROS_code
- $ cd ROS_code
- $ mkdir catkin_ws
- $ cd catkin_ws/
- $ mkdir src
- $ cd ~/Summer17/Laptop/ROS_code/catkin_ws
- $ catkin_make
- $ source ~/Summer17/Laptop/ROS_code/catkin_ws/devel/setup.bash
- Add the above line (source ~/Summer17/Laptop/ROS_code/catkin_ws/devel/setup.bash) to the bottom of ~/.basrhrc ($ sudo nano ~/.bashrc to open and edit it) for it to be run everytime you open a terminal

Create and build a package (called test_pckg) in the catkin workspace:
- $ cd ~/Summer17/Laptop/ROS_code/catkin_ws/src
- $ catkin_create_pkg test_pckg std_msgs roscpp rospy
- $ cd ~/Summer17/Laptop/ROS_code/catkin_ws
- $ catkin_make
- Create a scripts directory in the package (it's in this directory we would place all python ROS code/scripts):
- - $ cd ~/Summer17/Laptop/ROS_code/catkin_ws/src/test_pckg
- - $ mkdir scripts
- Every python script that one writes and places in scripts (e.g. test.py) must be made executable:
- - $ chmod a+x test.py
- You should always also build the package (this is sometimes (quite often) needed even for python scripts since we use C++ messages):
- - $ cd ~/Summer17/Laptop/ROS_code/catkin_ws
- - $ catkin_make

****

Setup of ROS IP addresses:
- Connect both the laptop and the Ubuntu RPI to the Raspian RPI wifi
- SSH into the Ubuntu RPI (to do this you need its IP address, you obtain this by running $ ifconfig when it's connected to the Raspbian RPI wifi. Its  IP address is found as "inet addr" below "wlan0". In my case I got: 172.24.1.57)
- Note the laptop's IP address (by running $ ifconfig. In my case I got: 172.24.1.72) 
- In the Ubuntu RPI terminal:
- - $ sudo nano ~/.bashrc
- - Replace the second-to-last line "export ROS_MASTER_URI=http://localhost:11311" with "export ROS_MASTER_URI=http://172.24.1.72:11311" (where 172.24.1.72 is the IP address of the laptop)
- - Replace the last line "export ROS_HOSTNAME=localhost" with "export ROS_HOSTNAME=172.24.1.57" (where 172.24.1.57 is the IP address of the Ubuntu RPI)
- - $ source ~/.bashrc
- In the laptop terminal:
- - $ sudo nano ~/.bashrc
- - Add the following two lines to the bottom of the file: "export ROS_MASTER_URI=http://172.24.1.72:11311" and "export ROS_HOSTNAME=172.24.1.72" (where again, 172.24.1.72 is the laptop's IP address)
- - $ source ~/.bashrc
- To test that everything works:
- - [Laptop terminal 1] $ roscore
- - [Ubuntu RPI terminal] $ roslaunch hls_lfcd_lds_driver hlds_laser.launch (the LiDAR should now start spinning, it might however take a few seconds)
- - [Laptop terminal 2] $ rostopic echo /scan (a stream of scan messages should now start appearing in the terminal)
- To also visualize the LiDAR measurements on the laptop using rviz:
- - Create a directory called "rviz" in the package test_pckg:
- - - $ cd ~/Summer17/Laptop/ROS_code/catkin_ws/src/test_pckg
- - - $ mkdir rviz
- - Create a file called "basic_lidar_visualization.rviz" that is a copy of the file "hlds_laser.rviz" in https://github.com/ROBOTIS-GIT/hls_lfcd_lds_driver and place it in the rviz directory AND make it executable
- - [Laptop terminal 1] $ roscore
- - [Ubuntu RPI terminal] $ roslaunch hls_lfcd_lds_driver hlds_laser.launch
- - [Laptop terminal 2] $ rosrun rviz rviz -d /home/fregu856/Summer17/Laptop/ROS_code/catkin_ws/src/test_pckg/rviz/basic_lidar_visualization.rviz (rviz should now open and you should see some green/yellow/red lines/dots)

****

Run SLAM on the laptop using Hector SLAM (only using the LiDAR scans, the car does currently not offer any odometry measurements):
- Useful links: http://wiki.ros.org/hector_slam/Tutorials/SettingUpForYourRobot, https://github.com/tu-darmstadt-ros-pkg/hector_slam/blob/catkin/hector_slam_launch/rviz_cfg/mapping_demo.rviz, https://github.com/tu-darmstadt-ros-pkg/hector_slam/blob/catkin/hector_slam_launch/launch/mapping_box.launch
- $ cd ~/Summer17/Laptop/ROS_code/catkin_ws/src
- $ git clone https://github.com/tu-darmstadt-ros-pkg/hector_slam.git
- $ cd ~/Summer17/Laptop/ROS_code/catkin_ws
- $ catkin_make
- Create a directory called "launch" in /home/fregu856/Summer17/Laptop/ROS_code/catkin_ws/src/test_pckg
- Write test_Hector.launch (based on the above links) and place it in the above directory
- Write test_Hector.rviz (based on mapping_demo.rviz linked above) and place it in /home/fregu856/Summer17/Laptop/ROS_code/catkin_ws/src/test_pckg/rviz
- $ cd ~/Summer17/Laptop/ROS_code/catkin_ws
- $ catkin_make
- [Laptop terminal 1] $ roscore
- [Ubuntu RPI terminal] $ roslaunch hls_lfcd_lds_driver hlds_laser.launch
- [Laptop terminal 2] $ roslaunch test_pckg test_Hector.launch

*****
Camera calibration
- TODO!


*****
ORB-SLAM
- TODO!

 



