import os.path
import sqlite3
import time

from DB.createDB import create_foodboxDB
from Hardware.MFRC522.rfid_card import RFIDCard
from foodbox.feeding_log import FeedingLog
from foodbox.system_log import MessageTypes
from foodbox.system_log import SystemLog
from foodbox.system_settings import SystemSettings


class FoodBoxDB:
	def __init__(self):
		# Check if DB exists , if not - create it
		if not os.path.exists('foodboxDB.db'):
			create_foodboxDB()

		self.conn = sqlite3.connect('foodboxDB.db')
		self.c = self.conn.cursor()  # type: sqlite3.Cursor
		self.c.execute("PRAGMA foreign_keys = ON")

	def __del__(self):
		self.c.close()
		self.conn.close()

	### Start Card functiones ###
	def get_card_byID(self, cardID: str):
		self.c.execute('SELECT * FROM cards WHERE card_id = ?', (cardID,))
		cardData = self.c.fetchall()
		if len(cardData) <= 0:
			return None
		print(cardData)  # TODO - Delete this print after fixing the problem with index out of bounds
		card = RFIDCard(cardData[0][0], cardData[0][2], cardData[0][1] == 1)
		return card

	def get_all_cards(self):
		"""
		Returns a tuple of all cards as RFIDCard objects
		"""
		self.c.execute('SELECT * FROM cards')
		cardsData = self.c.fetchall()
		# print(cardsData)
		cards = []

		for row in cardsData:
			card = RFIDCard(str(row[0]), row[2], row[1] == 1)
			cards.append(card)
		return tuple(cards)

	def get_active_cards(self):
		"""
		Returns a tuple of all active cards  as RFIDCard objects
		"""
		self.c.execute('SELECT * FROM cards')
		cardsData = self.c.fetchall()
		cards = []
		for row in cardsData:
			isActive = True
			if row[1] == 1:
				card = RFIDCard(row[0], row[2], isActive)
				cards.append(card)
		# print (tuple(cards))
		return tuple(cards)

	def get_not_active_cards(self):
		"""
		Returns a tuple of all non-active cards  as RFIDCard objects
		"""
		self.c.execute('SELECT * FROM cards')
		cardsData = self.c.fetchall()
		# print(cardsData)
		cards = []
		for row in cardsData:
			isActive = False
			if row[1] == 0:
				card = RFIDCard(row[0], row[2], isActive)
				cards.append(card)
		# print (tuple(cards))
		return tuple(cards)

	def card_state(self, cardID: str):
		"""
		Function is getting a CardID and checks if the card exists in DB and it's state - active or not
		We'll use it for adding new cards go DB
		-------------------------------------------------
		If card exists but not active will set to active
		If it doesn't exist we'll add a new card to DB
		Returns(Bool,Bool)==(Exists, IsActive)
		"""
		exists = False
		state = False
		# state: True-Active / False-NotActive
		self.c.execute('SELECT * FROM cards')
		cardsData = self.c.fetchall()
		for row in cardsData:
			if row[0] == cardID:
				exists = True
				if row[1] == 1:
					state = True
		return exists, state

	def set_state_from_object(self, mycard: RFIDCard):
		"""
		Function gets card as object and sets the state as requested
		If the card doesn't exist - Adding new card and setting the newState as requested
		"""
		cardID = mycard.get_uid()
		newState = mycard.get_active()
		self.set_state(cardID, newState)

	def set_state(self, cardID, newState):
		"""
		Function gets cardID number and a state to set it to = Active or Not active
		Value can be 0/1 or true/false or True/False
		check if newState is boolean and change to True=1 or False=0
		If the card doesn't exist - Adding new card and setting the newState as requested
		"""
		assert type(newState) is str or type(newState) is bool, "Wrong type"
		exists, state = self.card_state(cardID)
		if newState == 1 or newState == 0:
			setNewState = newState
		if newState == True or newState == 'true':
			setNewState = 1
		if newState == False or newState == 'false':
			setNewState = 0
		if exists == False:
			# if card doesn't exist - Adding new card and setting the newState as requested
			self.c.execute('INSERT INTO cards (card_id, active) VALUES (?, ?)', (cardID, setNewState))
			self.conn.commit()
		if exists == True:
			# if card exists - setting the newState as requested
			self.c.execute('UPDATE cards SET active = ? WHERE card_id = ?', (setNewState, cardID))
			self.conn.commit()

	def add_card(self, cardID: str):
		"""
		Adding a new card with default state = Active
		"""
		self.set_state(cardID, 1==1)
		self.conn.commit()

	def delete_card(self, cardID: str):
		"""Function that deletes a card by cardID """
		#  print(type(cardID))
		self.c.execute('DELETE FROM cards WHERE card_id = ?', (cardID,))
		self.conn.commit()

	### END of Card functiones ###

	### Start system_settings functiones ###
	def get_system_setting(self, setting: SystemSettings):
		"""Function returns a value of a specific setting from enums that are available:
			the input must be "SystemSettings.key_name"
			key names: BrainBox_IP / FoodBox_ID / FoodBox_Name / Max_Open_Time / Scale_Offset / Scale_Scale / Sync_Interval
			If the key_name is still not written in the DB or has no value it returns None
		"""
		self.c.execute('SELECT * FROM system_settings WHERE key_name = ?', (setting.name,))
		data = self.c.fetchall()
		if len(data) <= 0:
			return None
		else:
			for row in data:
				if row[0] == setting.name:
					return row[1]

	def set_system_setting(self, setting: SystemSettings, value: str):
		"""
		Function sets a value to a key in "system_settings" table
		If the key doesn't exist yet , it will write a new row with the key and value
		"""
		self.c.execute('UPDATE system_settings SET value_text = ? WHERE key_name = ?', (value, setting.name))
		self.conn.commit()
		if self.c.rowcount <= 0:
			self.c.execute('INSERT INTO system_settings (key_name, value_text) VALUES (?, ?)', (setting.name, value))
			self.conn.commit()

		### END of system_settings functiones ###

		### Start feeding_logs functiones ###

	def get_feeding_log_by_id(self, logID: str):
		"""
		Function gets a feeding_log ID and returns a feeding_log OBJECT
		"""
		self.c.execute('SELECT * FROM feeding_logs WHERE feeding_id = ?', (logID,))
		logData = self.c.fetchall()
		card = self.get_card_byID(str(logData[0][1]))
		myLog = FeedingLog(card, open_time=logData[0][2], close_time=logData[0][3], start_weight=logData[0][4],
			end_weight=logData[0][5], feeding_id=logData[0][0], synced=(logData[0][6] == 1))
		return myLog

	def add_feeding_log(self, myLog: FeedingLog):
		"""
		Getting a feeding_log as an object and Adding it to the DB
		"""
		self.c.execute(
			'INSERT INTO feeding_logs (feeding_id, card_id, open_time, close_time, start_weight, end_weight, synced)'
			' VALUES (?, ?, ?, ?, ?, ?, ?);', (
			str(myLog.get_id()), myLog.get_card().get_uid(), time.mktime(myLog.get_open_time()),
			time.mktime(myLog.get_close_time()), myLog.get_start_weight(), myLog.get_end_weight(), myLog.get_synced()))
		self.conn.commit()

	def get_all_feeding_logs(self):
		"""
		Returns a tuple of all feeding logs , the cards are objects inside the tuple
		"""
		self.c.execute('SELECT * FROM feeding_logs JOIN cards ON feeding_logs.card_id=cards.card_id')
		logData = self.c.fetchall()
		logs = []
		for row in logData:
			thisCard = RFIDCard(row[7], row[9], row[8] == 1)
			log = FeedingLog(thisCard, open_time=row[2], close_time=row[3], start_weight=row[4], end_weight=row[5],
				feeding_id=row[0], synced=(row[6] == 1))
			logs.append(log)
		return tuple(logs)

	def get_synced_feeding_logs(self):
		"""
		Returns a tuple of synced feeding logs , the cards are objects inside the tuple
		"""
		self.c.execute('SELECT * FROM feeding_logs JOIN cards ON feeding_logs.card_id=cards.card_id WHERE synced=1')
		logData = self.c.fetchall()
		# print(logData)
		logs = []
		for row in logData:
			thisCard = RFIDCard(row[7], row[9], row[8] == 1)
			log = FeedingLog(thisCard, open_time=row[2], close_time=row[3], start_weight=row[4], end_weight=row[5],
				feeding_id=row[0], synced=(row[6] == 1))
			logs.append(log)
		return tuple(logs)

	def get_not_synced_feeding_logs(self):
		"""
		Returns a tuple of synced feeding logs , the cards are objects inside the tuple
		"""
		self.c.execute('SELECT * FROM feeding_logs JOIN cards ON feeding_logs.card_id=cards.card_id WHERE synced=0')
		logData = self.c.fetchall()
		# print(logData)
		logs = []
		for row in logData:
			thisCard = RFIDCard(row[7], row[9], row[8] == 1)
			log = FeedingLog(thisCard, open_time=row[2], close_time=row[3], start_weight=row[4], end_weight=row[5],
				feeding_id=row[0], synced=(row[6] == 1))
			logs.append(log)
		return tuple(logs)

	def delete_synced_feeding_logs(self):
		"""
		Delete all synced feeding_logs from the DB
		"""
		self.c.execute('DELETE FROM feeding_logs WHERE synced = 1')
		self.conn.commit()

	def set_feeding_log_synced(self, myLogUID: str):
		"""
		Get feeding_log UID and change the synced status to True = 1
		"""
		self.c.execute('UPDATE feeding_logs SET synced = 1 WHERE feeding_id = ?', (myLogUID,))
		self.conn.commit()

	### END of feeding_logs functiones ###
	def get_system_log_by_id(self, logID: int):
		"""Function gets a SystemLog ID and returns a SystemLog object or None if no such object
		:arg logID: SystemLog ID
		:type logID: int
		:return ret_log: The requested log or None
		:rtype ret_log: Union[SystemLog, None]
		"""
		ret_log = None  # type: SystemLog
		self.c.execute(
			'SELECT rowid, card_id, time_stamp, message, message_type, severity FROM system_logs WHERE rowid = {}'.format(
				logID))
		data = self.c.fetchone()
		if len(data) == 0:
			return ret_log

		rowid = data[0]  # type: int
		card_id = data[1]  # type: str
		time_stamp = int(data[2])  # type: int
		msg = data[3]  # type: str
		msg_type = MessageTypes[data[4]]  # type: MessageTypes
		severity = data[5]  # type: int
		ret_log = SystemLog(message=msg, rowid=rowid, card=card_id, time_stamp=time_stamp, message_type=msg_type,
			severity=severity)
		return ret_log

	def add_system_log(self, myLog: SystemLog):
		"""Function gets a SystemLog object and writes it to the database

		:arg myLog: The SystemLog to write to the database
		:type myLog: SystemLog
		:return log_rowid: rowid if log was written successfully or None if not
		:rtype log_rowid: Union[int, None]
		"""
		log_rowid = None  # type: int
		self.c.execute('INSERT INTO system_logs (card_id, time_stamp, message, message_type, severity) VALUES(\'{0}\', '
					   '{1}, \'{2}\', \'{3}\', {4})'.format(str(myLog.get_card()),
													time.mktime(myLog.get_time_stamp()),
													str(myLog.get_message()),
													myLog.get_message_type().name,
													myLog.get_severity()))
		log_rowid = self.c.lastrowid
		print(log_rowid)
		self.conn.commit()
		return False

	def get_all_system_logs(self, logs_since: time.struct_time = None):
		"""Returns a tuple of all system logs since logs_since, or all of them

		:arg logs_since: Limit logs to a date, if it's None then no limit on date.
		:type logs_since: Union[None, time.struct_time]
		:return systemlog_tuple: A tuple of SystemLogs
		:rtype systemlog_tuple: Tuple[SystemLog]
		"""
		log_list = []  # type: List[SystemLog]
		if logs_since is None:
			self.c.execute('SELECT rowid, card_id, time_stamp, message, message_type, severity FROM system_logs')
		else:
			self.c.execute(
				'SELECT rowid, card_id, time_stamp, message, message_type, severity FROM system_logs WHERE time_stamp >= {0}'.format(
					time.mktime(logs_since)))

		logs_data = self.c.fetchall()
		for row in logs_data:
			rowid = row[0]  # type: int
			card_id = row[1]  # type: str
			time_stamp = int(row[2])  # type: int
			msg = row[3]  # type: str
			msg_type = MessageTypes[row[4]]  # type: MessageTypes
			severity = row[5]  # type: int
			log_list.append(
				SystemLog(message=msg, rowid=rowid, card=card_id, time_stamp=time_stamp, message_type=msg_type,
					severity=severity))

		return tuple(log_list)


### system_logs functions ###

### END of system_logs functions ###
"""
Printings and tests
"""
fbdb = FoodBoxDB()
##fbdb.add_card('138-236-209-167-111')
# sysLog = SystemLog('mymsg', None, None, time.gmtime(),MessageTypes.Information, 1)
#
# fbdb.add_system_log(sysLog)
# card = fbdb.get_card_byID('138-236-209-167-001')
# print(card)
# fLog = FeedingLog(card, 1503409879, 1503409904, 2, 1.5, '06d32ba16ba544d49718c9506030308e', True)
# print(fLog)
# fbdb.add_feeding_log(fLog)
# print(fbdb.get_all_cards())
# print(fbdb.get_active_cards())
# print(fbdb.get_not_active_cards())
# print(fbdb.card_state('175-244-217-141-000'))
# print(fbdb.set_state('138-236-209-167-001', False))
# fbdb.add_card('222-222-222-222-222')
# fbdb.delete_card('222-222-222-222-222')
# print(fbdb.get_system_setting(SystemSettings.FoodBox_Name))
# fbdb.set_system_setting(SystemSettings.FoodBox_Name, 'Elfik')
# print(fbdb.get_system_setting(SystemSettings.FoodBox_Name))
# crd = RFIDCard('138-236-209-167-111', True)
# fbdb.set_state_from_object(crd)
# print(fbdb.get_all_feeding_logs())
# print(fbdb.get_synced_feeding_logs())
# print(fbdb.get_not_synced_feeding_logs())
# fbdb.delete_synced_feeding_logs()
# myLog = fbdb.get_feeding_log_by_id('b61290112d3140f6969a0983219f7b98')
# print(myLog)
# fbdb.set_feeding_log_synced(myLog)
