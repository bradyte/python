# Example using PIO to drive a set of WS2812 LEDs.

import array, time
import math
import random
from machine import Pin
from pixels import BATTERY

def main():
    b = BATTERY(0, 8, 0.1)
    while(1):
        b.life_meter()


if __name__ == "__main__":
    main()
