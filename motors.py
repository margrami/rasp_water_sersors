import RPi.GPIO as GPIO
import io
import time

init = False
GPIO.setmode(GPIO.BCM) # use BCM numbering pin numbers


def init_output(pin):
    GPIO.setup(pin, GPIO.OUT) # set up channel as an output.
    GPIO.output(pin, GPIO.HIGH) # set the motor in 1 because it is inversed logic


def manual_pump(pump_pin:int, delay:int):
	init_output(pump_pin)
	GPIO.output(pump_pin, GPIO.LOW)
	time.sleep(1)
	GPIO.output(pump_pin, GPIO.HIGH)
	time.sleep(1)
	print(i)


for i in range(5):
	manual_pump(17, 1)



#GPIO.cleanup()

