#!/usr/bin/env python

import Jetson.GPIO as GPIO
import time

output_pin = 18 # pin 12 in BCM mapping

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)

    print("starting demo")
    toggle_value = GPIO.HIGH
    try:
        while True:
            time.sleep(1)
            GPIO.output(output_pin, toggle_value)
            toggle_value ^= GPIO.HIGH
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()

