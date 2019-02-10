import argparse
import picamera
import json
import io
import os
import http.client
import urllib.request
import urllib.parse
import urllib.error
import base64
import sys
import time

from neopixel import *
from colorblend import *
from imagecompare import *

# Replace this with your Microsoft API Key 1
api_key = 'PUT_YOUR_KEY_HERE'

# LED strip configuration:
LED_COUNT      = 150     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

def set_color(strip, color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)

    strip.show() 

def detect_faces(path):
    """Detects faces in an image."""

    # Create the request headers
    headers = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': api_key,
    }
    
    params = urllib.parse.urlencode({})

    # Open the image file
    image_file = io.open(path, 'rb')

    # Call the API
    faces = None
    #try:
    conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
    conn.request("POST", "/emotion/v1.0/recognize?%s" % params, image_file, headers)
    response = conn.getresponse()
    faces = json.loads(response.readall().decode('utf-8'))
    conn.close()
    #except Exception as e:
    #    print(e.args)
    #    return

    if faces is None:
        print('Emotion API error')
        return color(0, 0, 0)

    print(faces)

    # Enumerate the response json
    anger = []
    contempt = []
    disgust = []
    fear = []
    happiness = []
    neutral = []
    surprise = []
    sadness = []
    for face in faces:
        anger.append(face['scores']['anger'])
        contempt.append(face['scores']['contempt'])
        disgust.append(face['scores']['disgust'])
        fear.append(face['scores']['fear'])
        happiness.append(face['scores']['happiness'])
        neutral.append(face['scores']['neutral'])
        surprise.append(face['scores']['surprise'])
        sadness.append(face['scores']['sadness'])

    print('faces: {}'.format(len(anger)))

    # default to black (off)
    R = 0
    G = 0
    B = 0
    if len(anger) > 0:
       # Calculate alpha levels as an average of the scores for each emotion
       a_anger = sum(anger) / len(anger)
       a_contempt = sum(contempt) / len(contempt)
       a_disgust = sum(disgust) / len(disgust)
       a_fear = sum(fear) / len(fear)
       a_happiness = sum(happiness) / len(happiness)
       a_neutral = sum(neutral) / len(neutral)
       a_surprise = sum(surprise) / len(surprise)
       a_sadness = sum(sadness) / len(sadness)

       # Mix the colors
       R, G, B = ink_add_for_rgb([
                                  (255,   0,   0, a_anger),
                                  (255, 175, 197, a_contempt),
                                  (255,  84, 255, a_disgust),
                                  (  0, 150,   0, a_fear),
                                  (255, 255,  84, a_happiness),
                                  (100, 100, 100, a_neutral),
                                  ( 89, 189, 255, a_surprise),
                                  ( 81,  81, 255, a_sadness)
                                 ])

    return Color(R, G, B)


def main():
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 0, ws.WS2811_STRIP_GRB)

    # Intialize the library (must be called once before other functions).
    strip.begin()

    # Initialize the camera
    camera = picamera.PiCamera()

    imgidx = 0
    prev_imgname = None
    while True:
        try:
            imgname = 'image{}.jpg'.format(imgidx)
            print("Capturing image...")
            camera.capture(imgname)

            print("Checking locally for differences...")
            diff = 1.0
            if prev_imgname != None:
                # Compare the new image and the old
                # Image3 is too slow (about 3 seconds), but should use anything > 0.08
                diff = Images2(imgname, prev_imgname).DoComparison()               
            
            print('difference={}'.format(diff))           
            prev_imgname = imgname
            if imgidx == 0:
                imgidx = 1
            else:
                imgidx = 0
            
            # Is this worth submitting?
            if diff > 0.8:
                print("Determining face emotion...")
                color = detect_faces(imgname)
            
                print("Updating strip color to (#{:06X})...".format(color))
                set_color(strip, color)
            # Free tier of Microsoft's emotion API is limited to 20 calls per minute (one every 3 seconds)
            time.sleep(2)
        except KeyboardInterrupt:
            break
        except:
            pass


if __name__ == '__main__':

    main()

