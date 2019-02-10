# MoodMirror
MoodMirror is a simply Python script for a Raspberry Pi 3B that uses either Azure or Google emotion detection APIs to detect the emotions of any faces seen in the mirror, and then update a strip of RGB LEDs to reflect the person's expressed emotion. In the original build of this, the LEDs were placed behind a mirror and the camera on top of the mirror, thus the name "MoodMirror"

MoodMirror performs simple difference checking of images captured to ensure cloud services are only used when motion occurs.

## Hardware Parts Needed
### Core Parts
- Mirror
- http://amzn.to/2ofvGGI : Raspberry Pi 3 Model B (don't forget an SD card). Pi Zero is also possible, but the set up would be a bit harder.
- http://amzn.to/2oU2dAT : Raspberry Pi Camera Module V2
- http://amzn.to/2oTWJG6 : WS2812B Individually Addressable LED Strip 16.4ft 150 SMD
- http://amzn.to/2owSRbE : Wsdcam 5 Pairs 5.5x2.1mm Male and Female DC Power Jack 
- http://amzn.to/2pPGo3P : Adafruit Accessories Quad Level-Shifter
- http://amzn.to/2qCNzvW : Solderable PI HAT breadboard

### Solderless
_(replacing the PI HAT)_
- http://amzn.to/2ozVYyN : Solderless breadboard
- http://amzn.to/2ofOR3c : M/M solderless breadboard jumpers
- http://amzn.to/2p79AoZ : M/F solderless breadboard jumpers

### Power Supply
_(go with the 10A if you need more than about 45 pixels)_
- http://amzn.to/2pooAzY : Wall Mount AC Adapters 5V 2A (2000mA)
- http://amzn.to/2p6wzhi : 5V 10A AC Adapter

... there are also lots of camera and PI3 cases to choose from, depending on your application.
    I used the CanaKit clear case that came in the Pi kit at http://amzn.to/2wSHFct

## Wiring
1. Connect the LED strip as shown in the "Level-converter chip wiring" section of:
   https://learn.adafruit.com/neopixels-on-raspberry-pi/wiring
   * **NOTE:** The PI3 will not sit on the broadboard, but pin 6 (GND) and 12 (GPIO #18) are in the same spot.  Also, connect V+ to pin 2 (5V)

2. Connect the camera

## Setup Steps
1. Use Etcher to write raspbian-stretch image to SD card
   https://www.raspberrypi.org/downloads/raspbian/
   (if you use the lite version, you'll need to install a bunch of other software - easy enough to use full)

2. add "ssh" file to SD card root (no contents or extension)
   * If you have a Pi 3 Model B, fix a few params that screw with neopixel LEDs edit config.txt on the flashed drive, add:
     ```ini
     hdmi_force_hotplug=1
     hdmi_force_edid_audio=1
     ```
3. Connect ethernet cable, ssh:
   ```bash
   sudo vi /etc/wpa_supplicant/wpa_supplicant.conf
   ```
   add the following to the bottom of the file:
   ```json
   network={
       ssid="your-network-ssid-name"
       psk="your-network-password"
   }
   ```
   save, close
   
   Update the firmware and distro:
   ```bash
   sudo apt-get update
   sudo apt-get upgrade
   sudo apt-get dist-upgrade
   sudo rpi-update
   ```

4. Remove ethernet cable, power off

5. Power on, reconnect via ssh (over wifi)
   ```bash
   run "vcgencmd get_camera"
   ```
   * if the camera is disabled:
     ```bash
     run "sudo raspi-config"
     ```
     choose "configure peripherals"
     Enable the camera
     save, reboot

6. Update pip:
   ```bash
   sudo pip3 install --upgrade pip
   ```

7. Install a few libraries:
   ```bash
   sudo apt-get install libjpeg8-dev
   sudo pip3 install --upgrade Pillow
   sudo apt-get upgrade python-picamera
   ```

8. Compile and install the rpi_ws281x library for neopixel
   https://learn.adafruit.com/neopixels-on-raspberry-pi/software
   (note: for the "sudo python setup.py install" step, also run it using python3)
   
9. Microsoft Azure Cloud Setup:
    * Go to https://portal.azure.com
    * Create a new "Cognitive Services account" _(API type: Emotion API)_
    * From the dashboard, select your new emption API service, then select "Keys" on the left  
    * Copy "Key 1" and place it at the top of moodmirror-ms.py (api_key)   
    * Copy moodmirror-ms.py, imagecompare.py, launcher.sh, truncate.cfg, and colorblend.py to /home/pi   
      ```bash
      run "chmod 755 launcher.sh"
      run "sudo chown root:root /home/pi/truncate.cfg"

      run "./launcher.sh"
      ```
      ... CTRL-C when satisfied
    
10. Run "sudo crontab -e" (pick your favorite editor

    At the end of the file, add:
    ```cron
    @reboot sh /home/pi/launcher-ms.sh >>/home/pi/moodmirror-ms.log 2>&1
    @hourly logrotate /home/pi/truncate.cfg > /dev/null 2>&1
    ```    
    Save, exit

## Troubleshooting
1. If you need to kill the script, ssh in an run:
   ```bash
   ps -aux | grep python3
   ``` 
   Get the PID for "python3 moodmirror-ms.py", then run:
   ```bash   
   sudo kill -9 PID
   ```
   (where PID is what you found in the prior step)

## Google
I stopped developing this when I realized Azure was better at detecting emotions. If you want to use GCP, you'll probably want to copy the MS script and put back the Google detect_faces function. As for the cloud service, follow the "Google Cloud Set Up" steps on: https://www.dexterindustries.com/howto/use-google-cloud-vision-on-the-raspberry-pi/
    
* Install the Google python library:
  ```bash
  sudo pip3 install --upgrade google-api-python-client
  sudo pip3 install --upgrade google-cloud-vision
  ```
* Get credentials, and put them in a json file as instructed
* Update the json file name at the top of moodmirror-google.py
* Copy moodmirror-google.py, imagecompare.py, and colorblend.py to /home/pi    
* sudo python3 moodmirror-google.py
