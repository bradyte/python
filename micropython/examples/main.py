# Example using PIO to drive a set of WS2812 LEDs.

import array, time
import math
import random
from machine import Pin
import rp2

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)
 
 
def rainbow_cycle(wait):
    for j in range(255):
        for i in range(NUM_LEDS):
            rc_index = (i * 256 // NUM_LEDS) + j
            pixels_set(i, wheel(rc_index & 255))
        pixels_show()
        time.sleep(wait)

BLACK = (0, 0, 0)
RED = (255, 10, 0)
YELLOW = (255, 150, 10)
GREEN = (10, 255, 10)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
COLORS = (BLACK, RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE)


battery_states = [	(BLACK,) * 0 + (GREEN,) * 8,
                    (BLACK,) * 1 + (GREEN,) * 7,
                    (BLACK,) * 2 + (GREEN,) * 6,
                    (BLACK,) * 3 + (GREEN,) * 5,
                    (BLACK,) * 4 + (YELLOW,) * 4,
                    (BLACK,) * 5 + (YELLOW,) * 3,
                    (BLACK,) * 6 + (RED,) * 2,
                    (BLACK,) * 7 + (RED,) * 1,
                    (BLACK,) * 8 + (GREEN,) * 0]



class BATTERY:
    def __init__(self, pin_number, num_leds, brightness):
        self.pin_number = pin_number
        self.num_leds = num_leds
        self.sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(self.pin_number))
        self.GRB_array = array.array("I", [0 for _ in range(self.num_leds)])
        self.brightness_array = array.array("f", [brightness for _ in range(self.num_leds)])

        self.sm.active(1)


    def pixels_set(self, i, color):
        # The color of each LED is encoded as three LED brightness values, which must be sent in GRB (green-red-blue)
        self.GRB_array[i] = (color[1] << 16) + (color[0] << 8) + color[2]

    def pixels_fill_array(self, color_array):
        assert len(color_array) == self.num_leds, "color array is different length than number of LEDs"
        for i, color in enumerate(color_array):
            self.pixels_set(i, color)

    def pixels_show(self):
        dimmer_ar = array.array("I", [0 for _ in range(self.num_leds)])
        for i, c in enumerate(self.GRB_array):
            r = int(((c >> 8) & 0xFF) * self.brightness_array[i])
            g = int(((c >> 16) & 0xFF) * self.brightness_array[i])
            b = int((c & 0xFF) * self.brightness_array[i])
            dimmer_ar[i] = (g << 16) + (r << 8) + b
        self.sm.put(dimmer_ar, 8)
        time.sleep_ms(10)

    
    
    def wheel(self, pos):
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            return (0, 0, 0)
        if pos < 85:
            return (255 - pos * 3, pos * 3, 0)
        if pos < 170:
            pos -= 85
            return (0, 255 - pos * 3, pos * 3)
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

def main():
    battery = BATTERY(0, 8, 0.1)
    battery.pixels_fill_array((GREEN,) * 8)
    rate = 8
    while(1):
        # for i in range(battery.num_leds):
        #     for j in range (255):
        #         battery.pixels_set(i, battery.wheel(j))
        #         battery.pixels_show()
        #     battery.pixels_set(i, BLACK)
        #     battery.pixels_show()
        # rate_pin.toggle()
        # for i in range(360 // rate):
            
        #     battery.brightness = math.sin(math.radians(i * rate)) / 2 + 0.5
        battery.brightness_array = [random.random() / 10 for _ in range(1, battery.num_leds+1)]
        time.sleep(0.1)
        battery.pixels_show()

if __name__ == "__main__":
    main()
