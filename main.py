import dht
from machine import Pin, ADC
import time
import uasyncio
import uos


# init
calibrationFile = 'capacitive-soil-sensor-calibration.csv'
dryMoisture = 0
wetMoisture = 65535

print("Initializing the (dht11) sensor...")
dht11 = dht.DHT11(Pin(4))

print("Initializing the (capacitive-soil-sensor)...")
soil = ADC(Pin(26))


print("(capacitive-soil-sensor) Calibrating min/max values...")

def checkIfCalibrationExits():
    try:
        stat = uos.stat(calibrationFile)
        print("File '{}' exists.".format(calibrationFile))
        print("File size: {} bytes".format(stat[6]))
        return True
    except OSError as e:
        if e.args[0] == 2:  
            print("File '{}' does not exist.".format(calibrationFile))
        else:
            print("An error occurred while checking file existence:", e)
        return False

def calculateAverage(vals):
    sum = 0 
    for iterator in vals:
        sum = sum + iterator
    return int(sum / len(vals))

def readSoilSensorValues():
    count = 1
    vals = []
    while count <= 15:
        vals.append(soil.read_u16())
        print(str(15 - count) + "sec remaining...");
        count = count + 1
        time.sleep(1)
    return vals

def writeCalibrationValues(dry, wet):
    # Open the CSV file for writing
    with open(calibrationFile, 'w') as file:
        # Write the dry and wet moisture values to the file
        file.write("{},{}".format(dry, wet))

    print("capacitive-soil-sensor-calibration '{}' has been written successfully.".format(calibrationFile))


if checkIfCalibrationExits() is True:
    print("No calibration neccessary. Reading calibrated values...")
    
    
else:
    print("Hi, you are now calibrating the sensor!")
    print("Follow the steps below to calibrate the sensor right.")
    time.sleep(5)
    
    print("=====================================================")
    print("Put the capacitive-soil-sensor in water...")
    print("=====================================================")
    
    print("Waiting 10 secounds...(then reading)");
    time.sleep(10)
    
    print("=====================================================")
    print("Now put the sensor into the water!");
    print("=====================================================")
    
    time.sleep(3)
    
    # get sensor values
    vals = readSoilSensorValues()
        
    wetMoisture = calculateAverage(vals)
    
    
    print("=====================================================")
    print("Dry the capacitive-soil-sensor and put it into dry soil.")
    print("=====================================================")
    
    print("Waiting 10 secounds...(then reading)");
    time.sleep(10)
    
    print("=====================================================")
    print("Now put the sensor into the dry soil!");
    print("=====================================================")
    time.sleep(3)
    
    vals = readSoilSensorValues()
    dryMoisture = calculateAverage(vals)
    
    writeCalibrationValues(wetMoisture, dryMoisture)
    
    print("=====================================================")
    print("Capacitive-soil-sensor got calibrated successfully.")
    print("=====================================================")
    
    
async def readDHT11Values(sleepTime):
    while True:
        try:
            print("(dht11) measuring...")
            # wait every time before reading the values to prevent reading-errors 
            time.sleep(1)
            dht11.measure() 
        except Exception as err:
            print("(dht11) Error occurred while measuring the tempreature and the humidity: ", err)
        temperature = dht11.temperature()
        humidity = dht11.humidity()
        
        print("(dht11) Temperature: {}°C".format(temperature))
        print("(dht11) Humidity: {}%".format(humidity))
        print("=====================================================")
        await uasyncio.sleep_ms(sleepTime)

async def readCapacitiveSoilValues(sleepTime):
    while True:
        # read moisture value and convert to percentage into the calibration range
        moisture = (wetMoisture-soil.read_u16())*100/(wetMoisture-dryMoisture)
        # print values
        print("(capacitive-soil-sensor) Moisture: " + "%.2f" % moisture +"% (adc: "+str(soil.read_u16())+")")
        print("=====================================================")
        await uasyncio.sleep_ms(sleepTime)


async def main():
    while True:
        uasyncio.create_task(readDHT11Values(0))
        uasyncio.create_task(readCapacitiveSoilValues(0))
        await uasyncio.sleep_ms(10_000)
    
uasyncio.run(main())


