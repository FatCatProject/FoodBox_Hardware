import sqlite3
import os.path


def create_foodboxDB():
	"""
	Create new DB file and connect to it
	Check if the DB was created successfully
	If not throw exception
	"""
	try:
		conn = sqlite3.connect('foodboxDB.db')
	except sqlite3.OperationalError:
		pass
	finally:
		# TODO logic
		print('Eror creating DB')

	c = conn.cursor()
	c.execute('CREATE TABLE IF NOT EXISTS system_settings('
			  'key_name TEXT NOT NULL , '
			  'value_text TEXT, '
			  'PRIMARY KEY(`key_name`) );')

	c.execute('CREATE TABLE IF NOT EXISTS system_logs('
			  'card_id TEXT, '
			  'time_stamp TEXT NOT NULL,'
			  'message TEXT, '
			  'message_type TEXT NOT NULL,'
			  'severity INTEGER NOT NULL,'
			  'FOREIGN KEY(`card_id`) REFERENCES `cards`, '
			  'FOREIGN KEY(`message_type`) REFERENCES `message_types` );')

	c.execute('CREATE TABLE IF NOT EXISTS feeding_logs('
			  'feeding_id INTEGER NOT NULL ,'
			  'card_id TEXT NOT NULL,'
			  'open_time TEXT NOT NULL,'
			  'close_time TEXT NOT NULL,'
			  'starting_weight NUMERIC NOT NULL,'
			  'ending_weight NUMERIC NOT NULL,'
			  'synced INTEGER NOT NULL,'
			  'PRIMARY KEY(`feeding_id`), '
			  'FOREIGN KEY(`card_id`) REFERENCES `cards` );')

	c.execute('CREATE TABLE IF NOT EXISTS cards('
			  '`card_id` TEXT NOT NULL , '
			  '`active` INTEGER NOT NULL,'
			  'PRIMARY KEY(`card_id`) );')

	conn.commit()
	c.close()
	conn.close()
