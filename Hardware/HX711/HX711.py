#!/usr/bin/python3
# Development for reading sparkfun HX711 load cell amp
# Using Richard-Major's work
# https://gist.github.com/Richard-Major/64e94338c2d08eb1221c2eca9e014362
import RPi.GPIO as GPIO


# fatcat1
# fatcat2 OFFSET = -96096, SCALE=925
# fatcat3


class HX711:
	def __init__(self, dout=4, pd_sck=18, gain=128, readBits=24, offset=-96096, scale=925):
		self.PD_SCK = pd_sck
		self.DOUT = dout
		self.readBits = readBits
		self.twosComplementOffset = 1 << readBits
		self.twosComplementCheck = self.twosComplementOffset >> 1

		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.PD_SCK, GPIO.OUT)
		GPIO.setup(self.DOUT, GPIO.IN)

		self.GAIN = 0
		self.set_offset(offset)
		self.set_scale(scale)
		self.lastVal = 0

		self.set_gain(gain)

	def __del__(self):
		GPIO.setup(self.PD_SCK, GPIO.IN)
		GPIO.setup(self.DOUT, GPIO.IN)

	def is_ready(self):
		return GPIO.input(self.DOUT) == 0

	def set_gain(self, gain):
		if gain is 128:
			self.GAIN = 1
		elif gain is 64:
			self.GAIN = 3
		elif gain is 32:
			self.GAIN = 2

		GPIO.output(self.PD_SCK, False)
		self.read()

	def waitForReady(self):
		while not self.is_ready():
			pass

	def setChannelGainFactor(self):
		for i in range(self.GAIN):
			GPIO.output(self.PD_SCK, True)
			GPIO.output(self.PD_SCK, False)

	def correctForTwosComplement(self, unsignedValue):
		if unsignedValue >= self.twosComplementCheck:
			return -self.twosComplementOffset + unsignedValue
		else:
			return unsignedValue

	def read(self):
		self.waitForReady()
		unsignedValue = 0

		for i in range(0, self.readBits):
			GPIO.output(self.PD_SCK, True)
			unsignedValue = unsignedValue << 1
			GPIO.output(self.PD_SCK, False)
			bit = GPIO.input(self.DOUT)
			if (bit):
				unsignedValue = unsignedValue | 1

		self.setChannelGainFactor()
		signedValue = self.correctForTwosComplement(unsignedValue)

		self.lastVal = signedValue
		return self.lastVal

	def read_average(self, times=3):
		sum = 0
		for i in range(times):
			sum += self.read()

		return sum / times

	def get_value(self, times=3):
		return self.read_average(times) - self.OFFSET

	def get_units(self, times=3):
		return self.get_value(times) / self.SCALE

	def tare(self, times=15):
		sum = self.read_average(times)
		self.set_offset(sum)

	def set_scale(self, scale):
		if scale == 0:
			scale = 1
		self.SCALE = scale

	def set_offset(self, offset):
		self.OFFSET = offset

	def power_down(self):
		GPIO.output(self.PD_SCK, False)
		GPIO.output(self.PD_SCK, True)

	def power_up(self):
		GPIO.output(self.PD_SCK, False)
