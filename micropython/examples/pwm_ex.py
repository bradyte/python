from machine import Pin , PWM

MAX_VALUE = (2 ** 16) - 1

class fsync:
    def __init__(self, fps, perc):
        self.fps = fps
        self.perc = perc
        self.pwm_pin = 0
        self.pwm = PWM(Pin(self.pwm_pin))
        self.pwm.freq(self.fps)
        self.pwm.duty_u16(int(self.perc * MAX_VALUE))


fsync0 = fsync(fps=30, perc=0.10)
