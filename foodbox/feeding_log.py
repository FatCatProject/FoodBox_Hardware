import time
import uuid

class FeedingLog:

	__id = None  # Line id, uuid.UUID
	__card = None  # Card class object
	__open_time = None  # time.struct_time
	__close_time = None  # time.struct_time
	__start_weight = None
	__end_weight = None
	__synced = False

	def __init__(self, card, open_time, close_time, start_weight, end_weight, id=uuid.uuid4(), synced=False):
		pass

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

	def set_id(self, id):
		if type(id) is uuid.UUID:
			self.__id = uuid.UUID(id.hex)
			return
		try:
			self.__id = uuid.UUID(id)
		except:
			# TODO - Write a fatal error to the log and throw an exception
			pass
		return

	def get_card(self):
		return self.__card

	def set_card(self, card):
		# TODO - complete this with Card class
		if card is None:
			self.__card = None
		# elif type(card) is PlaceHolderForCardClass:
		# 	self.__card = card
		else:
			# TODO - Write a fatal error to the log and throw an exception
			return

	def get_open_time(self):
		return self.__open_time

	def set_open_time(self, open_time):
		if type(open_time) is time.struct_time:
			self.__open_time = open_time
		elif type(open_time) is float or type(open_time) is int:
			self.__open_time = time.gmtime(open_time)
		else:
			# TODO - Write a fatal error to the log and throw an exception
			return

	def get_close_time(self):
			return self.__close_time

	def set_close_time(self, close_time):
			if type(close_time) is time.struct_time:
				self.__close_time = close_time
			elif type(close_time) is float or type(close_time) is int:
				self.__close_time = time.gmtime(close_time)
			else:
				# TODO - Write a fatal error to the log and throw an exception
				return

	def get_start_weight(self):
		return self.__start_weight

	def set_start_weight(self, weight):
		# TODO - Do we check that start_weight <= end_weight?
		if not (type(weight) is float or type(weight) is int):
			# TODO - Write a fatal error to the log and throw an exception
			pass
		elif weight < 0:
			# TODO - Write a fatal error to the log and throw an exception
			return
		self.__start_weight = weight
		return

	def get_end_weight(self):
			return self.__end_weight

	def set_end_weight(self, weight):
		# TODO - Do we check that start_weight <= end_weight?
		if not (type(weight) is float or type(weight) is int):
			# TODO - Write a fatal error to the log and throw an exception
			pass
		elif weight < 0:
			# TODO - Write a fatal error to the log and throw an exception
			return
		self.__end_weight = weight
		return

	def get_synced(self):
		return self.__synced

	def set_synced(self, synced):
		if type(synced) is bool:
			self.__synced = synced
		else:
			# TODO - Write a fatal error to the log and throw an exception
			return
