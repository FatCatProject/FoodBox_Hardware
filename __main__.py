from foodbox.foodbox import FoodBox
from RPi.GPIO import GPIO


def main():
	box = FoodBox()
	try:
		box.start_mainloop()
	except Exception as e:
		raise e
	finally:
		GPIO.cleanup()

if __name__ == "__main__":
	main()
