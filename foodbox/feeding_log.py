import time
from Hardware import RFIDCard
import uuid
from typing import Union


class FeedingLog:
	__feeding_id: str = None  # Line id
	__card: RFIDCard = None  # Card class object
	__open_time: time.struct_time = None  # type: time.struct_time
	__close_time: time.struct_time = None  # type: time.struct_time
	__start_weight: Union[int, float] = None
	__end_weight: Union[int, float] = None
	__synced: bool = False

	def __init__(self, card: RFIDCard, open_time: time.struct_time, close_time: time.struct_time,
			start_weight: Union[int, float], end_weight: Union[int, float],
			feeding_id: str = uuid.uuid4().hex, synced: bool = False) -> None:
		self.__set_card(card=card)
		self.__set_open_time(open_time=open_time)
		self.__set_close_time(close_time=close_time)
		self.__set_start_weight(weight=start_weight)
		self.__set_end_weight(weight=end_weight)
		self.__set_id(feeding_id=feeding_id)
		self.__set_synced(synced=synced)

	def __del__(self):
		del self.__feeding_id
		del self.__card
		del self.__open_time
		del self.__close_time

	def get_id(self) -> Union[uuid.UUID, int]:
		return self.__feeding_id

	def __set_id(self, feeding_id: str) -> None:
		assert type(feeding_id) is str, "id is not an str, it is %r" % type(feeding_id)
		try:
			self.__feeding_id = uuid.UUID(feeding_id).hex
		except Exception as e:
			raise e
		return

	def get_card(self) -> RFIDCard:
		return self.__card

	def __set_card(self, card: RFIDCard) -> None:
		assert card is None or type(card) is RFIDCard, "card is neither an RFIDCard nor None, it is : %r" % type(card)
		self.__card = card
		return

	def get_open_time(self) -> time.struct_time:
		return self.__open_time

	def __set_open_time(self, open_time: time.struct_time) -> None:
		assert type(open_time) is time.struct_time or type(open_time) is float or type(
				open_time) is int, "open_time is neither an time.struct_time nor int or float, it is : %r" % type(
				open_time)
		if type(open_time) is time.struct_time:
			self.__open_time = open_time
		else:
			self.__open_time = time.gmtime(open_time)
		return

	def get_close_time(self) -> time.struct_time:
		return self.__close_time

	def __set_close_time(self, close_time: time.struct_time) -> None:
		assert type(close_time) is time.struct_time or type(close_time) is float or type(
				close_time) is int, "close_time is neither an time.struct_time nor int or float, it is : %r" % type(
				close_time)
		if type(close_time) is time.struct_time:
			self.__close_time = close_time
		else:
			self.__close_time = time.gmtime(close_time)
		return

	def get_start_weight(self) -> Union[int, float]:
		return self.__start_weight

	def __set_start_weight(self, weight: Union[int, float]) -> None:
		assert type(weight) is float or type(weight) is int, "weight is neither and int or a float, it is an %r" % type(
				weight)
		assert weight >= 0, "weight is negative: %r" % weight
		self.__start_weight = weight
		return

	def get_end_weight(self) -> Union[int, float]:
		return self.__end_weight

	def __set_end_weight(self, weight: Union[int, float]) -> None:
		assert type(weight) is float or type(weight) is int, "weight is neither and int or a float, it is an %r" % type(
				weight)
		assert weight >= 0, "weight is negative: %r" % weight
		self.__end_weight = weight
		return

	def get_synced(self) -> bool:
		return self.__synced

	def __set_synced(self, synced: bool) -> None:
		assert type(synced) is bool, "synced is not a bool type, it is: %r" % type(synced)
		self.__synced = synced
		return

	def __str__(self):
		string = "{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}".format(self.__feeding_id,
				time.asctime(self.__open_time), time.asctime(self.__close_time), self.__start_weight, self.__end_weight,
				self.__synced, self.__card.get_uid(), self.__card.get_name(), self.__card.get_active())
		return string

	def __repr__(self):
		return self.__str__()
