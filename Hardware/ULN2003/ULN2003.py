import time
import RPi.GPIO as GPIO


class ULN2003:
	# We default to using these pins
	# BCM27 - Physical 13 - IN1
	# BCM22 - Physical 15 - IN2
	# BCM23 - Physical 16 - IN3
	# BCM24 - Physical 18 - IN4

	__coil_a_1_pin = None
	__coil_a_2_pin = None
	__coil_b_1_pin = None
	__coil_b_2_pin = None

	__step_count = 8
	__step_seq = []
	__delay = 0.025  # In seconds

	__full_rotation = 0
	__half_rotation = 0
	__quarter_rotation = 0

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

		# Change the sequence to half-step 64 steps per full rotation (Assuming it works correctly ¯\_('_')_/¯ )
		self.__step_seq.insert(0, [0, 0, 0, 1])
		self.__step_seq.insert(1, [0, 0, 1, 1])
		self.__step_seq.insert(2, [0, 0, 1, 0])
		self.__step_seq.insert(3, [0, 1, 1, 0])
		self.__step_seq.insert(4, [0, 1, 0, 0])
		self.__step_seq.insert(5, [1, 1, 0, 0])
		self.__step_seq.insert(6, [1, 0, 0, 0])
		self.__step_seq.insert(7, [1, 0, 0, 1])
		# self.__step_seq.reverse()

		self.set_delay(delay=delay)
		self.set_circle(d=512)

	def __del__(self):
		self.stop()
		GPIO.output(self.__coil_a_1_pin, GPIO.LOW)
		GPIO.output(self.__coil_a_2_pin, GPIO.LOW)
		GPIO.output(self.__coil_b_1_pin, GPIO.LOW)
		GPIO.output(self.__coil_b_2_pin, GPIO.LOW)
		GPIO.setup(self.__coil_a_1_pin, GPIO.IN)
		GPIO.setup(self.__coil_a_2_pin, GPIO.IN)
		GPIO.setup(self.__coil_b_1_pin, GPIO.IN)
		GPIO.setup(self.__coil_b_2_pin, GPIO.IN)

	def set_step(self, w1, w2, w3, w4):
		GPIO.output(self.__coil_a_1_pin, w1)
		GPIO.output(self.__coil_a_2_pin, w2)
		GPIO.output(self.__coil_b_1_pin, w3)
		GPIO.output(self.__coil_b_2_pin, w4)

	def stop(self):
		GPIO.output(self.__coil_a_1_pin, GPIO.LOW)
		GPIO.output(self.__coil_a_2_pin, GPIO.LOW)
		GPIO.output(self.__coil_b_1_pin, GPIO.LOW)
		GPIO.output(self.__coil_b_2_pin, GPIO.LOW)

	def get_delay(self):
		return self.__delay

	def set_delay(self, delay=0.025):
		if delay < 0.025:
			delay = 0.025
		self.__delay = delay

	def step_forward(self, steps):
		for i in range(steps):
			for j in range(0, self.__step_count):
				pin1 = self.__step_seq[j][0]
				pin2 = self.__step_seq[j][1]
				pin3 = self.__step_seq[j][2]
				pin4 = self.__step_seq[j][3]
				self.set_step(w1=pin1, w2=pin2, w3=pin3, w4=pin4)
				time.sleep(self.__delay)
		self.stop()

	def step_backward(self, steps):
		for i in range(steps):
			for j in reversed(range(0, self.__step_count)):
				pin1 = self.__step_seq[j][0]
				pin2 = self.__step_seq[j][1]
				pin3 = self.__step_seq[j][2]
				pin4 = self.__step_seq[j][3]
				self.set_step(w1=pin1, w2=pin2, w3=pin3, w4=pin4)
				time.sleep(self.__delay)
		self.stop()

	def set_circle(self, d=512):
		self.__full_rotation = int(d)
		self.__half_rotation = int(d / 2)
		self.__quarter_rotation = int(d / 4)

	def get_full_half_quarter_rotation(self):
		return self.__full_rotation, self.__half_rotation, self.__quarter_rotation

	def full_rotation_forward(self):
		self.step_forward(steps=self.__full_rotation)

	def half_rotation_forward(self):
		self.step_forward(steps=self.__half_rotation)

	def quarter_rotation_forward(self):
		self.step_forward(steps=self.__quarter_rotation)

	def full_rotation_backward(self):
		self.step_backward(steps=self.__full_rotation)

	def half_rotation_backward(self):
		self.step_backward(steps=self.__half_rotation)

	def quarter_rotation_backward(self):
		self.step_backward(steps=self.__quarter_rotation)
