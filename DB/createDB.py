import sqlite3
import os.path


def create_foodboxDB():
	# Create new file and connect to it
	conn = sqlite3.connect('foodboxDB.db')

	# Check if file was created successfully
	if os.path.exists('foodboxDB.db') == False:
		# TODO  Create Exeption for error on creating a DB file instead of printing it
		print('Error creating DB file')
	else:
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
