import time


class SystemLog:
	__rowid = None
	__card_id = None
	__timestamp = None
	__type = None
	__severity = None
	__msg = None

	def __init__(self, message, rowid=None, card_id=None, time_stamp=time.gmtime(), message_type="Info", severity=0):
		self.__rowid = rowid
		self.__card_id = card_id
		self.__timestamp = time_stamp
		self.__type = message_type
		self.__severity = severity
		self.__msg = message
		pass

	def get_rowid(self):
		return self.__rowid

	def set_rowid(self, rowid):
		self.__rowid = rowid

	def get_card_id(self):
		return self.__card_id

	def set_card_id(self, card_id):
		self.__card_id = card_id
