"""
This is the "drinkomator" programm
you can use this for buy coffee or waterbutle
"""

import time
from time import sleep
import threading
import serial
import RPi.GPIO as GPIO
import stepmotor



#GPIO  vars ####################################
A =  7              #GPIO 4  pin a for stepmotor
B = 11              #GPIO 17 in 2 for stepmotor
C = 13              #GPIO 27 in 3 for stepmotor
D = 15              #GPIO 22 pin d for stepmotor
BUTTON_WATER = 31   #GPIO 6 for water button
LED_WATER    = 35   #GPIO 19 for water led
BUTTON_COFFE = 33   #GPIO 13 for coffe button
LED_COFFE    = 37   #GPIO 26 for coffe led
RELAY_COFFEE = 40   #GPIO 21 for 5v relay
ISCOIN       = 16   #GPIO 25 for coin inserter

#E = 16
#F = 18

#GPIO init settings ############################
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
stepmotor.GPIO_INIT(A, B, C, D)

GPIO.setup(BUTTON_WATER, GPIO.IN)
GPIO.setup(BUTTON_COFFE, GPIO.IN)
GPIO.setup(LED_COFFE, GPIO.OUT)
GPIO.setup(LED_WATER, GPIO.OUT)
GPIO.setup(RELAY_COFFEE, GPIO.OUT)
GPIO.output(LED_COFFE, GPIO.LOW)
GPIO.setup(ISCOIN, GPIO.IN)

# Programlogic vars ############################

### using internal gpio
start = 1
stop = 0
coffeLedState = False
waterLedState = False
lastState = 0
geld = 0

### coin counter interupt
coinValue = 0        
signalCostFactor = 1
update = 0
updateDebounceTime = 0
updateDebounceDelay = 500

##serial connection
connected = False
port='/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0' #select the serial port here
baud=115200 #baud is defined on arduino firmware

#MAINLOGIK #####################################
def RUN_WATER_OUT():
    print(".....bottle output run")
    print("Rückgeld: %d" % geld);
    stepmotor.RIGHT_TURN(360)
    GPIO.output(LED_WATER, GPIO.LOW)
    GPIO.output(LED_COFFE, GPIO.LOW)
    #GPIO.output(RELAY_COFFEE, GPIO.LOW)
    #time.sleep(10)

def RUN_COFFE_OUT():
    print("....coffe output run")
    print("Rückgeld: %d" % geld);
    GPIO.output(LED_WATER, GPIO.LOW)
    GPIO.output(LED_COFFE, GPIO.LOW)
    GPIO.output(RELAY_COFFEE, GPIO.HIGH)
    #time.sleep(60)
    GPIO.output(RELAY_COFFEE, GPIO.LOW)

def SERIAL_HANDLE(data):
    global geld;
    print("SERIAL INPUT: ")
    try:
        geld = geld + int(data)
        print("Balance: %d" % geld);
    except ValueError:
        print(data) #nothing to do is debug msg
        geld = 0 #reset mony
    
    
def READ_FROM_PORT(ser):
    global connected;
    #while not connected:
        #serin = ser.read()
        #connected = True
    while True:
        sleep(1)
        #reading = ser.readline().decode()
        getVal = ser.readline().decode().replace("\r", "")
        SERIAL_HANDLE(getVal)
    
#is not needed     
def ISCOIN_TRIGGER(cannel):
    global coinValue
    global geld
    global update
    global state
    global lastState
    global updateDebounceTime
    global updateDebounceDelay
    signalValue = GPIO.input(ISCOIN)
    print("coin signal is %d" % signalValue);
    #print(time.time())
    if signalValue:
        state = 1;
    else:
        state = 0;
        # Should we send a balance update
        if update == 0 :
          if ((time.time()- updateDebounceTime) > updateDebounceDelay):
            print("Coin Value: %d" % coinValue); # WARNING: The coin value will be wrong if coins are inserted within the updateDebounceDelay, adjust the delay and test
            if (coinValue==1) :
                geld = geld + 10
            if (coinValue==2) :
                geld = geld + 20
            if (coinValue==3) :
                geld = geld + 50
            if (coinValue==4) :
                geld = geld + 100
            ###
            ##if (coinValue==15) :
            #    geld = geld + 100
            #if (coinValue==18) :
            #    geld = geld + 200
            coinValue = 0; # Reset current coin value
            print("Balance: %d" % geld); # This should be the most accurate as we should get the same ammount of pulses even if multiple coins get inserted at once
            update = 1; # Make sure we don't run again, till next coin

    if (state != lastState):
        # Process new signal
        if (state == 1) :
          coinValue = coinValue + signalCostFactor; # Update coin value
          updateDebounceTime = time.time(); # Update last time we processed a signal
          update = 0; # Time to send a update now?
          lastState = state; # Update last state
       
    
#MAIN #########################

#stepmotor.DEMO_RUN()
print('Welcome to drinkmator')
try:
    serialCoin = serial.Serial(port, baud)
    thread = threading.Thread(target=READ_FROM_PORT, args=(serialCoin,))
    thread.start()
    #stepmotor.DEMO_RUN()
    #GPIO.add_event_detect(ISCOIN, GPIO.RISING, callback=ISCOIN_TRIGGER)#, bouncetime=updateDebounceDelay)
    while True: #main loop
        if(geld>=20):
            if (waterLedState==False):
                print("Water Bottle can out");
                waterLedState=True
                GPIO.output(LED_WATER, GPIO.HIGH)
            if (GPIO.input(BUTTON_WATER)==False):
                geld=geld-20
                RUN_WATER_OUT()
            if (geld >= 30):
                if (coffeLedState==False):
                    print("Coffe can out");
                    coffeLedState=True
                    GPIO.output(LED_COFFE, GPIO.HIGH)
                if (GPIO.input(BUTTON_COFFE)==False):
                    geld=geld-30
                    RUN_COFFE_OUT();
        time.sleep(.5)
except Exception as exc:
    GPIO.cleanup()
    print("FEHLER")
    print(exc)
except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    print("\nBye bye")
    
GPIO.cleanup()
"""

    taster = GPIO.input(BUTTON_COFFE)
    time.sleep(0.010) #entprellen
    if(taster == False):
        print("Button is pressed")
        RUN_DRINK_OUT()
        
"""
