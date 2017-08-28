import time
from Hardware import LM393
from Hardware import ULN2003
from Hardware import HX711
from Hardware import MFRC522
from Hardware import RFIDCard
from typing import Union, Tuple, List
from foodbox.system_settings import SystemSettings
from foodbox.system_log import SystemLog
from foodbox.feeding_log import FeedingLog
from foodbox.system_log import MessageTypes
import socket
import uuid
from DB.foodboxDB import FoodBoxDB


class FoodBox:
	__buzzer = None  # TODO - Add a buzzer
	__cn = None  # type: FoodBoxDB  # Database connection
	__proximity = None  # type: LM393  # LM393 proximity sensor
	__rfid_scanner = None  # type: MFRC522  # MFRC522 RFID reader
	__scale = None  # type: HX711  # HX711 + load cell
	__stepper = None  # type: ULN2003  # ULN2003 stepper controller

	# Settings section
	__brainbox_ip_address = None  # type: Union[str, None]  # IP address of BrainBox to communicate with
	__foodbox_id = None  # type: str  # Unique ID for this box
	__foodbox_name = None  # type: str  # Name of box, defaults to HOSTNAME
	__max_open_time = None  # type: int  # Max time to keep lid open before buzzer turns on
	__scale_offset = None  # type: Union[int, float]  # OFFSET for HX711
	__scale_scale = None  # type: int  # SCALE for HX711
	__sync_interval = None  # type: int  # Interval between pooling BrainBox
	__sync_last = None  # type: time.struct_time  # When was last successful communication with BrainBox
	__presentation_mode = False  # type: bool
	__sync_on_change = False  # type: bool  # Should sync with the BrainBox on every FeedingLog?
	__lid_open = False  # type: bool

	# End of settings section

	def __init__(self, presentation_mode: bool = False, sync_on_change: bool = False) -> None:
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
		self.__sync_on_change = sync_on_change

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

		cn = FoodBoxDB()  # type: FoodBoxDB
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
		cn = FoodBoxDB()  # type: FoodBoxDB
		cn.set_system_setting(setting=setting, value=value)
		del cn

		success = True
		return success

	def write_system_log(self, log: SystemLog) -> bool:
		"""Writes a system log to the database.

		:arg log: The system log to write.
		:type log: SystemLog
		:rtype: bool
		"""
		cn = FoodBoxDB()  # type: FoodBoxDB
		cn.add_system_log(myLog=log)
		del cn
		return False

	def write_feeding_log(self, log: FeedingLog) -> bool:
		"""Writes a feeding log to the database.

		:arg log: The feeding log to write.
		:type log: FeedingLog
		:rtype: bool
		"""
		cn = FoodBoxDB()  # type: FoodBoxDB
		cn.add_feeding_log(myLog=log)
		del cn
		return True

	def mark_feeding_logs_synced(self, uids: Tuple[str]) -> bool:
		"""Marks FeedingLogs as synced to brainbox.

		:arg uids: A Tuple[str] of IDs to mark
		:type uids: Tuple[str]
		:rtype: bool
		"""
		cn = FoodBoxDB()  # type: FoodBoxDB
		for uid in uids:
			cn.set_feeding_log_synced(uid)
		del cn
		return True

	def delete_synced_feeding_logs(self) -> bool:
		"""Delete FeedingLogs that were already synced to the brainbox.

		:rtype: bool
		"""
		cn = FoodBoxDB()  # type: FoodBoxDB
		cn.delete_synced_feeding_logs()
		del cn
		return False

	def sync_with_brainbox(self) -> Tuple[Tuple[str], bool]:
		"""Sync unsynced FeedingLogs with the brainbox.

		:return synced_uid: A Tuple[str] of uids that were synced, or failed to sync.
		:return success: Did it sync successfully or not.
		:rtype synced_uid: Tuple[str]
		:rtype success: bool
		"""

		cn = FoodBoxDB()  # type: FoodBoxDB
		uid_to_sync = cn.get_not_synced_feeding_logs()  # type: List[FeedingLog]
		del cn
		synced_uid = Tuple([log.get_id() for log in uid_to_sync])  # type: Tuple[str]

		if self.__brainbox_ip_address is None:
			self.__brainbox_ip_address = self.__scan_for_brainbox()
			if self.__brainbox_ip_address is not None:
				self.__set_system_setting(SystemSettings.BrainBox_IP, self.__brainbox_ip_address)
			else:
				return synced_uid, False

		success: bool = False
		# TODO - Sync with brainbox
		return synced_uid, success

	def start_mainloop(self) -> bool:
		"""The main loop of reading card, checking access and writing logs.

		:rtype: bool
		"""
		while True:
			if time.time() - time.mktime(self.__sync_last) >= self.__sync_interval:

				sync_uid, sync_success = self.sync_with_brainbox()
				if sync_success:
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

				if sync_success:
					if self.mark_feeding_logs_synced(uids=sync_uid):
						logstr = "FeedingLogs marked synced successfully."
						logtype = MessageTypes.Information
						logsev = 0
						deleted_logs = True
					else:
						logstr = "Failed to mark FeedingLogs synced."
						logtype = MessageTypes.Error
						logsev = 1
						deleted_logs = False
					syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(),
						severity=logsev)
					self.write_system_log(syslog)

					if deleted_logs:
						if self.delete_synced_feeding_logs():
							logstr = "FeedingLogs marked synced were deleted successfully."
							logtype = MessageTypes.Information
							logsev = 0
						else:
							logstr = "Failed to delete FeedingLogs marked as synced."
							logtype = MessageTypes.Error
							logsev = 1
						syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(),
							severity=logsev)
						self.write_system_log(syslog)

			carduid = self.__rfid_scanner.get_uid()
			if carduid is None:
				time.sleep(0.1)
				continue

			cn = FoodBoxDB()  # type: FoodBoxDB
			card = cn.get_card_byID()  # type: RFIDCard
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
			if self.__sync_on_change:
				sync_uid, sync_success = self.sync_with_brainbox()
				if sync_success:
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
