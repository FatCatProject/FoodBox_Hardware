import time
from Hardware import RFIDCard
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
		assert rowid is None or type(rowid) is int, "rowid is neither an integer nor None, it is : %r" % type(rowid)
		self.__rowid = rowid
		return

	def get_card(self):
		return self.__card

	def set_card(self, card):
		assert card is None or type(card) is RFIDCard, "card is neither an RFIDCard nor None, it is : %r" % type(card)
		self.__card = card
		return

	def get_time_stamp(self):
		return self.__timestamp

	def set_time_stamp(self, time_stamp):
		assert type(time_stamp) is time.struct_time or type(time_stamp) is float or type(
			time_stamp) is int, "time_stamp is neither an time.struct_time nor int or float, it is : %r" % type(
			time_stamp)
		if type(time_stamp) is time.struct_time:
			self.__timestamp = time_stamp
		else:
			#  elif type(time_stamp) is float or type(time_stamp) is int:
			self.__timestamp = time.gmtime(time_stamp)
		return

	def get_message_type(self):
		return self.get_message_type()

	def set_message_type(self, message_type):
		assert type(message_type) is type(MessageTypes), "message_type is not an MessageTypes, it is : %r" % type(
			message_type)
		self.__type = message_type
		return

	def get_severity(self):
		return self.__severity

	def set_severity(self, severity):
		assert type(severity) is int, "severity is not an int, it is : %r" % type(severity)
		self.__severity = severity
		return

	def get_message(self):
		return self.__msg

	def set_message(self, message):
		assert type(message) is str, "message is not an str, it is : %r" % type(message)
		self.__msg = message
		return
