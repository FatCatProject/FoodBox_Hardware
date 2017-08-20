import time
from Hardware import RFIDCard
import uuid


class FeedingLog:
	__id = None  # Line id, uuid.UUID
	__card = None  # Card class object
	__open_time = None  # time.struct_time
	__close_time = None  # time.struct_time
	__start_weight = None
	__end_weight = None
	__synced = False

	def __init__(self, card, open_time, close_time, start_weight, end_weight, log_id=uuid.uuid4(), synced=False):
		self.set_card(card=card)
		self.set_open_time(open_time=open_time)
		self.set_close_time(close_time=close_time)
		self.set_start_weight(weight=start_weight)
		self.set_end_weight(weight=end_weight)
		self.set_id(log_id=log_id)
		self.set_synced(synced=synced)

	def __del__(self):
		del self.__id
		del self.__card
		del self.__open_time
		del self.__close_time

	def get_id(self, in_hex=True):
		if in_hex:
			return self.__id.hex
		else:
			return self.__id

	def set_id(self, log_id):
		assert type(log_id) is uuid.UUID or type(log_id) is str, "id is neither a UUID or str, it is %r" % type(log_id)
		if type(log_id) is uuid.UUID:
			self.__id = uuid.UUID(log_id.hex)
			return
		try:
			self.__id = uuid.UUID(log_id)
		except Exception as e:
			raise e
		return

	def get_card(self):
		return self.__card

	def set_card(self, card):
		assert card is None or type(card) is RFIDCard, "card is neither an RFIDCard nor None, it is : %r" % type(card)
		self.__card = card
		return

	def get_open_time(self):
		return self.__open_time

	def set_open_time(self, open_time):
		assert type(open_time) is time.struct_time or type(open_time) is float or type(
			open_time) is int, "open_time is neither an time.struct_time nor int or float, it is : %r" % type(
			open_time)
		if type(open_time) is time.struct_time:
			self.__open_time = open_time
		else:
			self.__open_time = time.gmtime(open_time)
		return

	def get_close_time(self):
		return self.__close_time

	def set_close_time(self, close_time):
		assert type(close_time) is time.struct_time or type(close_time) is float or type(
			close_time) is int, "close_time is neither an time.struct_time nor int or float, it is : %r" % type(
			close_time)
		if type(close_time) is time.struct_time:
			self.__close_time = close_time
		else:
			self.__close_time = time.gmtime(close_time)
		return

	def get_start_weight(self):
		return self.__start_weight

	def set_start_weight(self, weight):
		assert not (
			type(weight) is float or type(weight) is int), "weight is neither and int or a float, it is an %r" % type(
			weight)
		assert weight >= 0, "weight is negative: %r" % weight
		self.__start_weight = weight
		return

	def get_end_weight(self):
		return self.__end_weight

	def set_end_weight(self, weight):
		assert not (
			type(weight) is float or type(weight) is int), "weight is neither and int or a float, it is an %r" % type(
			weight)
		assert weight >= 0, "weight is negative: %r" % weight
		self.__end_weight = weight
		return

	def get_synced(self):
		return self.__synced

	def set_synced(self, synced):
		assert type(synced) is bool, "synced is not a bool type, it is: %r" % type(synced)
		self.__synced = synced
		return
