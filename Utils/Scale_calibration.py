from math import sqrt
import sys

HWPATH = sys.path[0] + '/../'
sys.path.insert(0, HWPATH)
from Hardware.HX711.HX711 import HX711

scale = HX711()

v = input("Please clear the scale of any items and press Enter to continue.\n")
scale.tare_2()

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

	units_array = []
	avg = 0
	for i in range(50):
		tmp_units = scale.get_value()
		units_array.append(tmp_units)
		avg += tmp_units
	avg = (avg / len(units_array))

	flag_2 = True
	while flag_2:
		d = 0
		for n in units_array:
			d += sqrt((n - avg) ** 2)
		d = sqrt((d / len(units_array)))
		drop_avg = [
			n for n in units_array
			if sqrt((n - avg) ** 2) <= d
		]

		if len(drop_avg) > 0:
			flag_2 = False
			continue
		assert len(units_array) > 0, "len(units_array) == 0, Bad."
		min = units_array[0]
		max = min
		for n in units_array:
			if n < min:
				min = n
			if n > max:
				max = n
		if sqrt((min - avg) ** 2) > sqrt((max - avg) ** 2):
			avg = ((avg * len(units_array)) - min) / (len(units_array) - 1)
			units_array.remove(min)
		else:
			avg = ((avg * len(units_array)) - max) / (len(units_array) - 1)
			units_array.remove(max)
	val = 0
	for n in drop_avg:
		val += n
	val = val / len(drop_avg)

	scale_factor = int(val / weight)
	print("Please set scale factor to : {}".format(scale_factor))
	print("Bye.")
	flag = False

