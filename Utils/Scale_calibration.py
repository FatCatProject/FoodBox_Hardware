import time
import sys

HWPATH = sys.path[0] + '/../'
sys.path.insert(0, HWPATH)
from Hardware.HX711.HX711 import HX711

scale = HX711()

v = input("Please clear the scale of any items and press Enter to continue.\n")
scale.tare()

flag = True
while flag:
	try:
		weight = input("Please put a weight on the scale and tell me the weight in grams: ")
		weight = int(weight)
	except ValueError:
		print("You were asked to enter a number, you entered {} .".format(weight))
		continue

	if weight < 100:
		print("Please put a weight that is >= 100 grams.")
		continue
	
	val = scale.get_value(150)
	scale_factor = int(val / weight)
	print("Please set scale factor to : {}".format(scale_factor))
	print("Bye.")
	flag = False

