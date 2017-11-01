from DB.foodboxDB import FoodBoxDB
from Hardware import HX711
from Hardware import LM393
from Hardware import MFRC522
from Hardware import RFIDCard
from Hardware import ULN2003
from foodbox.feeding_log import FeedingLog
from foodbox.system_log import MessageTypes
from foodbox.system_log import SystemLog
from foodbox.system_settings import SystemSettings
from zeroconf import ServiceBrowser
from zeroconf import ServiceStateChange
from zeroconf import Zeroconf
from zeroconf import ZeroconfServiceTypes
import datetime
import json
import pytz
import requests
import socket
import time
import uuid


class FoodBox:
	__buzzer = None  # TODO - Add a buzzer
	__proximity = None  # type: LM393  # LM393 proximity sensor
	__rfid_scanner = None  # type: MFRC522  # MFRC522 RFID reader
	__scale = None  # type: HX711  # HX711 + load cell
	__stepper = None  # type: ULN2003  # ULN2003 stepper controller
	__browser = None  # Zeroconf ServiceBrowser

	# Settings section
	__brainbox_ip_address = None  # type: bytes  # IP address of BrainBox to communicate with
	__brainbox_port_number = None  # type: int  # TCP port number
	__foodbox_id = None  # type: str  # Unique ID for this box
	__foodbox_name = None  # type: str  # Name of box, defaults to HOSTNAME
	__max_open_time = None  # type: int  # Max time to keep lid open before buzzer turns on
	__scale_offset = None  # type: int  # OFFSET for HX711
	__scale_scale = None  # type: int  # SCALE for HX711
	__sync_interval = None  # type: int  # Interval between pooling BrainBox
	__sync_last = None  # type: time.struct_time  # When was last successful communication with BrainBox
	__presentation_mode = False  # type: bool
	__sync_on_change = False  # type: bool  # Should sync with the BrainBox on every FeedingLog?
	__lid_open = False  # type: bool
	__last_weight = None  # type: float
	__last_purge = None  # type: float  # When were the logs last purged
	__said_hi_to_brainbox = False  # type: bool

	# End of settings section

	def __init__(self, presentation_mode: bool = False, sync_on_change: bool = True):
		self.__last_weight = float(self.__get_system_setting(SystemSettings.Last_Weight) or 0)
		if self.__last_weight < 0:
			self.__last_weight = 0
		self.__scale_offset = int(self.__get_system_setting(SystemSettings.Scale_Offset) or -96096)
		self.__scale_scale = int(self.__get_system_setting(SystemSettings.Scale_Scale) or 925)
		self.__foodbox_id = self.__get_system_setting(SystemSettings.FoodBox_ID)
		if self.__foodbox_id is None:
			self.__foodbox_id = uuid.uuid4().hex
			self.__set_system_setting(SystemSettings.FoodBox_ID, self.__foodbox_id)
		self.__foodbox_name = self.__get_system_setting(SystemSettings.FoodBox_Name) or socket.gethostname()
		self.__max_open_time = int(self.__get_system_setting(SystemSettings.Max_Open_Time) or 600)
		self.__sync_interval = int(self.__get_system_setting(SystemSettings.Sync_Interval) or 60)
		self.__sync_last = time.localtime(0)
		self.__presentation_mode = presentation_mode
		self.__last_purge = self.__get_system_setting(SystemSettings.Last_Purge)
		if self.__last_purge is None:
			self.purge_logs()
		elif type(self.__last_purge) is str:
			self.__last_purge = float(self.__last_purge)

		self.__buzzer = None  # TODO
		self.__proximity = LM393(pin_num=17)
		self.__rfid_scanner = MFRC522(dev='/dev/spidev0.0', spd=1000000, SDA=8, SCK=11, MOSI=10, MISO=9, RST=25)
		self.__scale = HX711(
			dout=4, pd_sck=18, gain=128, readBits=24, offset=self.__scale_offset, scale=self.__scale_scale)
		self.__stepper = ULN2003(
			pin_a_1=27, pin_a_2=22, pin_b_1=23, pin_b_2=24, delay=0.025, presentation_mode=presentation_mode)
		self.__scale.tare()
		self.__scale.set_offset(self.__scale_offset + self.__last_weight)
		self.__set_system_setting(SystemSettings.Last_Weight, self.__scale.get_units())

		self.start_network_discovery()
		self.__sync_on_change = sync_on_change
		print("Ready")
		print("Weight on Ready is: ", self.__scale.get_units())

	def __del__(self):
		if self.__browser is not None:
			self.stop_network_discovery()
			del self.__browser
		if self.__buzzer is not None:
			del self.__buzzer
		if self.__proximity is not None:
			del self.__proximity
		if self.__rfid_scanner is not None:
			del self.__rfid_scanner
		if self.__scale is not None:
			del self.__scale
		if self.__stepper is not None:
			del self.__stepper

	def __get_system_setting(self, setting: SystemSettings):
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
		del cn
		return value

	def __set_system_setting(self, setting: SystemSettings, value):
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

	def write_system_log(self, log: SystemLog):
		"""Writes a system log to the database.

		:arg log: The system log to write.
		:type log: SystemLog
		:rtype: bool
		"""
		cn = FoodBoxDB()  # type: FoodBoxDB
		cn.add_system_log(myLog=log)
		del cn
		return False

	def write_feeding_log(self, log: FeedingLog):
		"""Writes a feeding log to the database.

		:arg log: The feeding log to write.
		:type log: FeedingLog
		:rtype: bool
		"""
		cn = FoodBoxDB()  # type: FoodBoxDB
		cn.add_feeding_log(myLog=log)
		del cn
		return True

	def mark_feeding_logs_synced(self, uids: tuple):
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

	def delete_synced_feeding_logs(self):
		"""Delete FeedingLogs that were already synced to the brainbox.

		:rtype: bool
		"""
		cn = FoodBoxDB()  # type: FoodBoxDB
		cn.delete_synced_feeding_logs()
		del cn
		return False

	def sync_with_brainbox(self):
		"""Sync unsynced FeedingLogs with the brainbox.

		:return synced_uid: A Tuple[str] of uids that were synced, or failed to sync.
		:return success: Did it sync successfully or not.
		:rtype sync_uid: Tuple[str]
		:rtype success: bool
		"""

		cn = FoodBoxDB()  # type: FoodBoxDB
		logs_to_sync = cn.get_not_synced_feeding_logs()  # type: list[FeedingLog]
		del cn
		sync_uid = tuple([log.get_id() for log in logs_to_sync])  # type: tuple[str]
		# success = False  # type: bool

		if not logs_to_sync:
			success = True
			logstr = "Sync with BrainBox succeeded - Nothing to sync."
			logtype = MessageTypes.Information
			logsev = 0
			syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
			print("syslog: {}".format(syslog))  # Debug message
			self.write_system_log(syslog)
			self.__sync_last = time.localtime()
			return sync_uid, success

		if self.__brainbox_ip_address is None or self.__brainbox_port_number is None:
			success = False
			logstr = "Sync with BrainBox failed - BrainBox not recognized."
			logtype = MessageTypes.Error
			logsev = 1
			syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
			print("syslog: {}".format(syslog))  # Debug message
			self.write_system_log(syslog)
			self.__sync_last = time.localtime()
			return sync_uid, success

		logs_list = []
		for log in logs_to_sync:
			tmp_open_time = log.get_open_time()  # type: time.struct_time
			tmp_open_datetime = datetime.datetime.fromtimestamp(
				tmp_open_time).astimezone(pytz.timezone("Asia/Jerusalem"))
			tmp_close_time = log.get_close_time()  # type: time.struct_time
			tmp_close_datetime = datetime.datetime.fromtimestamp(
				tmp_close_time).astimezone(pytz.timezone("Asia/Jerusalem"))
			tmp_log_dict = {
				"feeding_id": log.get_id(), "card_id": log.get_card().get_uid(),
				"open_time": str(tmp_open_datetime), "close_time": str(tmp_close_datetime),
				"start_weight": log.get_start_weight(), "end_weight": log.get_end_weight()
			}
			logs_list.append(tmp_log_dict)

		payload = {"box_id": self.__foodbox_id, "feeding_logs": logs_list}
		url = "http://{0}:{1}/bbox/pushlogs/".format(
			socket.inet_ntoa(self.__brainbox_ip_address), self.__brainbox_port_number
		)
		print("url: {}".format(url))  # Debug message
		print("payload: {}\n\n".format(payload))  # Debug message

		try:
			brainbox_response = requests.post(url=url, json=payload, headers={"connection": "close"})

			if brainbox_response.status_code != 200:
				success = False
				logstr = "Sync with brainbox failed - status_code = {}.".format(brainbox_response.status_code)
				logtype = MessageTypes.Error
				logsev = 1
				syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
				print("syslog: {}".format(syslog))  # Debug message
				self.write_system_log(syslog)
				self.__sync_last = time.localtime()
				if "brainbox_response" in vars():
					brainbox_response.close()
				return sync_uid, success

			response_obj = json.loads(brainbox_response.text)
			confirmed_ids = tuple(response_obj["confirm_ids"])  # TODO - Compare against sync_uid
			print("confirmed ids: {}\n\n".format(confirmed_ids))  # Debug message
			if "brainbox_response" in vars():
				brainbox_response.close()
			self.mark_feeding_logs_synced(confirmed_ids)
		except (
			ValueError, AttributeError, requests.exceptions.RequestException,
			Exception
		) as e:
			success = False
			logstr = "Sync with brainbox failed - exception = {}.".format(
				str(e.args)
			)
			logtype = MessageTypes.Error
			logsev = 2
			syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
			print("syslog: {}".format(syslog))  # Debug message
			self.write_system_log(syslog)
			self.__sync_last = time.localtime()
			if "brainbox_response" in vars():
				brainbox_response.close()
			return sync_uid, success

		success = True
		logstr = "Sync with brainbox succeeded."
		logtype = MessageTypes.Information
		logsev = 0
		syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
		print("syslog: {}".format(syslog))  # Debug message
		self.write_system_log(syslog)
		self.__sync_last = time.localtime()

		if "brainbox_response" in vars():
			brainbox_response.close()
		return sync_uid, success

	def sync_cards_from_brainbox(self):
		"""Pull new cards from brainbox.

		:return synced_cards: A Tuple[str] of card_ids that were received from the server.
		:return success: Did it sync successfully or not.
		:rtype synced_cards: Tuple[str]
		:rtype success: bool
		"""

		synced_cards = []

		if self.__brainbox_ip_address is None or self.__brainbox_port_number is None:
			success = False
			logstr = "Sync cards with BrainBox failed - BrainBox not recognized."
			logtype = MessageTypes.Error
			logsev = 1
			syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
			print("syslog: {}".format(syslog))  # Debug message
			self.write_system_log(syslog)
			self.__sync_last = time.localtime()
			return tuple(synced_cards), success

		url = "http://{0}:{1}/bbox/pullcards/{2}".format(
			socket.inet_ntoa(self.__brainbox_ip_address), self.__brainbox_port_number, self.__foodbox_id
		)

		try:
			brainbox_response = requests.get(url=url, headers={"connection": "close"})

			if brainbox_response.status_code != 200:
				success = False
				logstr = "Sync cards with brainbox failed - status_code = {}.".format(brainbox_response.status_code)
				logtype = MessageTypes.Error
				logsev = 1
				syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
				print("syslog: {}".format(syslog))  # Debug message
				self.write_system_log(syslog)
				self.__sync_last = time.localtime()
				if "brainbox_response" in vars():
					brainbox_response.close()
				return tuple(synced_cards), success

			response_obj = json.loads(brainbox_response.text)
			admin_cards = tuple(response_obj["admin_cards"])
			modified_cards = tuple(response_obj["modified_cards"])
			new_cards = tuple(response_obj["new_cards"])
			print("admin cards: {}\n\n".format(admin_cards))  # Debug message
			print("modified cards: {}\n\n".format(modified_cards))  # Debug message
			print("new cards: {}\n\n".format(new_cards))  # Debug message

			cn = FoodBoxDB()  # type: FoodBoxDB
			for admin_card in admin_cards:
				tmp_id = admin_card["card_id"]
				tmp_active = admin_card["active"]
				cn.set_state(cardID=tmp_id, newState=tmp_active)
				cn.set_card_name(cardID=tmp_id, new_name="ADMIN")
				synced_cards.append(tmp_id)
			for modified_card in modified_cards:
				tmp_id = modified_card["card_id"]
				tmp_active = modified_card["active"]
				tmp_name = modified_card["card_name"]
				cn.set_state(cardID=tmp_id, newState=tmp_active)
				cn.set_card_name(cardID=tmp_id, new_name=tmp_name)
				synced_cards.append(tmp_id)
			for new_card in new_cards:
				tmp_id = new_card["card_id"]
				tmp_active = new_card["active"]
				tmp_name = new_card["card_name"]
				cn.set_state(cardID=tmp_id, newState=tmp_active)
				cn.set_card_name(cardID=tmp_id, new_name=tmp_name)
				synced_cards.append(tmp_id)

			del cn
			success = True
			if "brainbox_response" in vars():
				brainbox_response.close()
		except (
			ValueError, AttributeError, requests.exceptions.RequestException,
			Exception
		) as e:
			success = False
			logstr = "Sync cards with brainbox failed - exception = {}.".format(
				str(e.args)
			)
			logtype = MessageTypes.Error
			logsev = 2
			syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
			print("syslog: {}".format(syslog))  # Debug message
			self.write_system_log(syslog)
			self.__sync_last = time.localtime()
			if "brainbox_response" in vars():
				brainbox_response.close()
			return tuple(synced_cards), success

		logstr = "Sync cards with brainbox succeeded."
		logtype = MessageTypes.Information
		logsev = 0
		syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
		print("syslog: {}".format(syslog))  # Debug message
		self.write_system_log(syslog)
		self.__sync_last = time.localtime()

		if "brainbox_response" in vars():
			brainbox_response.close()
		return tuple(synced_cards), success

	def sync_foodbox_with_brainbox(self):
		if self.__brainbox_ip_address is None or self.__brainbox_port_number is None:
			return False

		url = "http://{0}:{1}/bbox/pullfoodbox/{2}".format(
			socket.inet_ntoa(self.__brainbox_ip_address), self.__brainbox_port_number, self.__foodbox_id
		)
		print("url: {}".format(url))  # Debug message
		payload = {"current_weight": self.__last_weight}
		print("payload: {}\n\n".format(payload))  # Debug message

		try:
			brainbox_response = requests.get(url=url, params=payload, headers={"connection": "close"})

			if brainbox_response.status_code != 200:
				success = False
				logstr = "Sync FoodBox with brainbox failed - status_code = {}.".format(brainbox_response.status_code)
				logtype = MessageTypes.Error
				logsev = 1
				syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
				print("syslog: {}".format(syslog))  # Debug message
				self.write_system_log(syslog)
				self.__sync_last = time.localtime()
				if "brainbox_response" in vars():
					brainbox_response.close()
				return success

			response_obj = json.loads(brainbox_response.text)
			response_box_name = response_obj["foodbox_name"]
			print("response_box_name: {}\n\n".format(response_box_name))  # Debug message
			if "brainbox_response" in vars():
				brainbox_response.close()
		except (
			ValueError, AttributeError, requests.exceptions.RequestException,
			Exception
		) as e:
			success = False
			logstr = "Sync FoodBox with brainbox failed - exception = {}.".format(
				str(e.args)
			)
			logtype = MessageTypes.Error
			logsev = 2
			syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
			print("syslog: {}".format(syslog))  # Debug message
			self.write_system_log(syslog)
			self.__sync_last = time.localtime()
			if "brainbox_response" in vars():
				brainbox_response.close()
			return success

		self.__foodbox_name = response_box_name
		self.__set_system_setting(SystemSettings.FoodBox_Name, self.__foodbox_name)

		success = True
		logstr = "Sync FoodBox with brainbox succeeded."
		logtype = MessageTypes.Information
		logsev = 0
		syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
		print("syslog: {}".format(syslog))  # Debug message
		self.write_system_log(syslog)
		self.__sync_last = time.localtime()

		if not self.__said_hi_to_brainbox:
			self.__said_hi_to_brainbox = True
		if "brainbox_response" in vars():
			brainbox_response.close()
		return success

	def purge_logs(self):
		cn = FoodBoxDB()  # type: FoodBoxDB
		cn.purge_logs()
		self.__last_purge = time.time()
		del cn

		self.__set_system_setting(SystemSettings.Last_Purge, self.__last_purge)
		logstr = "Logs purged."
		logtype = MessageTypes.Information
		logsev = 0
		syslog = SystemLog(
			message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev, card=None
		)
		print("syslog: {}".format(syslog))  # Debug message
		self.write_system_log(syslog)

		return True

	def start_mainloop(self):
		"""The main loop of reading card, checking access and writing logs.

		:rtype: bool
		"""
		while True:
			if time.time() - time.mktime(self.__sync_last) >= self.__sync_interval:
				sync_success = self.sync_foodbox_with_brainbox()
				if sync_success:
					sync_uid, sync_success = self.sync_with_brainbox()
				if sync_success:
					self.sync_cards_from_brainbox()

				if time.time() - self.__last_purge >= 1440:
					self.purge_logs()

			carduid = self.__rfid_scanner.get_uid()
			if carduid is None:
				time.sleep(0.1)
				continue

			cn = FoodBoxDB()  # type: FoodBoxDB
			card = cn.get_card_byID(carduid)  # type: RFIDCard
			del cn
			if card is None or not card.get_active():
				logstr = "Invalid card tried to open box."
				logtype = MessageTypes.Information
				logsev = 1
				syslog = SystemLog(
					message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev, card=carduid
				)
				print("syslog: {}".format(syslog))  # Debug message
				self.write_system_log(syslog)
				old_carduid = carduid
				while self.__rfid_scanner.get_uid() == old_carduid:
					time.sleep(0.1)
				continue

			logstr = "Opened lid for card."
			admin_card = False
			if card.get_name() == "ADMIN":
				logstr = "ADMIN card opened the box."
				admin_card = True
			logtype = MessageTypes.Information
			logsev = 0
			syslog = SystemLog(
				message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev, card=carduid
			)
			print("syslog: {}".format(syslog))  # Debug message
			self.write_system_log(syslog)
			open_time = time.localtime()
			start_weight = self.__scale.get_units()
			print("Starting weight is: ", start_weight)
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
					syslog = SystemLog(
						message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev,
						card=carduid
					)
					print("syslog: {}".format(syslog))  # Debug message
					self.write_system_log(syslog)
				# TODO - Beep at the cat

			self.close_lid()
			close_time = time.localtime()
			end_weight = self.__scale.get_units()
			print("End weight is: ", end_weight)
			if admin_card:
				self.admin_refill(start_weight=start_weight, end_weight=end_weight, card_uid=carduid)
				continue
			feedinglog = FeedingLog(
				card=card, open_time=open_time, close_time=close_time, start_weight=start_weight, end_weight=end_weight,
				feeding_id=uuid.uuid4().hex
			)
			print("feedinglog: {}".format(feedinglog))  # Debug message
			self.write_feeding_log(feedinglog)
			self.__last_weight = end_weight
			self.__set_system_setting(SystemSettings.Last_Weight, end_weight)
			del feedinglog
			if self.__sync_on_change:
				sync_success = self.sync_foodbox_with_brainbox()
				if sync_success:
					sync_uid, sync_success = self.sync_with_brainbox()
				if sync_success:
					self.sync_cards_from_brainbox()

			if False:  # Ignore me.
				break
		return False

	def open_lid(self):
		# Fake open for debugging
		# print("Opening.")
		# time.sleep(1)
		# print("Open.")
		# self.__lid_open = True
		if self.__lid_open:
			return True
		self.__stepper.quarter_rotation_forward()
		self.__lid_open = True
		return True

	def close_lid(self):
		# Fake close for debugging
		# print("Closing.")
		# time.sleep(1)
		# print("Closed.")
		# self.__lid_open = False
		if not self.__lid_open:
			return True
		self.__stepper.quarter_rotation_backward()
		self.__lid_open = False
		return True

	def start_network_discovery(self):
		logstr = "Starting network discovery."
		logtype = MessageTypes.Information
		logsev = 0
		syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
		print("syslog: {}".format(syslog))  # Debug message
		self.write_system_log(syslog)
		print(logstr)

		zeroconf = Zeroconf()
		self.__browser = ServiceBrowser(zeroconf, "_FatCatBB._tcp.local.", handlers=[self.on_service_state_change])
		return None

	def stop_network_discovery(self):
		logstr = "Stopping network discovery."
		logtype = MessageTypes.Information
		logsev = 0
		syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
		print("syslog: {}".format(syslog))  # Debug message
		self.write_system_log(syslog)
		print(logstr)

		self.__browser.zc.close()
		return None

	def on_service_state_change(
			self, zeroconf: Zeroconf, service_type: ZeroconfServiceTypes, name: str, state_change: ServiceStateChange):
		logstr = "service_state_change"
		logtype = MessageTypes.Information
		logsev = 0
		syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
		print("syslog: {}".format(syslog))  # Debug message
		self.write_system_log(syslog)

		info = zeroconf.get_service_info(service_type, name)
		if info:
			if state_change is ServiceStateChange.Added:
				print("IP: {0} - PORT: {1}".format(socket.inet_ntoa(info.address), info.port))
				if time.time() - time.mktime(self.__sync_last) >= self.__sync_interval:
					self.__sync_last = time.localtime(
						time.time() - self.__sync_interval + 20
					)
				self.__brainbox_ip_address = info.address
				self.__brainbox_port_number = info.port
				self.__set_system_setting(setting=SystemSettings.BrainBox_IP, value=socket.inet_ntoa(info.address))
				self.__set_system_setting(setting=SystemSettings.BrainBox_Port, value=info.port)

				logstr = "BrainBox_IP and BrainBox_Port updates - {0}:{1}".format(
					socket.inet_ntoa(info.address), info.port
				)
				logtype = MessageTypes.Information
				logsev = 0
				syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
				print("syslog: {}".format(syslog))  # Debug message
				self.write_system_log(syslog)

			# if not self.__said_hi_to_brainbox:
			# 	self.sync_foodbox_with_brainbox()
			elif state_change is ServiceStateChange.Removed:  # We never get inside here, because it always goes to else
				print(
					"BrainBox_IP and BrainBox_Port removed. - This is the 'We never get inside her' part."
				)  # Debug message.
				self.__brainbox_ip_address = None
				self.__brainbox_port_number = None
				self.__set_system_setting(setting=SystemSettings.BrainBox_IP, value=None)
				self.__set_system_setting(setting=SystemSettings.BrainBox_Port, value=None)

				logstr = "BrainBox_IP and BrainBox_Port removed."
				logtype = MessageTypes.Information
				logsev = 0
				syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
				print("syslog: {}".format(syslog))  # Debug message
				self.write_system_log(syslog)
		else:
			print("BrainBox_IP and BrainBox_Port removed.")  # Debug message
			self.__brainbox_ip_address = None
			self.__brainbox_port_number = None
			self.__set_system_setting(setting=SystemSettings.BrainBox_IP, value=None)
			self.__set_system_setting(setting=SystemSettings.BrainBox_Port, value=None)

			logstr = "BrainBox_IP and BrainBox_Port removed."
			logtype = MessageTypes.Information
			logsev = 0
			syslog = SystemLog(message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev)
			print("syslog: {}".format(syslog))  # Debug message
			self.write_system_log(syslog)

	def admin_refill(self, start_weight: float, end_weight: float, card_uid: str):
		logstr = "ADMIN refilled the box from: {0} to {1}.".format(start_weight, end_weight)
		logtype = MessageTypes.Information
		logsev = 0
		syslog = SystemLog(
			message=logstr, message_type=logtype, time_stamp=time.localtime(), severity=logsev, card=card_uid
		)
		print("syslog: {}".format(syslog))  # Debug message
		self.write_system_log(syslog)
		self.__last_weight = end_weight
		self.__set_system_setting(SystemSettings.Last_Weight, end_weight)

		sync_success = self.sync_foodbox_with_brainbox()
		if sync_success:
			sync_uid, sync_success = self.sync_with_brainbox()
		if sync_success:
			self.sync_cards_from_brainbox()
