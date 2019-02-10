import argparse
import picamera
import json
import io
import os

from google.cloud import vision
from google.cloud.vision.likelihood import Likelihood
from neopixel import *

# Set this to the .json file downloaded from the GCP management console
api_keys = "/home/pi/[GCP-API-KEY-FILE].json"

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

# Capture a photo from the pi camera
def takephoto():
    camera = picamera.PiCamera()
    camera.capture('image.jpg')

# Convert the likelihood responses Google gives to a numeric score
def likelihood_to_score(val):
    return {
        Likelihood.VERY_UNLIKELY: 0.0,
        Likelihood.UNKNOWN: 0.0,
        Likelihood.UNLIKELY: 0.25,
        Likelihood.POSSIBLE: 0.50,
        Likelihood.LIKELY: 0.75,
        Likelihood.VERY_LIKELY: 1.00
    }[val]

# Send an image file on disk to the cloud for face and emotion detection
def detect_faces(path):
    """Detects faces in an image."""
    vision_client = vision.Client()

    # Read the image from disk
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision_client.image(content=content)

    # Send the image to Google
    faces = image.detect_faces()

    # Combine the responses, in case there were multiple faces
    anger = []
    joy = []
    surprise = []
    sorrow = []
    for face in faces:
        anger.append(likelihood_to_score(face.emotions.anger))
        joy.append(likelihood_to_score(face.emotions.joy))
        surprise.append(likelihood_to_score(face.emotions.surprise))
        sorrow.append(likelihood_to_score(face.emotions.sorrow))

    print('faces: {}'.format(len(anger)))

    # Calculate the aggregate color
    # default to black (off)
    R = 0
    G = 0
    B = 0
    if len(anger) > 0:
       a_anger = sum(anger) / len(anger)
       a_joy = sum(joy) / len(joy)
       a_surprise = sum(surprise) / len(surprise) 
       a_sorrow = sum(sorrow) / len(sorrow) 


       # Mix the colors
       R, G, B = ink_add_for_rgb([
                                  (255,   0,   0, a_anger),
                                  (255, 255,  84, a_joy),
                                  ( 89, 189, 255, a_surprise),
                                  ( 81,  81, 255, a_sorrow)
                                 ])

    print('R: {}'.format(R))
    print('G: {}'.format(G))
    print('B: {}'.format(B))

    return Color(int(R), int(G), int(B))


def main():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = api_keys

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)

    # Intialize the library (must be called once before other functions).
    strip.begin()


    # TODO: Make this a loop
    takephoto()
    color = detect_faces("image.jpg")
    set_color(strip, color)


if __name__ == '__main__':

    main()

