import time
import Hardware
from typing import Union, Tuple
import foodbox.system_settings
import foodbox.system_log
import foodbox.feeding_log


class FoodBox:
	__buzzer = None  # TODO - Add a buzzer
	__cn = None  # TODO - Add DB connection (Waiting for DAL class to be written)
	__proximity: Hardware.LM393 = None  # LM393 proximity sensor
	__rfid_scanner: Hardware.MFRC522 = None  # MFRC522 RFID reader
	__scale: Hardware.HX711 = None  # HX711 + load cell
	__stepper: Hardware.ULN2003 = None  # ULN2003 stepper controller

	# Settings section
	__brainbox_ip_address: Union[str, None] = None  # IP address of BrainBox to communicate with
	__foodbox_id: str = None  # Unique ID for this box
	__foodbox_name: str = None  # Name of box, defaults to HOSTNAME
	__max_open_time: int = None  # Max time to keep lid open before buzzer turns on
	__scale_offset: Union[int, float] = None  # OFFSET for HX711
	__scale_scale: int = None  # SCALE for HX711
	__sync_interval: int = None  # Interval between pooling BrainBox
	__sync_last: time.struct_time = None  # When was last successful communication with BrainBox

	# End of settings section

	def __init__(self):
		self.__buzzer = None  # TODO
		self.__cn = None  # TODO
		self.__proximity = Hardware.LM393(pin_num=17)
		self.__rfid_scanner = Hardware.MFRC522(dev='/dev/spidev0.0', spd=1000000, SDA=8, SCK=11, MOSI=10, MISO=9,
				RST=25)
		self.__scale = Hardware.HX711(dout=4, pd_sck=18, gain=128, readBits=24, offset=-96096, scale=925)
		self.__stepper = Hardware.ULN2003(pin_a_1=27, pin_a_2=22, pin_b_1=23, pin_b_2=24, delay=0.025,
				presentation_mode=False)

	def __del__(self):
		del self.__buzzer
		del self.__cn
		del self.__proximity
		del self.__rfid_scanner
		del self.__scale
		del self.__stepper

	def __scan_for_brainbox(self) -> Union[str, None]:
		"""Scans the network for a BrainBox.

		:return bb_ip: The IP of the BrainBox server or None if not found.
		:rtype bb_ip: String, None
		"""
		# TODO
		bb_ip = None
		return bb_ip

	def __get_system_setting(self, setting: foodbox.system_settings) -> Tuple[Union[str, int, float, None], bool]:
		"""Get the value for a specific system setting.

		:arg setting: The system setting we want.
		:type setting: SystemSettings
		:return value: The unique ID for this FoodBox, or None if doesn't exist or wasn't set yet.
		:return from_db: Was the setting read from the database or from a file.
		:rtype value: String
		:rtype from_db: Boolean
		"""
		# TODO
		value = None
		from_db = False
		return value, from_db

	def __set_system_setting(self, setting: foodbox.system_settings, value: Union[str, int, float, None]) -> bool:
		"""Set the value for a specific system setting.

		:arg setting: The system setting to set.
		:arg value: The value for the setting.
		:type setting: SystemSettings
		:type value: String
		:return success: Was the setting set successfully or not.
		:rtype success: Boolean
		"""
		# TODO
		success = False
		return success

	# def write_system_log(self):
	# def write_feeding_log(self):
