import time
from machine import ADC, Pin
import utime


soil = ADC(Pin(26))


soil.read_u16
