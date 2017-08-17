import sqlite3
import time
import datetime
import os.path
from DB.createDB import create_foodboxDB

# Check if DB exists , if not - create it
if os.path.exists('foodboxDB.db') == False:
	create_foodboxDB()

conn = sqlite3.connect('foodboxDB.db')
c = conn.cursor()


def get_all_cards():
	c.execute('SELECT * FROM cards')
	cardsData = c.fetchall()
	cards=[]
	for row in cardsData:
		isActive = True
		if row[1] == 0:
			isActive = False
			cards.append((row[0],isActive))
		else:
			cards.append((row[0], isActive))
	#print (tuple(cards))
	return tuple(cards)

def get_active_cards():
	c.execute('SELECT * FROM cards')
	cardsData = c.fetchall()
	cards=[]
	for row in cardsData:
		isActive = True
		if row[1] == 1:
			cards.append((row[0],isActive))
	print (tuple(cards))
	return tuple(cards)

def get_not_active_cards():
	c.execute('SELECT * FROM cards')
	cardsData = c.fetchall()
	cards=[]
	for row in cardsData:
		isActive = False
		if row[1] == 0:
			cards.append((row[0],isActive))
	print (tuple(cards))
	return tuple(cards)

get_all_cards()
get_active_cards()
get_not_active_cards()

c.close
conn.close()