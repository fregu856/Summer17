# Summer17

Pictures from the build:  
https://goo.gl/photos/LKZvyXHjr5Y9rBLAA

https://drive.google.com/file/d/0B8u1-N9yBAQoOVZDZGI4dDNPdjQ/view

******

### Raspbian RPI (for video streaming, communication with the laptop and actuator control)

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

### Ubuntu RPI (for reading the LiDAR)

Install Ubuntu Mate:  
http://turtlebot3.robotis.com/en/latest/sbc_software.html (See 6.1) (Download the file, burn the image onto the micro-SD card using e.g. Etcher, insert micro-SD into RPI, power it up and follow the instructions (need HDMI cable and usb mouse & keyboard)) (Choose a username and password of your liking, you'll use it to SSH into the RPI)

Install ROS:
- $ sudo apt-get update
- $ sudo apt-get upgrade
- $ wget https://raw.githubusercontent.com/ROBOTIS-GIT/robotis_tools/master/install_ros_kinetic.sh && chmod 755 ./install_ros_kinetic.sh && bash ./install_ros_kinetic.sh

To use the LiDAR:
- $ sudo apt-get install ros-kinetic-hls-lfcd-lds-driver
- $ sudo chmod a+rw /dev/ttyUSB0 (do this when the LiDAR is plugged into the RPI)
- $ roslaunch hls_lfcd_lds_driver hlds_laser.launch (the LiDAR should now start turning and publish messages to /scan)

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

### Laptop

Install ROS:
- Test

Install required packages:
- OpenCV
- 
- 

****

Setup of ROS IP addresses:
- Connect both the laptop and the Ubuntu RPI to the Raspian RPI wifi
- 

