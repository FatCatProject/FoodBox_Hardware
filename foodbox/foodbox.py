import time
from Hardware import LM393
from Hardware import ULN2003
from Hardware import HX711
from Hardware import MFRC522
from Hardware import RFIDCard
from typing import Union, Tuple
from foodbox.system_settings import SystemSettings
from foodbox.system_log import SystemLog
from foodbox.feeding_log import FeedingLog
from foodbox.system_log import MessageTypes
import socket
import uuid
from DB.foodboxDB import FoodBoxDB


class FoodBox:
	__buzzer = None  # TODO - Add a buzzer
	__cn: FoodBoxDB = None  # Database connection
	__proximity: LM393 = None  # LM393 proximity sensor
	__rfid_scanner: MFRC522 = None  # MFRC522 RFID reader
	__scale: HX711 = None  # HX711 + load cell
	__stepper: ULN2003 = None  # ULN2003 stepper controller

	# Settings section
	__brainbox_ip_address: Union[str, None] = None  # IP address of BrainBox to communicate with
	__foodbox_id: str = None  # Unique ID for this box
	__foodbox_name: str = None  # Name of box, defaults to HOSTNAME
	__max_open_time: int = None  # Max time to keep lid open before buzzer turns on
	__scale_offset: Union[int, float] = None  # OFFSET for HX711
	__scale_scale: int = None  # SCALE for HX711
	__sync_interval: int = None  # Interval between pooling BrainBox
	__sync_last: time.struct_time = None  # When was last successful communication with BrainBox
	__presentation_mode: bool = False
	__lid_open = False
	# End of settings section

	def __init__(self, presentation_mode: bool = False) -> None:
		self.__scale_offset = self.__get_system_setting(SystemSettings.Scale_Offset) or -96096
		self.__scale = self.__get_system_setting(SystemSettings.Scale_Scale) or 925
		self.__foodbox_id = self.__get_system_setting(SystemSettings.FoodBox_ID)
		if self.__foodbox_id is None:
			self.__foodbox_id = uuid.uuid4().hex
			self.__set_system_setting(SystemSettings.FoodBox_ID, self.__foodbox_id)
		self.__foodbox_name = self.__get_system_setting(SystemSettings.FoodBox_Name) or socket.gethostname()
		self.__max_open_time = self.__get_system_setting(SystemSettings.Max_Open_Time) or 600
		self.__sync_interval = self.__get_system_setting(SystemSettings.Sync_Interval) or 600
		self.__brainbox_ip_address = self.__get_system_setting(SystemSettings.BrainBox_IP)
		if self.__brainbox_ip_address is None:
			self.__brainbox_ip_address = self.__scan_for_brainbox()
			if self.__brainbox_ip_address is not None:
				self.__set_system_setting(SystemSettings.BrainBox_IP, self.__brainbox_ip_address)
		self.__sync_last = time.localtime()
		self.__presentation_mode = presentation_mode

		self.__buzzer = None  # TODO
		self.__cn = None  # TODO - Do we need this?
		self.__proximity = LM393(pin_num=17)
		self.__rfid_scanner = MFRC522(dev='/dev/spidev0.0', spd=1000000, SDA=8, SCK=11, MOSI=10, MISO=9, RST=25)
		self.__scale = HX711(dout=4, pd_sck=18, gain=128, readBits=24, offset=self.__scale_offset,
				scale=self.__scale_scale)
		self.__stepper = ULN2003(pin_a_1=27, pin_a_2=22, pin_b_1=23, pin_b_2=24, delay=0.025,
				presentation_mode=presentation_mode)
		self.__scale.tare()
		if not self.__presentation_mode:
			self.__stepper.quarter_rotation_forward()
			self.__stepper.quarter_rotation_backward()

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

	def __get_system_setting(self, setting: SystemSettings) -> Tuple[Union[str, int, float, None], bool]:
		"""Get the value for a specific system setting.

		:arg setting: The system setting we want.
		:type setting: SystemSettings
		:return value: The unique ID for this FoodBox, or None if doesn't exist or wasn't set yet.
		:return from_db: Was the setting read from the database or from a file.
		:rtype value: String
		:rtype from_db: Boolean
		"""

		cn: FoodBoxDB = FoodBoxDB()
		value = cn.get_system_setting(setting=setting)
		from_db = value is not None
		del cn

		return value, from_db

	def __set_system_setting(self, setting: SystemSettings, value: Union[str, int, float, None]) -> bool:
		"""Set the value for a specific system setting.

		:arg setting: The system setting to set.
		:arg value: The value for the setting.
		:type setting: SystemSettings
		:type value: String
		:return success: Was the setting set successfully or not.
		:rtype success: Boolean
		"""
		cn: FoodBoxDB = FoodBoxDB()
		cn.set_system_setting(setting=setting, value=value)
		del cn

		success = True
		return success

	def write_system_log(self, log: SystemLog) -> bool:
		# TODO
		return False

	def write_feeding_log(self, log: FeedingLog) -> bool:
		cn: FoodBoxDB = FoodBoxDB()
		cn.add_feeding_log(myLog=log)
		del cn
		return True

	def mark_feeding_logs_synced(self, uids: Tuple[str]) -> bool:
		cn: FoodBoxDB = FoodBoxDB()
		for uid in uids:
			cn.set_feeding_log_synced(uid)
		del cn
		return True

	def delete_synced_feeding_logs(self) -> bool:
		cn: FoodBoxDB = FoodBoxDB()
		cn.delete_synced_feeding_logs()
		del cn
		return False

	def sync_with_brainbox(self) -> bool:
		if self.__brainbox_ip_address is None:
			self.__brainbox_ip_address = self.__scan_for_brainbox()
			if self.__brainbox_ip_address is not None:
				self.__set_system_setting(SystemSettings.BrainBox_IP, self.__brainbox_ip_address)
			else:
				return False

		# TODO
		return False

	def start_mainloop(self) -> bool:
		while True:
			if time.time() - time.mktime(self.__sync_last) >= self.__sync_interval:
				if self.sync_with_brainbox():
					logstr = "Sync with brainbox succeeded."
					logtype = MessageTypes.Information
					logsev = 0
				else:
					logstr = "Sync with brainbox failed."
					logtype = MessageTypes.Error
					logsev = 1
				syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
				self.write_system_log(syslog)
				self.__sync_last = time.localtime()

			carduid = self.__rfid_scanner.get_uid()
			if carduid is None:  # TODO - Check what carduid looks like
				time.sleep(0.1)
				continue

			cn: FoodBoxDB = FoodBoxDB()
			card: RFIDCard = cn.get_card_byID()  # or None
			del cn
			if card is None or not card.get_active():
				logstr = "Invalid card tried to open box."
				logtype = MessageTypes.Information
				logsev = 1
				syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev,
						card=carduid)
				self.write_system_log(syslog)
				old_carduid = carduid
				while self.__rfid_scanner.get_uid() == old_carduid:
					time.sleep(0.1)
				continue

			logstr = "Opened lid for card."
			if card.get_name() == "ADMIN":
				logstr = "ADMIN card opened the box."
			logtype = MessageTypes.Information
			logsev = 0
			syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev,
					card=carduid)
			self.write_system_log(syslog)
			open_time = time.localtime()
			start_weight = self.__scale.get_units()
			self.open_lid()
			time.sleep(5)
			if card.get_name() == "ADMIN":
				while self.__rfid_scanner.get_uid() == carduid:
					time.sleep(5)
			while self.__proximity.is_blocked():
				time.sleep(0.1)
				if time.time() - time.mktime(open_time) >= self.__max_open_time:
					logstr = "Lid was opened for too long."
					logtype = MessageTypes.Information
					logsev = 0
					syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(),
							severity=logsev, card=carduid)
					self.write_system_log(syslog)
				# TODO - Beep at the cat

			self.close_lid()
			close_time = time.localtime()
			end_weight = self.__scale.get_units()
			feedinglog = FeedingLog(card=card, open_time=open_time, close_time=close_time, start_weight=start_weight,
					end_weight=end_weight)
			self.write_feeding_log(feedinglog)

			if False:  # Ignore me.
				break
		return False

	def open_lid(self) -> bool:
		if self.__lid_open:
			return True
		self.__stepper.quarter_rotation_forward()
		self.__lid_open = True
		return True

	def close_lid(self):
		if not self.__lid_open:
			return True
		self.__stepper.quarter_rotation_backward()
		self.__lid_open = False
		return True
