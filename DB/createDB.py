import sqlite3
import time
import os.path


def create_foodboxDB():
	"""
	Create new DB file and connect to it
	Check if the DB was created successfully
	If not throw exception
	"""
	print("create_foodboxDB() started.")  # Debug message

	try:
		conn = sqlite3.connect("foodboxDB.db")

		query_pragma = [
			"PRAGMA foreign_keys = ON;"
		]
		query_system_settings = [
			"CREATE TABLE IF NOT EXISTS system_settings(",
			"key_name TEXT NOT NULL, value_text TEXT, PRIMARY KEY('key_name')",
			");"
		]
		query_system_logs = [
			"CREATE TABLE IF NOT EXISTS system_logs(",
			"card_id TEXT, time_stamp NUMERIC NOT NULL, message TEXT,",
			"message_type TEXT NOT NULL, severity INTEGER NOT NULL",
			");"
		]
		query_feeding_logs = [
			"CREATE TABLE IF NOT EXISTS feeding_logs(",
			"feeding_id TEXT NOT NULL, card_id TEXT NOT NULL,",
			"open_time NUMERIC NOT NULL, close_time NUMERIC NOT NULL,",
			"start_weight NUMERIC NOT NULL, end_weight NUMERIC NOT NULL,",
			"synced INTEGER NOT NULL, PRIMARY KEY('feeding_id'),",
			"FOREIGN KEY('card_id') REFERENCES 'cards'",
			");"
		]
		query_cards = [
			"CREATE TABLE IF NOT EXISTS cards(",
			"card_id TEXT NOT NULL, active INTEGER NOT NULL, card_name TEXT,",
			"PRIMARY KEY('card_id')",
			");"
		]

		c = conn.cursor()
		c.execute(str.join(" ", query_pragma))
		c.execute(str.join(" ", query_system_settings))
		c.execute(str.join(" ", query_system_logs))
		c.execute(str.join(" ", query_feeding_logs))
		c.execute(str.join(" ", query_cards))

		conn.commit()
		c.close()
		conn.close()
	except sqlite3.OperationalError as e:
		print("Error creating DB - {}".format(e.args))

	print("create_foodboxDB() ended.")  # Debug message
