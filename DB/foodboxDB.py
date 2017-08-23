import sqlite3
import time
import datetime
import uuid
import os.path
from turtledemo.chaos import f

from Hardware.MFRC522.rfid_card import RFIDCard
from DB.createDB import create_foodboxDB
from foodbox.system_settings import SystemSettings
from foodbox.feeding_log import FeedingLog
from typing import Union, Tuple


class FoodBoxDB:
	def __init__(self):
		# Check if DB exists , if not - create it
		if not os.path.exists('foodboxDB.db'):
			create_foodboxDB()

		self.conn = sqlite3.connect('foodboxDB.db')
		self.c = self.conn.cursor()
		self.c.execute("PRAGMA foreign_keys = ON")

	def __del__(self):
		self.c.close()
		self.conn.close()

	### Start Card functiones ###
	def get_card_byID(self, cardID: str):
		self.c.execute('SELECT * FROM cards WHERE card_id = ?', (cardID,))
		cardData = self.c.fetchall()
		card = RFIDCard(cardData[0][0], cardData[0][2], cardData[0][1] == 1)
		return card

	def get_all_cards(self):
		"""
		Returns a tuple of all cards as RFIDCard objects
		"""
		self.c.execute('SELECT * FROM cards')
		cardsData = self.c.fetchall()
		cards = []
		for row in cardsData:
			isActive = True
			if row[1] == 0:
				isActive = False
				card = RFIDCard(row[0], row[2], isActive)
				cards.append(card)
			else:
				card = RFIDCard(row[0], row[2], isActive)
				cards.append(card)
		# print (tuple(cards))
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

	def set_state(self, cardID, newState: Union[str, bool]):
		"""
		Function gets cardID number and a state to set it to = Active or Not active
		Value can be 0/1 or true/false or True/False
		check if newState is boolean and change to True=1 or False=0
		If the card doesn't exist - Adding new card and setting the newState as requested
		"""
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
		self.set_state(cardID, 1)
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
		if self.c.rowcount == 0:
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
		if self.c.rowcount == 0:
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
						   end_weight=logData[0][5],
						   feeding_id=logData[0][0], synced=(logData[0][6] == 1))
		return myLog

	def add_feeding_log(self, myLog: FeedingLog):
		"""
		Getting a feeding_log as an object and Adding it to the DB
		"""
		self.c.execute(
			'INSERT INTO feeding_logs (feeding_id, card_id, open_time, close_time, start_weight, end_weight, synced)'
			' VALUES (?, ?, ?, ?, ?, ?, ?);',
			(str(myLog.get_id()), myLog.get_card().get_uid(), time.mktime(myLog.get_open_time()),
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

	def set_feeding_log_synced(self, myLog: FeedingLog):
		"""
		Get feeding_log OBJECT and change the synced status to True = 1
		"""
		self.c.execute('UPDATE feeding_logs SET synced = 1 WHERE feeding_id = ?', (myLog.get_id(),))
		self.conn.commit()


### END of feeding_logs functiones ###

### system_logs functiones ###
### END of system_logs functiones ###
"""
Printings and tests
"""
fbdb = FoodBoxDB()
card = fbdb.get_card_byID('138-236-209-167')
fLog = FeedingLog(card, 1503409879, 1503409904, 2, 1.5, '2d49780476064471b0f1dafe459195e2', True)
# print(fLog)
# fbdb.add_feeding_log(fLog)


# print(fbdb.get_all_cards())
# print(fbdb.get_active_cards())
# print(fbdb.get_not_active_cards())
# print(fbdb.card_state('126-126-126-126'))
# print(fbdb.set_state('129-129-129-129', True))
# fbdb.add_card('222-222-222-222')
# fbdb.delete_card('222-222-222-222')
# print(fbdb.get_all_cards())
# print(fbdb.get_system_setting(SystemSettings.FoodBox_Name))
# fbdb.set_system_setting(SystemSettings.FoodBox_Name, 'Elf')
# print(fbdb.get_system_setting(SystemSettings.FoodBox_Name))

# fbdb.set_state_from_object(card)

# print(fbdb.get_all_feeding_logs())
# print(fbdb.get_synced_feeding_logs())
# print(fbdb.get_not_synced_feeding_logs())
# fbdb.delete_synced_feeding_logs()



# fbdb.set_feeding_log_synced()

myLog = fbdb.get_feeding_log_by_id('d3e815b9a34742e39002a648c39da02e')
fbdb.set_feeding_log_synced(myLog)

