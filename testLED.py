#!/usr/bin/env python

import Jetson.GPIO as GPIO
import time

output_pin = 18 # pin 40 in BCM mapping

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)

    print("starting demo")
    toggle_value = True
    try:
        while True:
            time.sleep(1)
            if (toggle_value):
                GPIO.output(output_pin, GPIO.LOW)
                toggle_value = False
            else:
                GPIO.output(output_pin, GPIO.HIGH)
                toggle_value = True
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()

