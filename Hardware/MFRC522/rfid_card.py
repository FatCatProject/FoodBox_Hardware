class RFIDCard:
	__uid = None
	__name = None
	__active = False

	def __init__(self, uid, name=None, active=False):
		self.set_uid(uid=uid)
		self.set_name(name=name)
		self.set_active(active=active)

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

	def set_uid(self, uid):
		if not type(uid) is str:
			# TODO - Write a fatal error to the log and throw an exception
			return
		strlst = uid.split("-")
		if len(strlst) != 4:
			# TODO - Write a fatal error to the log and throw an exception
			return
		isvalidnumeric = True
		isvalidhex = True
		for x in strlst:
			isvalidnumeric = isvalidnumeric and x.isumeric() and 0 <= int(x) <= 255
		for x in strlst:
			try:
				tmphex = int(x, base=16)
			except:
				isvalidhex = False
				break
			isvalidhex = isvalidhex and int(hex(0), base=16) <= int(hex(tmphex), base=16) <= int(hex(255), base=16)
			if not isvalidhex:
				break

		if not (isvalidnumeric or isvalidhex):
			# TODO - Write a fatal error to the log and throw an exception
			return

		if isvalidnumeric:
			self.__uid = (hex(int(strlst[0], base=10)), hex(int(strlst[1], base=10)), hex(int(strlst[2], base=10)),
						  hex(int(strlst[3], base=10)))
		else:
			self.__uid = (hex(int(strlst[0], base=16)), hex(int(strlst[1], base=16)), hex(int(strlst[2], base=16)),
						  hex(int(strlst[3], base=16)))
		return

	def get_name(self):
		return self.__name

	def set_name(self, name):
		self.__name = str(name)
		return

	def get_active(self):
		return self.__active

	def set_active(self, active):
		if not type(active) is bool:
			# TODO - Write a fatal error to the log and throw an exception
			return
		self.__active = active
		return

	def __str__(self):
		string = self.__uid[0] + "-" + self.__uid[1] + "-" + self.__uid[2] + "-" + self.__uid[3]

		if self.__name is not None:
			string += ", " + self.__name
		return string

	def __repr__(self):
		return self.__str__()
