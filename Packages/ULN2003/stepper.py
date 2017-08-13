import time
import RPi.GPIO as GPIO


class Stepper:
	# We default to using pins
	# 27 - Physical 13
	# 22 - Physical 15
	# 23 - Physical 16
	# 24 - Physical 18

	__coil_a_1_pin = None
	__coil_a_2_pin = None
	__coil_b_1_pin = None
	__coil_b_2_pin = None

	__step_count = 8
	__step_seq = []
	__delay = 0.025  # In seconds

	__full_circle = 256
	__half_circle = 128
	__quarter_circle = 64

	def __init__(self, pin_a_1=27, pin_a_2=22, pin_b_1=23, pin_b_2=24, delay=0.025):
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)

		self.__coil_a_1_pin = pin_a_1
		self.__coil_a_2_pin = pin_a_2
		self.__coil_b_1_pin = pin_b_1
		self.__coil_b_2_pin = pin_b_2
		GPIO.setup(self.__coil_a_1_pin, GPIO.OUT)
		GPIO.setup(self.__coil_a_2_pin, GPIO.OUT)
		GPIO.setup(self.__coil_b_1_pin, GPIO.OUT)
		GPIO.setup(self.__coil_b_2_pin, GPIO.OUT)

		self.__step_seq.insert(0, [1, 0, 0, 0])
		self.__step_seq.insert(1, [0, 1, 0, 0])
		self.__step_seq.insert(2, [0, 0, 1, 0])
		self.__step_seq.insert(3, [0, 0, 0, 1])
		self.__step_seq.insert(4, [1, 0, 0, 0])
		self.__step_seq.insert(5, [0, 1, 0, 0])
		self.__step_seq.insert(6, [0, 0, 1, 0])
		self.__step_seq.insert(7, [0, 0, 0, 1])

		self.__delay = delay
		self.set_circle(256)

	def __del__(self):
		# TODO
		# Proper cleanup
		GPIO.cleanup()

	def set_step(self, w1, w2, w3, w4):
		GPIO.output(self.__coil_a_1_pin, w1)
		GPIO.output(self.__coil_a_2_pin, w2)
		GPIO.output(self.__coil_b_1_pin, w3)
		GPIO.output(self.__coil_b_2_pin, w4)

	def stop(self):
		GPIO.output(self.__coil_a_1_pin, 0)
		GPIO.output(self.__coil_a_2_pin, 0)
		GPIO.output(self.__coil_b_1_pin, 0)
		GPIO.output(self.__coil_b_2_pin, 0)

	def get_delay(self):
		return self.__delay

	def set_delay(self, delay=0.025):
		if delay < 0.025:
			delay = 0.025
		self.__delay = delay

	def step_forward(self, steps):
		for i in range(steps):
			for j in reversed(range(self.__step_count)):
				self.set_step(self.__step_seq[j][0], self.__step_seq[j][1], self.__step_seq[j][2],
							  self.__step_seq[j][3])
				time.sleep(self.__delay)
		self.__stop()

	def step_backward(self, steps):
		for i in range(steps):
			for j in reversed(range(self.__step_count)):
				self.set_step(self.__step_seq[j][3], self.__step_seq[j][2], self.__step_seq[j][1],
							  self.__step_seq[j][0])
				time.sleep(self.__delay)
		self.__stop()

	def set_circle(self, d=256):
		self.__full_circle = d
		self.__half_circle = d / 2
		self.__quarter_circle = d / 4

	def get_full_half_quarter_circle(self):
		return self.__full_circle, self.__half_circle, self.__quarter_circle

	def full_circle_forward(self):
		self.step_forward(self.__full_circle)

	def half_circle_forward(self):
		self.step_forward(self.__half_circle)

	def quarter_circle_forward(self):
		self.step_forward(self.__quarter_circle)

	def full_circle_backward(self):
		self.step_backward(self.__full_circle)

	def half_circle_backward(self):
		self.step_backward(self.__half_circle)

	def quarter_circle_backward(self):
		self.step_backward(self.__quarter_circle)
