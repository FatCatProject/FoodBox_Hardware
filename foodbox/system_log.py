import time
from Hardware import RFIDCard
from enum import Enum


class MessageTypes(Enum):
	Information = 1  # General information
	Error = 2  # Something bad happened but operation can continue
	Fatal = 3  # Something bad happened and program has to stop


class SystemLog:
	__rowid = None  # type: int
	__card_uid = None  # type: str
	__timestamp = None  # type: time.struct_time
	__msg_type = None  # type: MessageTypes
	__severity = None  # type: int
	__msg = None  # type: str

	def __init__(self, message: str, rowid: int = None, card: str = None, time_stamp=time.gmtime(),
			message_type: MessageTypes = MessageTypes.Information, severity: int = 0):
		assert type(time_stamp) is time.struct_time or type(time_stamp) is int or type(time_stamp) is float
		self.__set_rowid(rowid=rowid)
		self.__set_card(card=card)
		self.__set_time_stamp(time_stamp=time_stamp)
		self.__set_message_type(message_type=message_type)
		self.__set_severity(severity=severity)
		self.__set_message(message=message)

	def __del__(self):
		del self.__card_uid
		del self.__timestamp

	def get_rowid(self):
		return self.__rowid

	def __set_rowid(self, rowid: int):
		assert rowid is None or type(rowid) is int, "rowid is neither an integer nor None, it is : %r" % type(rowid)
		self.__rowid = rowid
		return

	def get_card(self):
		return self.__card_uid

	def __set_card(self, card: str):
		assert card is None or type(card) is str, "card is neither an str nor None, it is : %r" % type(card)
		self.__card_uid = card
		return

	def get_time_stamp(self):
		return self.__timestamp

	def __set_time_stamp(self, time_stamp):
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
		return self.__msg_type

	def __set_message_type(self, message_type: MessageTypes):
		assert isinstance(message_type, MessageTypes), "message_type is not an MessageTypes, it is : %r" % type(
			message_type)
		self.__msg_type = message_type
		return

	def get_severity(self):
		return self.__severity

	def __set_severity(self, severity: int):
		assert type(severity) is int, "severity is not an int, it is : %r" % type(severity)
		self.__severity = severity
		return

	def get_message(self):
		return self.__msg

	def __set_message(self, message: str):
		assert type(message) is str, "message is not an str, it is : %r" % type(message)
		self.__msg = message
		return

	def __str__(self):
		string = "{0}, {1}, {2}, {3}, {4}, {5}".format(self.__rowid, self.__card_uid,
			time.asctime(self.__timestamp), self.__msg, self.__msg_type.name, self.__severity)
		return string

	def __repr__(self):
		return self.__str__()
