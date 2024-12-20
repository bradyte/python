# Example using PIO to drive a set of WS2812 LEDs.

import array, time
import math
import random
from machine import Pin
from pixels import PIXELS

def main():
    p = PIXELS(0, 64, 0.1)

    while(1):
        for i in range(360):
            p.fill_pixels_array([p.angle_to_rgb(i)] * p.num_leds)
            p.show_pixels()



if __name__ == "__main__":
    main()
