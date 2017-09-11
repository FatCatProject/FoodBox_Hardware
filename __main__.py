from foodbox.foodbox import FoodBox
import RPi.GPIO as GPIO
from DB.foodboxDB import FoodBoxDB
from foodbox.system_log import SystemLog
from foodbox.feeding_log import FeedingLog
import time


def main():
	startup_time = time.gmtime()  # type: startup_time
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

	print("Printing new logs for debugging purposes:")
	cn = FoodBoxDB()
	new_logs = cn.get_all_system_logs(startup_time)  # type: tuple
	i = 1
	print("SystemLogs:")
	for log in new_logs:
		print("{:04} : ".format(i), end="")
		print(log)
		i += 1

	new_logs = cn.get_all_feeding_logs()  # type: tuple
	i = 1
	print("FeedingLogs:")
	for log in new_logs:
		print("{:04} : ".format(i), end="")
		print(log)
		i += 1

if __name__ == "__main__":
	main()
