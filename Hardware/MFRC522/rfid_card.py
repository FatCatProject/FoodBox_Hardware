from typing import Tuple, Union


class RFIDCard:
	__uid = None
	__name = None
	__active = False

	def __init__(self, uid, name=None, active=False):
		self.__set_uid(uid=uid)
		self.__set_name(name=name)
		self.__set_active(active=active)

	def __del__(self):
		del self.__uid
		del self.__name
		del self.__active

	def get_uid(self, in_hex=False):
		if in_hex:
			return self.__uid
		else:
			uid = []
			for x in self.__uid:
				uid.append(int(x, base=16))
			return tuple(uid)

	def __set_uid(self, uid):
		assert type(uid) is str, "uid is not of type str, it is %r" % type(uid)

		strlst = uid.split("-")
		assert len(strlst) == 4, "uid is malformed, uid: %r" % uid

		is_valid_numeric = True
		is_valid_hex = True
		for x in strlst:
			is_valid_numeric = is_valid_numeric and x.isnumeric() and 0 <= int(x) <= 255
		for x in strlst:
			try:
				tmphex = int(x, base=16)
			except Exception as e:
				is_valid_hex = False
				break
			is_valid_hex = is_valid_hex and int(hex(0), base=16) <= int(hex(tmphex), base=16) <= int(hex(255), base=16)
			if not is_valid_hex:
				break

		assert is_valid_numeric or is_valid_hex, "uid is not a valid decimal or hexadecimal uid string, uid: %r" % uid

		if is_valid_numeric:
			self.__uid = (hex(int(strlst[0], base=10)), hex(int(strlst[1], base=10)), hex(int(strlst[2], base=10)),
						  hex(int(strlst[3], base=10)))
		else:
			self.__uid = (hex(int(strlst[0], base=16)), hex(int(strlst[1], base=16)), hex(int(strlst[2], base=16)),
						  hex(int(strlst[3], base=16)))
		return

	def get_name(self):
		return self.__name

	def __set_name(self, name):
		self.__name = str(name)
		return

	def get_active(self):
		return self.__active

	def __set_active(self, active):
		assert type(active) is bool, "active is not bool type, it is %r" % type(active)
		self.__active = active
		return

	def __str__(self):
		string = str(int(self.__uid[0], base=16)) + "-" + str(
			int(self.__uid[1], base=16)) + "-" + str(int(self.__uid[2], base=16)) + "-" + str(
			int(self.__uid[3], base=16))

		if self.__name is not None:
			string += ", " + self.__name
		return string

	def __repr__(self):
		return self.__str__()

	@staticmethod
	def check_uid(uid: str) -> Tuple[bool, Union[str, None]]:
		if type(uid) is not str:
			return False

		strlst = uid.split("-")
		if len(strlst) != 4:
			return False

		is_valid_numeric: bool = True
		is_valid_hex: bool = True

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
			return False

		if is_valid_numeric:
			return_string = strlst[0] + "-" + strlst[1] + "-" + strlst[2] + "-" + strlst[3]
		else:
			return_string = str(int(strlst[0], base=16)) + "-" + str(int(strlst[0], base=16)) + "-" + str(
				int(strlst[0], base=16)) + "-" + str(int(strlst[0], base=16))

		return is_valid_numeric or is_valid_hex, return_string
