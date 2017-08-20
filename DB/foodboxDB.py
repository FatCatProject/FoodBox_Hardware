import sqlite3
import time
import datetime
import os.path
from Hardware.MFRC522.rfid_card import RFIDCard
from DB.createDB import create_foodboxDB


class FoodBoxDB:
	def __init__(self):
		# Check if DB exists , if not - create it
		if not os.path.exists('foodboxDB.db'):
			create_foodboxDB()

		self.conn = sqlite3.connect('foodboxDB.db')
		self.c = self.conn.cursor()

	def __del__(self):
		self.c.close
		self.conn.close()

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
				card = RFIDCard(row[0], isActive)
				cards.append(card)
			else:
				card = RFIDCard(row[0], isActive)
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
				card = RFIDCard(row[0], isActive)
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
				card = RFIDCard(row[0], isActive)
				cards.append(card)
		# print (tuple(cards))
		return tuple(cards)

	def card_state(self, cardID):
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

	def set_state(self, cardID, newState):
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

	def add_card(self, cardID):
		"""
		Adding a new card with default state = Active
		"""
		self.set_state(cardID, 1)
		self.conn.commit()

	def delete_card(self, cardID):
		#  print(type(cardID))
		self.c.execute('DELETE FROM cards WHERE card_id = ?', (cardID,))
		self.conn.commit()


"""
Printing tests
"""
fbdb = FoodBoxDB()
print(fbdb.get_all_cards())
# print(fbdb.get_active_cards())
# print(fbdb.get_not_active_cards())
# print(fbdb.card_state('126-126-126-126'))
# print(fbdb.set_state('129-129-129-129', True))
fbdb.add_card('222-222-222-222')

fbdb.delete_card('222-222-222-222')
print(fbdb.get_all_cards())
