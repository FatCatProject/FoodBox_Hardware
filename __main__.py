from foodbox.foodbox import FoodBox
from RPi.GPIO import GPIO


def main():
	box = FoodBox()
	try:
		box.start_mainloop()
	except KeyboardInterrupt:
		print("\nProgram interrupted by user.\n")
	except Exception:
		raise
	finally:
		del box
		GPIO.cleanup()
		print("Clean up and exit.")

if __name__ == "__main__":
	main()
