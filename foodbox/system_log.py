import time
from enum import Enum


class MessageTypes(Enum):
	Information = 1  # General information
	Error = 2  # Something bad happened but operation can continue
	Fatal = 3  # Something bad happened and program has to stop


class SystemLog:
	__rowid = None
	__card = None  # Card class object
	__timestamp = None  # time.struct_time
	__type = None  # MessageTypes
	__severity = None
	__msg = None

	def __init__(self, message, rowid=None, card=None, time_stamp=time.gmtime(),
				 message_type=MessageTypes.Information, severity=0):
		self.set_rowid(rowid=rowid)
		self.set_card(card=card)
		self.set_time_stamp(time_stamp=time_stamp)
		self.set_message_type(message_type=message_type)
		self.set_severity(severity=severity)
		self.set_message(message=message)

	def __del__(self):
		del self.__card
		del self.__timestamp

	def get_rowid(self):
		return self.__rowid

	def set_rowid(self, rowid):
		if rowid is None:
			self.__rowid = None
		elif type(rowid) is int:
			self.__rowid = rowid
		else:
			# TODO - Write a fatal error to the log and throw an exception
			return

	def get_card(self):
		return self.__card

	def set_card(self, card):
		# TODO - complete this with Card class
		if card is None:
			self.__card = None
		# elif type(card_id) is PlaceHolderForCardClass:
		# 	self.__card = card
		else:
			# TODO - Write a fatal error to the log and throw an exception
			return

	def get_time_stamp(self):
		return self.__timestamp

	def set_time_stamp(self, time_stamp):
		if type(time_stamp) is time.struct_time:
			self.__timestamp = time_stamp
		elif type(time_stamp) is float or type(time_stamp) is int:
			self.__timestamp = time.gmtime(time_stamp)
		else:
			# TODO - Write a fatal error to the log and throw an exception
			return

	def get_message_type(self):
		return self.get_message_type()

	def set_message_type(self, message_type):
		if type(message_type) is type(MessageTypes):
			self.__type = message_type
		else:
			# TODO - Write a fatal error to the log and throw an exception
			return

	def get_severity(self):
		return self.__severity

	def set_severity(self, severity):
		if type(severity) is int:
			self.__severity = severity
		else:
			# TODO - Write a fatal error to the log and throw an exception
			return

	def get_message(self):
		return self.__msg

	def set_message(self, message):
		if type(message) is str:
			self.__msg = message
		else:
			# TODO - Write a fatal error to the log and throw an exception
			return
