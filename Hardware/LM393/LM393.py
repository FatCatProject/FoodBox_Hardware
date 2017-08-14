import RPi.GPIO as GPIO
import time

# while True:
# 	print(1-(GPIO.input(17))) <-- by default 0=sensor blocked , 1 sensor opened


class LM393:
	__pin_num = None

	def __init__(self, pin_num=17):
		self.__pin_num = pin_num
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.__pin_num, GPIO.IN)

	def __del__(self):
		pass

	def is_blocked(self):
		if (1 - GPIO.input(self.__pin_num)) == 0:
			return False
		else:
			return True

#prox=Proximity()
#print(prox.is_blocked())



