from typing import Tuple
from typing import Union


class RFIDCard:
	__uid = None  # type: str  # The uid is in a format of 255-(x5), where each section is in a range of 000-255.
	__name = None  # type: Union[str, None]
	__active = False  # type: bool

	def __init__(self, uid: str, name: Union[str, None] = None, active: bool = False) -> None:
		self.__set_uid(uid=uid)
		self.__set_name(name=name or uid)
		self.__set_active(active=active)

	def __del__(self):
		del self.__uid
		del self.__name
		del self.__active

	def get_uid(self) -> str:
		return self.__uid

	def __set_uid(self, uid: str) -> None:
		is_valid_uid, uid = self.check_uid(uid)
		assert is_valid_uid, "uid is not a valid uid: %r" % uid
		self.__uid = uid
		return

	def get_name(self) -> Union[str, None]:
		return self.__name

	def __set_name(self, name: Union[str, None]) -> None:
		self.__name = str(name)
		return

	def get_active(self) -> bool:
		return self.__active

	def __set_active(self, active: bool) -> None:
		assert type(active) is bool, "active is not bool type, it is %r" % type(active)
		self.__active = active
		return

	def __str__(self):
		string = self.__uid  #str(int(self.__uid[0], base=16)) + "-" + str(int(self.__uid[1], base=16)) + "-" + str(
				#int(self.__uid[2], base=16)) + "-" + str(int(self.__uid[3], base=16))

		if self.__name is not None:
			string += ", " + self.__name

		string += ", " + str(self.__active)
		return string

	def __repr__(self):
		return self.__str__()

	@staticmethod
	def check_uid(uid: str) -> Tuple[bool, Union[str, None]]:
		if type(uid) is not str:
			return False, None

		strlst = uid.split("-")
		if len(strlst) != 5: #changed from 4 to 5
			return False, None

		is_valid_numeric = True  # type: bool
		is_valid_hex = True  # type: bool

		for x in strlst:
			is_valid_numeric = is_valid_numeric and x.isnumeric() and 0 <= int(x) <= 255
			if not is_valid_numeric:
				break

		for x in strlst:
			try:
				tmphex = int(x, base=16)
			except Exception as e:
				is_valid_hex = False
				break
			is_valid_hex = is_valid_hex and int(hex(0), base=16) <= int(hex(tmphex), base=16) <= int(hex(255), base=16)
			if not is_valid_hex:
				break

		if not (is_valid_numeric or is_valid_hex):
			return False, None

		if is_valid_numeric:
			return_string = strlst[0] + "-" + strlst[1] + "-" + strlst[2] + "-" + strlst[3] + "-" + strlst[4]
		else:
			return_string = str(int(strlst[0], base=16)) + "-" + str(int(strlst[0], base=16)) + "-" + str(
					int(strlst[0], base=16)) + "-" + str(int(strlst[0], base=16))+ "-" + str(int(strlst[0], base=16))

		return is_valid_numeric or is_valid_hex, return_string
