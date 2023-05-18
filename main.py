import dht
from machine import Pin, ADC
import time
import uasyncio
import uos
import network
import json
import gc

# garbage collector enabled
gc.enable()

# define
configFile = 'config.json'
calibrationFile = 'capacitive-soil-sensor-calibration.csv'
dryMoisture = 0
wetMoisture = 65535
wlan = network.WLAN(network.STA_IF)

# define wlan settings
ssid = ""
psk = ""
server = ""
port = 0


print("Initializing the (dht11) sensor...")
dht11 = dht.DHT11(Pin(4))

print("Initializing the (capacitive-soil-sensor)...")
soil = ADC(Pin(26))


print("(capacitive-soil-sensor) Calibrating min/max values...")

def readConfigJson():
    global ssid,psk,server,port
    try:
        with open(configFile) as config:
            data = json.load(config)
            print(data)
    
        # dumps the json object into an element
        json_str = json.dumps(data)

        # load the json to a string
        config = json.loads(json_str)

        # init wlan-connection
        ssid = config['ssid']
        psk = config['psk']
        server = config['server']
        port = config['port']
        
        
    except Exception as err:
        print("config.json is missing ",err)

def checkIfFileExits(file):
    try:
        stat = uos.stat(file)
        print("File '{}' exists.".format(file))
        print("File size: {} bytes".format(stat[6]))
        return True
    except OSError as e:
        if e.args[0] == 2:  
            print("File '{}' does not exist.".format(file))
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
    secs = 30
    vals = []
    while count <= secs:
        vals.append(soil.read_u16())
        print(str(secs - count) + "sec remaining...");
        count = count + 1
        time.sleep(1)
    return vals


def writeCalibrationValues(dry, wet):
    # Open the CSV file for writing
    with open(calibrationFile, 'w') as file:
        # Write the dry and wet moisture values to the file
        file.write("{},{}".format(dry, wet))

    print("capacitive-soil-sensor-calibration '{}' has been written successfully.".format(calibrationFile))


def wlanConnection(ssid, psk):
    print("-----------------------------------------------------")
    print("Validating config.json...")
    wlan.active(True)
    if psk != "" or ssid !="":
        print(ssid + ": " + psk)
        wlan.connect(ssid, psk)
        print(wlan.isconnected())
    else:
        print("Invalid config.json")
    print("-----------------------------------------------------")



if checkIfFileExits(configFile) is True:
    print("=====================================================")
    
    # init wlan-vars
    readConfigJson()
    
    
    wlanConnection(ssid,psk) 
    while wlan.isconnected() == False:
        print("Trying to connect to: " + ssid + "...")
        wlanConnection(ssid, psk)
        time.sleep(3)
    print("Successfully connected to (" + ssid + ")!")
    
    print("=====================================================")


# calibrating the capacitive soil-sensor
if checkIfFileExits(calibrationFile) is True:
    print("=====================================================")
    print("No calibration neccessary. Reading calibrated values...")
    dry_moisture = 0
    wet_moisture = 0

    with open(calibrationFile, 'r') as file:
        lines = file.readlines()

        for line in lines:
            columns = line.strip().split(',')

            if len(columns) == 2:
                dry_moisture = int(columns[1])
                wet_moisture = int(columns[0])
                break  

    print("Dry Moisture Level:", dry_moisture)
    print("Wet Moisture Level:", wet_moisture)
    print("=====================================================")
    dryMoisture = dry_moisture
    wetMoisture = wet_moisture
    
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
    
    # dryMoisture wetMoisture
    writeCalibrationValues(dryMoisture, wetMoisture)
    
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

