# Summer17

Pictures from the build:  
https://goo.gl/photos/LKZvyXHjr5Y9rBLAA

******

### Raspbian RPI (for video streaming and communication with the laptop)

If one would like to have the RPI and computer connected to the same router and send wifi data that way, you might have to make the following modifications in order to be able to connect to the RPI via ssh:  
- Add the line "IPQoS 0x00" to the bottom of the files "/etc/ssh/ssh_config" and "/etc/ssh/sshd_config" on the RPI and then reboot it.

Another problem you might run into is that you can't install anything using pip on the RPI. The solution is, strangely, to set the date and time properly:  
- $ sudo date -s "Jul 7 18:31" (where you replace "Jul 7 18:31" with your current date and time)

*****

### Ubuntu RPI (for reading the LiDAR)

Install Linux (Ubuntu Mate) on the RPI:  
http://turtlebot3.robotis.com/en/latest/sbc_software.html (See 6.1) (Download the file, burn the image onto the micro-sd card using e.g. Etcher, insert micro-sd into RPI, power it up and follow the instructions (need HDMI cable and usb mouse & keyboard)) (Choose a username and password of your liking, you'll use it to SSH into the RPI)

Enable SSH:
- $ sudo apt-get install raspi-config rpi-update
- $ sudo raspi-config
- Select "Interfacing Options"
- Select "SSH", select "Yes"
- Reboot to confirm the changes

