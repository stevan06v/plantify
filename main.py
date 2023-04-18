import _thread
import time
from machine import Pin, ADC

def calcAvg(vals):
    sum = 0
    for i in range(0, len(vals)):
        sum += vals[i]
    return sum / len(vals)

def readSoilSensor():
    
    # init
    soil = ADC(Pin(26))
    delay = 0.5
    counter = 0
    vals = []

    # assign the values from the calibrator.py to the vars underneath
    maxVal = 65535
    minVal = 0

    while True:
        if counter <= 10:
            # get the 16-bit integer value from the sensor
            currVal = soil.read_u16()

            # calculate the average with this formular: ((max-x)*100) - ()
            perc_val = ((maxVal-currVal) * 100) / (maxVal-minVal)

            vals.append(perc_val)

            counter = counter + 1
        else:
            print("Average humidity for " + "[" + counter + "] iterations: " + calcAvg(vals))

            # reset counter
            counter = 0

        # set delay to get accurate sensor-values
        time.sleep(delay)
        pass

def while2():
    # Add code for while loop 2 here
    while True:
        print("test 2")
        time.sleep(1)
        pass

def runLcdDisplay():
    print("LCD screen is running")


_thread.start_new_thread(readSoilSensor, ())
_thread.start_new_thread(while2, ())
_thread.start_new_thread(runLcdDisplay,())
