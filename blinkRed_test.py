import machine
import neopixel
import time

# Define the number of NeoPixels and the GPIO pin to which the data line is connected
num_pixels = 10
pin = machine.Pin(15)  # Change to the GPIO pin where the data line is connected

# Create a NeoPixel object
np = neopixel.NeoPixel(pin, num_pixels)

def flash_red():
    # Set all pixels to red (RGB)
    for i in range(num_pixels):
        np[i] = (255, 0, 0)  # Red color (maximum red, no green or blue)
    np.write()  # Update the strip to show the colors
    time.sleep(3)  # Keep the strip red for 3 seconds

    # Turn off all pixels
    for i in range(num_pixels):
        np[i] = (0, 0, 0)  # Turn off the LED (all channels 0)
    np.write()  # Update the strip to turn off the LEDs
    time.sleep(3)  # Keep the strip off for 3 seconds

# Main loop
while True:
    print("Hello World")
    flash_red()
