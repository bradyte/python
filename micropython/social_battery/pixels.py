# Example using PIO to drive a set of WS2812 LEDs.

import array, time
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

class PIXELS:
    colors = {
        'red':      0xff0000,
        'orange':   0xff8000,
        'yellow':   0xffff00,
        'green':    0x00ff00,
        'cyan':     0x00ffff,
        'blue':     0x0000ff,
        'purple':   0x8000ff,
        'magenta':  0xff00ff,
        'pink':     0xff0080,
        'white':    0xffffff,
        'black':    0x000000

    }

    battery_states = [  [colors['black']] * 0 + [colors['green']] * 8,
                        [colors['black']] * 1 + [colors['green']] * 7,
                        [colors['black']] * 2 + [colors['green']] * 6,
                        [colors['black']] * 3 + [colors['green']] * 5,
                        [colors['black']] * 4 + [colors['yellow']] * 4,
                        [colors['black']] * 5 + [colors['yellow']] * 3,
                        [colors['black']] * 6 + [colors['red']] * 2,
                        [colors['black']] * 7 + [colors['red']] * 1,
                        [colors['black']] * 8 + [colors['red']] * 0]

    def __init__(self, pin_number, num_leds, brightness=0.1):
        self.pin_number = pin_number
        self.num_leds = num_leds
        self.sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(self.pin_number))
        self.RGB_array = array.array("I", [0 for _ in range(self.num_leds)])
        self.brightness_array = array.array("f", [brightness for _ in range(self.num_leds)])

        self.sm.active(1)

    def set_pixel(self, i, color):
        if isinstance(color, str):  # first check if it's a string or hex number
            try:  # check if the string is part of the colors dictionary
                self.RGB_array[i] = self.colors[color]
            except KeyError:
                print(f'The color {color} is currently not a predefined color.')
        else:
            self.RGB_array[i] = color

    def fill_pixels_array(self, color_array):
        assert len(color_array) == self.num_leds, f"color array length [{len(color_array)}] is different length than number of LEDs[{self.num_leds}]"
        for i, color in enumerate(color_array):
            self.set_pixel(i, color)

    def show_pixels(self):
        dimmer_ar = array.array("I", [0 for _ in range(self.num_leds)])
        # The color of each LED is encoded as three LED brightness values
        for i, c in enumerate(self.RGB_array):
            r = int(((c >> 16) & 0xFF) * self.brightness_array[i])
            g = int(((c >> 8) & 0xFF) * self.brightness_array[i])
            b = int((c & 0xFF) * self.brightness_array[i])
            dimmer_ar[i] = (g << 16) + (r << 8) + b  # sent in GRB (green-red-blue)
        self.sm.put(dimmer_ar, 8)
        # time.sleep_ms(10)

    def angle_to_rgb(self, angle):
        angle = angle % 360
        segment = angle // 60
        position = (angle % 60) / 60.0

        r, g, b = 0, 0, 0

        if segment == 0:
            r, g, b = 1, position, 0
        elif segment == 1: 
            r, g, b = 1 - position, 1, 0
        elif segment == 2: 
            r, g, b = 0, 1, position
        elif segment == 3: 
            r, g, b = 0, 1 - position, 1
        elif segment == 4: 
            r, g, b = position, 0, 1
        elif segment == 5: 
            r, g, b = 1, 0, 1 - position

        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        return (r << 16) + (g << 8) + b
    
    def life_meter(self):
        for i in range(self.num_leds + 1):
            meter = [self.angle_to_rgb(120 - (120 // (self.num_leds-1)) * i)] * (self.num_leds - i) + [self.colors['black']] * i
            self.fill_pixels_array(meter)
            self.show_pixels()
            time.sleep(0.01)


def main():
    p = PIXELS(0, 64, 0.1)
    # while(1):
        # for i in range(360):
        #     b.set_pixel(6, b.angle_to_rgb(i))
    while(1):
        for i in range(360):
            p.fill_pixels_array([p.angle_to_rgb(i)] * p.num_leds)
            p.show_pixels()


if __name__ == "__main__":
    main()