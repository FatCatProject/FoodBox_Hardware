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
		pass
	# print('Error creating DB')

	c = conn.cursor()
	c.execute("PRAGMA foreign_keys = ON")
	c.execute('CREATE TABLE IF NOT EXISTS system_settings('
			  'key_name TEXT NOT NULL , '
			  'value_text TEXT, '
			  'PRIMARY KEY(`key_name`) );')

	c.execute('CREATE TABLE IF NOT EXISTS system_logs('
			  'card_id TEXT, '
			  'time_stamp NUMERIC NOT NULL,'
			  'message TEXT, '
			  'message_type TEXT NOT NULL,'
			  'severity INTEGER NOT NULL);')

	c.execute('CREATE TABLE IF NOT EXISTS feeding_logs('
			  'feeding_id TEXT NOT NULL ,'
			  'card_id TEXT NOT NULL,'
			  'open_time NUMERIC NOT NULL,'
			  'close_time NUMERIC NOT NULL,'
			  'start_weight NUMERIC NOT NULL,'
			  'end_weight NUMERIC NOT NULL,'
			  'synced INTEGER NOT NULL,'
			  'PRIMARY KEY(`feeding_id`), '
			  'FOREIGN KEY(`card_id`) REFERENCES `cards` );')

	c.execute('CREATE TABLE IF NOT EXISTS cards('
			  '`card_id` TEXT NOT NULL , '
			  '`active` INTEGER NOT NULL,'
			  '`card_name` TEXT, '
			  'PRIMARY KEY(`card_id`) );')

	conn.commit()
	c.close()
	conn.close()
