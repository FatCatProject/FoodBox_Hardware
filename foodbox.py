import time
import Hardware


class FoodBox:
	__buzzer = None 					# TODO - Add a buzzer
	__cn = None 						# TODO - Add DB connection (Waiting for DAL class to be written)
	__proximity = None 					# LM393 proximity sensor
	__rfid_scanner = None 				# MFRC522 RFID reader
	__scale = None						# HX711 + load cell
	__stepper = None 					# ULN2003 stepper controller

	# Settings section
	__brainbox_ip_address = None		# IP address of BrainBox to communicate with
	__foodbox_id = None					# Unique ID for this box
	__foodbox_name = None				# Name of box, defaults to HOSTNAME
	__max_open_time = None				# Max time to keep lid open before buzzer turns on
	__scale_offset = None				# OFFSET for HX711
	__scale_scale = None				# SCALE for HX711
	__sync_interval = None				# Interval between pooling BrainBox
	__sync_last = None					# When was last successful communication with BrainBox
	# End of settings section

	def __init__(self):

		self.__buzzer = None			# TODO
		self.__cn = None				# TODO
		# self.__proximity = Hardware.LM393(pin_num=17)
		# self.__rfid_scanner = Hardware.MFRC522(dev='/dev/spidev0.0', spd=1000000, SDA=8, SCK=11, MOSI=10, MISO=9, RST=25)
		# self.__scale = Hardware.HX711(dout=4, pd_sck=18, gain=128, readBits=24, offset=-96096, scale=925)
		# self.__stepper = Hardware.ULN2003(pin_a_1=27, pin_a_2=22, pin_b_1=23, pin_b_2=24, delay=0.025)
		pass

	def __del__(self):
		pass
