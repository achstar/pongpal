from machine import ADC, Pin
import neopixel
import time

# Configuration
NUM_LEDS_PER_SEGMENT = 9  # Number of LEDs per NeoPixel strip
PINS = [2, 3, 6, 8, 7, 4, 5]  # GPIO pins for each segment (A-G)

# Initialize NeoPixel objects for each strip
segments = [neopixel.NeoPixel(Pin(pin, Pin.OUT), NUM_LEDS_PER_SEGMENT) for pin in PINS]

# Initialize button and ADC input pins
adc = ADC(Pin(27))
button_dec = Pin(10, Pin.IN)
button_inc = Pin(11, Pin.IN)
button_sel = Pin(12, Pin.IN)

# Hexadecimal digit to 7-segment mapping (A-G)
HEX_TO_SEGMENTS = {
    0: [1, 1, 1, 1, 1, 1, 0],
    1: [0, 1, 1, 0, 0, 0, 0],
    2: [1, 1, 0, 1, 1, 0, 1],
    3: [1, 1, 1, 1, 0, 0, 1],
    4: [0, 1, 1, 0, 0, 1, 1],
    5: [1, 0, 1, 1, 0, 1, 1],
    6: [1, 0, 1, 1, 1, 1, 1],
    7: [1, 1, 1, 0, 0, 0, 0],
    8: [1, 1, 1, 1, 1, 1, 1],
    9: [1, 1, 1, 1, 0, 1, 1],
    10: [1, 1, 1, 0, 1, 1, 1],  # A
    11: [0, 0, 1, 1, 1, 1, 1],  # b
    12: [1, 0, 0, 1, 1, 1, 0],  # C
    13: [0, 1, 1, 1, 1, 0, 1],  # d
    14: [1, 0, 0, 1, 1, 1, 1],  # E
    15: [1, 0, 0, 0, 1, 1, 1],  # F
}

def set_segment_color(segment, color):
    """
    Set all LEDs in a segment to the specified color.
    :param segment: Segment index (0-6, representing A-G)
    :param color: (R, G, B) tuple for the color
    """
    for i in range(NUM_LEDS_PER_SEGMENT):
        segments[segment][i] = color
    segments[segment].write()

def display_number(num):
    """
    Light up the NeoPixel 7-segment display to show the number.
    :param num: Number (0-F) to display
    """
    # Turn off all segments
    for segment in range(7):
        set_segment_color(segment, (0, 0, 0))
    
    # Turn on the segments for the given number
    if num in HEX_TO_SEGMENTS:
        for segment, is_on in enumerate(HEX_TO_SEGMENTS[num]):
            if is_on:
                set_segment_color(segment, (255, 0, 0))  # Red color

def update_button(i, sel):
    if (button_sel.value() == sel):
        if (button_dec.value()):
            print("decrement button pressed!")
            if i == 15:
                i = 0
            else:
                i += 1
            display_number(i)
        elif (button_inc.value()):
            print("increment button pressed!")
            if i == 0:
                i = 15
            else:
                i -= 1
            display_number(i)
    return i

try:
    display_number(0)
    i = 0
    adcRead = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    while True:
        adcRead.pop(0)
        
        adcRead.append(adc.read_u16())
        if (sum(adcRead) > 300000):
            adcRead = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            print("here1", adc.read_u16())
            if i == 15:
                i = 0
            else:
                i += 1
            
            display_number(i)
            time.sleep_ms(1000) # debounce
        else:
            print("here3")
            i = update_button(i, False) # one board should be false, one should be true
            time.sleep_ms(250) # debounce
            
    #while True:
    #    for i in range(16):  # 0 to F
    #        display_number(i)
    #        print(i)
    #        time.sleep(1)
            
except KeyboardInterrupt:
    # Turn off all LEDs on exit
    for segment in range(7):
        set_segment_color(segment, (0, 0, 0))
