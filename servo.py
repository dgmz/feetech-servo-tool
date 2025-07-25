
from collections import namedtuple

MemItem = namedtuple("MemItem", ["address", "name", "size", "default_value", "direction", "is_eprom", "is_readonly", "min", "max"])

MemConfig = {
	"STS": [
		# address, name, size, default_value, direction, eprom, readonly, min, max 
		MemItem(0, "Firmare Main Version NO.", 1, 0, -1, True, True, -1, -1),
		MemItem(1, "Firmware Secondary Version NO.", 1, 0, -1, True, True, -1, -1),
		MemItem(3, "Servo Main Version", 1, 0, -1, True, True, -1, -1),
		MemItem(4, "Servo Sub Version", 1, 0, -1, True, True, -1, -1),
		MemItem(5, "ID", 1, 0, -1, True, False, 0, 253),
		MemItem(6, "Baud Rate", 1, 4, -1, True, False, 0, 7),
		MemItem(7, "Return Delay Time", 1, 250, -1, True, False, 0, 254),
		MemItem(8, "Status Return Level", 1, 1, -1, True, False, 0, 1),
		MemItem(9, "Min Position Limit", 2, 0, 15, True, False, -1, -1),
		MemItem(11, "Max Position Limit", 2, 0, 15, True, False, -1, -1),
		MemItem(13, "Max Temperature limit", 1, 80, -1, True, False, 0, 100),
		MemItem(14, "Max Input Voltage", 1, 140, -1, True, False, 0, 254),
		MemItem(15, "Min Input Voltage", 1, 80, -1, True, False, 0, 254),
		MemItem(16, "Max Torque Limit", 2, 1000, -1, True, False, 0, 1000),
		MemItem(18, "Setting Byte", 1, 0, -1, True, False, 0, 254),
		MemItem(19, "Protection Switch", 1, 37, -1, True, False, 0, 254),
		MemItem(20, "LED Alarm Condition", 1, 37, -1, True, False, 0, 254),
		MemItem(21, "Position P Gain", 1, 32, -1, True, False, 0, 254),
		MemItem(22, "Position D Gain", 1, 0, -1, True, False, 0, 254),
		MemItem(23, "Position I Gain", 1, 0, -1, True, False, 0, 254),
		MemItem(24, "Punch", 2, 0, -1, True, False, 0, 1000),
		MemItem(26, "CW Dead Band", 1, 0, -1, True, False, 0, 32),
		MemItem(27, "CCW Dead Band", 1, 0, -1, True, False, 0, 32),
		MemItem(28, "Overload Current", 2, 0, -1, True, False, 0, 511),
		MemItem(30, "Angular Resolution", 1, 1, -1, True, False, 1, 100),
		MemItem(31, "Position Offset Value", 2, 0, 15, True, False, -2047, 2047),
		MemItem(33, "Work Mode", 1, 0, -1, True, False, 0, 3),
		MemItem(34, "Protect Torque", 1, 40, -1, True, False, 0, 254),
		MemItem(35, "Overload Protection Time", 1, 80, -1, True, False, 0, 254),
		MemItem(36, "Overload Torque", 1, 80, -1, True, False, 0, 254),
		MemItem(37, "Velocity P Gain", 1, 32, -1, True, False, 0, 254),
		MemItem(38, "Overcurrent Protection Time", 1, 100, -1, True, False, 0, 254),
		MemItem(39, "Velocity I Gain", 1, 0, -1, True, False, 0, 254),
		MemItem(40, "Torque Enable", 1, 0, -1, False, False, 0, 254),
		MemItem(41, "Goal  Acceleration", 1, 0, -1, False, False, 0, 254),
		MemItem(42, "Goal Position", 2, 0, 15, False, False, -32766, 32766),
		MemItem(46, "Goal  Velocity", 2, 0, 15, False, False, -1000, 1000),
		MemItem(48, "Torque Limit", 2, 1000, -1, False, False, 0, 1000),
		MemItem(55, "Lock", 1, 1, -1, False, False, 0, 1),
		MemItem(56, "Current Position", 2, 0, 15, False, True, -1, -1),
		MemItem(58, "Instantaneous Velocity", 2, 0, 15, False, True, -1, -1),
		MemItem(60, "Current PWM", 2, 0, 10, False, True, -1, -1),
		MemItem(62, "Instantaneous Input Voltage", 1, 0, -1, False, True, -1, -1),
		MemItem(63, "Current Temperature", 1, 0, -1, False, True, -1, -1),
		MemItem(64, "Sync Write Flag", 1, 0, -1, False, True, -1, -1),
		MemItem(65, "Hardware Error Status", 1, 0, -1, False, True, -1, -1),
		MemItem(66, "Moving Status", 1, 0, -1, False, True, -1, -1),
		MemItem(69, "Instantaneous Current", 2, 0, 15, False, True, -1, -1)
	],
	"SCS": [
		# address, name, size, default value, direction, eprom, readonly, min, max 
		MemItem(0, "Firmare Main Version NO.", 1, 0, -1, True, True, -1, -1),
		MemItem(1, "Firmware Secondary Version NO.", 1, 0, -1, True, True, -1, -1),
		MemItem(3, "Servo Main Version", 1, 0, -1, True, True, -1, -1),
		MemItem(4, "Servo Sub Version", 1, 0, -1, True, True, -1, -1),
		MemItem(5, "ID", 1, 0, -1, True, False, 0, 253),
		MemItem(6, "Baud Rate", 1, 4, -1, True, False, 0, 10),
		MemItem(7, "Return Delay Time", 1, 250, -1, True, False, 0, 254),
		MemItem(8, "Status Return Level", 1, 1, -1, True, False, 0, 1),
		MemItem(9, "Min Position Limit", 2, 0, 15, True, False, 0, 1023),
		MemItem(11, "Max Position Limit", 2, 0, 15, True, False, 0, 1023),
		MemItem(13, "Max Temperature limit", 1, 80, -1, True, False, 0, 100),
		MemItem(14, "Max Input Voltage", 1, 140, -1, True, False, 0, 254),
		MemItem(15, "Min Input Voltage", 1, 80, -1, True, False, 0, 254),
		MemItem(16, "Max Torque Limit", 2, 1000, -1, True, False, 0, 1000),
		MemItem(19, "Protection Switch", 1, 37, -1, True, False, 0, 254),
		MemItem(20, "LED Alarm Condition", 1, 37, -1, True, False, 0, 254),
		MemItem(21, "Position P Gain", 1, 32, -1, True, False, 0, 254),
		MemItem(22, "Position D Gain", 1, 0, -1, True, False, 0, 254),
		MemItem(23, "Position I Gain", 1, 0, -1, True, False, 0, 254),
		MemItem(24, "Punch", 2, 0, -1, True, False, 0, 1000),
		MemItem(26, "CW Dead Band", 1, 2, -1, True, False, 0, 32),
		MemItem(27, "CCW Dead Band", 1, 2, -1, True, False, 0, 32),
		MemItem(37, "Protect Torque", 1, 40, -1, True, False, 0, 254),
		MemItem(38, "Overload Protection Time", 1, 80, -1, True, False, 0, 254),
		MemItem(39, "Overload Torque", 1, 80, -1, True, False, 0, 254),
		MemItem(40, "Torque Enable", 1, 0, -1, False, False, 0, 2),
		MemItem(42, "Goal Position", 2, 0, -1, False, False, 0, 1023),
		MemItem(44, "Running Time", 2, 0, 15, False, False, -32766, 32766),
		MemItem(46, "Goal  Velocity", 2, 0, -1, False, False, 0, 32766),
		MemItem(48, "Lock", 1, 1, -1, False, False, 0, 1),
		MemItem(56, "Current Position", 2, 0, 15, False, True, -1, -1),
		MemItem(58, "Instantaneous Velocity", 2, 0, 15, False, True, -1, -1),
		MemItem(60, "Current PWM", 2, 0, 10, False, True, -1, -1),
		MemItem(62, "Instantaneous Input Voltage", 1, 0, -1, False, True, -1, -1),
		MemItem(63, "Current Temperature", 1, 0, -1, False, True, -1, -1),
		MemItem(64, "Sync Write Flag", 1, 0, -1, False, True, -1, -1),
		MemItem(65, "Hardware Error Status", 1, 0, -1, False, True, -1, -1),
		MemItem(66, "Moving Status", 1, 0, -1, False, True, -1, -1)
	],
	"SMCL": [
		# address, name, size, default_value, direction, eprom, readonly, min, max 
		MemItem(0, "Firmare Main Version NO.", 1, 0, -1, True, True, -1, -1),
		MemItem(1, "Firmware Secondary Version NO.", 1, 0, -1, True, True, -1, -1),
		MemItem(3, "Servo Main Version", 1, 0, -1, True, True, -1, -1),
		MemItem(4, "Servo Sub Version", 1, 0, -1, True, True, -1, -1),
		MemItem(5, "ID", 1, 0, -1, True, False, 0, 253),
		MemItem(6, "Baud Rate", 1, 4, -1, True, False, 0, 254),
		MemItem(7, "Return Delay Time", 1, 250, -1, True, False, 0, 254),
		MemItem(8, "Status Return Level", 1, 1, -1, True, False, 0, 1),
		MemItem(9, "Min Position Limit", 2, 0, 15, True, False, -1, -1),
		MemItem(11, "Max Position Limit", 2, 0, 15, True, False, -1, -1),
		MemItem(13, "Max Temperature limit", 1, 80, -1, True, False, 0, 100),
		MemItem(14, "Max Input Voltage", 1, 140, -1, True, False, 0, 254),
		MemItem(15, "Min Input Voltage", 1, 80, -1, True, False, 0, 254),
		MemItem(16, "Max Torque Limit", 2, 1000, -1, True, False, 0, 1000),
		MemItem(18, "Setting Byte", 1, 0, -1, True, False, 0, 254),
		MemItem(19, "Protection Switch", 1, 37, -1, True, False, 0, 254),
		MemItem(20, "LED Alarm Condition", 1, 37, -1, True, False, 0, 254),
		MemItem(21, "Position P Gain", 1, 32, -1, True, False, 0, 254),
		MemItem(22, "Position D Gain", 1, 0, -1, True, False, 0, 254),
		MemItem(23, "Position I Gain", 1, 0, -1, True, False, 0, 254),
		MemItem(24, "Punch", 2, 0, -1, True, False, 0, 1000),
		MemItem(26, "CW Dead Band", 1, 0, -1, True, False, 0, 32),
		MemItem(27, "CCW Dead Band", 1, 0, -1, True, False, 0, 32),
		MemItem(28, "Overload Current", 2, 0, -1, True, False, 0, 1023),
		MemItem(33, "Position Offset Value", 2, 0, 15, True, False, -2047, 2047),
		MemItem(35, "Work Mode", 1, 0, -1, True, False, 0, 2),
		MemItem(36, "Overcurrent Protection Time", 1, 100, -1, True, False, 0, 254),
		MemItem(37, "Protect Torque", 1, 40, -1, True, False, 0, 254),
		MemItem(38, "Overload Protection Time", 1, 80, -1, True, False, 0, 254),
		MemItem(39, "Overload Torque", 1, 80, -1, True, False, 0, 254),
		MemItem(40, "Torque Enable", 1, 0, -1, False, False, 0, 254),
		MemItem(41, "Goal  Acceleration", 1, 0, -1, False, False, 0, 254),
		MemItem(42, "Goal Position", 2, 0, -1, False, False, -32766, 32766),
		MemItem(44, "Running Time", 2, 0, 15, False, False, -32766, 32766),
		MemItem(46, "Goal  Velocity", 2, 0, 15, False, False, 0, 32766),
		MemItem(48, "Lock", 1, 1, -1, False, False, 0, 1),
		MemItem(56, "Current Position", 2, 0, 15, False, True, -1, -1),
		MemItem(58, "Instantaneous Velocity", 2, 0, 15, False, True, -1, -1),
		MemItem(60, "Current PWM", 2, 0, 10, False, True, -1, -1),
		MemItem(62, "Instantaneous Input Voltage", 1, 0, -1, False, True, -1, -1),
		MemItem(63, "Current Temperature", 1, 0, -1, False, True, -1, -1),
		MemItem(64, "Sync Write Flag", 1, 0, -1, False, True, -1, -1),
		MemItem(65, "Hardware Error Status", 1, 0, -1, False, True, -1, -1),
		MemItem(66, "Moving Status", 1, 0, -1, False, True, -1, -1),
		MemItem(69, "Instantaneous Current", 2, 0, 15, False, True, -1, -1)
	],
	"SMBL": [
		# address, name, size, default_value, direction, eprom, readonly, min, max 
		MemItem(0, "Firmare Main Version NO.", 1, 0, -1, True, True, -1, -1),
		MemItem(1, "Firmware Secondary Version NO.", 1, 0, -1, True, True, -1, -1),
		MemItem(3, "Servo Main Version", 1, 0, -1, True, True, -1, -1),
		MemItem(4, "Servo Sub Version", 1, 0, -1, True, True, -1, -1),
		MemItem(5, "ID", 1, 0, -1, True, False, 0, 253),
		MemItem(6, "Baud Rate", 1, 4, -1, True, False, 0, 11),
		MemItem(7, "Return Delay Time", 1, 250, -1, True, False, 0, 254),
		MemItem(8, "Status Return Level", 1, 1, -1, True, False, 0, 1),
		MemItem(9, "Min Position Limit", 2, 0, 15, True, False, -1, -1),
		MemItem(11, "Max Position Limit", 2, 0, 15, True, False, -1, -1),
		MemItem(13, "Max Temperature limit", 1, 80, -1, True, False, 0, 100),
		MemItem(14, "Max Input Voltage", 1, 140, -1, True, False, 0, 254),
		MemItem(15, "Min Input Voltage", 1, 80, -1, True, False, 0, 254),
		MemItem(16, "Max Torque Limit", 2, 1000, -1, True, False, 0, 1000),
		MemItem(18, "Setting Byte", 1, 0, -1, True, False, 0, 254),
		MemItem(19, "Protection Switch", 1, 37, -1, True, False, 0, 254),
		MemItem(20, "LED Alarm Condition", 1, 37, -1, True, False, 0, 254),
		MemItem(21, "Position P Gain", 1, 32, -1, True, False, 0, 254),
		MemItem(22, "Position D Gain", 1, 0, -1, True, False, 0, 254),
		MemItem(23, "Position I Gain", 1, 0, -1, True, False, 0, 254),
		MemItem(24, "Punch", 2, 0, -1, True, False, 0, 1000),
		MemItem(26, "CW Dead Band", 1, 0, -1, True, False, 0, 32),
		MemItem(27, "CCW Dead Band", 1, 0, -1, True, False, 0, 32),
		MemItem(28, "Overload Current", 2, 0, -1, True, False, 0, 511),
		MemItem(30, "Angular Resolution", 1, 1, -1, True, False, 1, 100),
		MemItem(31, "Position Offset Value", 2, 0, 15, True, False, -2047, 2047),
		MemItem(33, "Work Mode", 1, 0, -1, True, False, 0, 2),
		MemItem(34, "Protect Torque", 1, 40, -1, True, False, 0, 254),
		MemItem(35, "Overload Protection Time", 1, 80, -1, True, False, 0, 254),
		MemItem(36, "Overload Torque", 1, 80, -1, True, False, 0, 254),
		MemItem(37, "Velocity P Gain", 1, 32, -1, True, False, 0, 254),
		MemItem(38, "Overcurrent Protection Time", 1, 100, -1, True, False, 0, 254),
		MemItem(39, "Velocity I Gain", 1, 0, -1, True, False, 0, 254),
		MemItem(40, "Torque Enable", 1, 0, -1, False, False, 0, 254),
		MemItem(41, "Goal  Acceleration", 1, 0, -1, False, False, 0, 254),
		MemItem(42, "Goal Position", 2, 0, 15, False, False, -32766, 32766),
		MemItem(44, "Running Time", 2, 0, 10, False, False, -32766, 32766),
		MemItem(46, "Goal  Velocity", 2, 0, 15, False, False, -32766, 32766),
		MemItem(48, "Torque Limit", 2, 1000, -1, False, False, 0, 1000),
		MemItem(55, "Lock", 1, 1, -1, False, False, 0, 1),
		MemItem(56, "Current Position", 2, 0, 15, False, True, -1, -1),
		MemItem(58, "Instantaneous Velocity", 2, 0, 15, False, True, -1, -1),
		MemItem(60, "Current PWM", 2, 0, 10, False, True, -1, -1),
		MemItem(62, "Instantaneous Input Voltage", 1, 0, -1, False, True, -1, -1),
		MemItem(63, "Current Temperature", 1, 0, -1, False, True, -1, -1),
		MemItem(64, "Sync Write Flag", 1, 0, -1, False, True, -1, -1),
		MemItem(65, "Hardware Error Status", 1, 0, -1, False, True, -1, -1),
		MemItem(66, "Moving Status", 1, 0, -1, False, True, -1, -1),
		MemItem(69, "Instantaneous Current", 2, 0, 15, False, True, -1, -1)
	]
}

def SERVO_MODEL(a,b):
	return (b << 8) + a

ServoModels = {
	SERVO_MODEL(5, 0): "SCSXX",
	SERVO_MODEL(5, 4): "SCS009",
	SERVO_MODEL(5, 8): "SCS2332",
	SERVO_MODEL(5, 12): "SCS45",
	SERVO_MODEL(5, 15): "SCS15",
	SERVO_MODEL(5, 16): "SCS315",
	SERVO_MODEL(5, 25): "SCS115",
	SERVO_MODEL(5, 35): "SCS215",
	SERVO_MODEL(5, 40): "SCS40",
	SERVO_MODEL(5, 60): "SCS6560",
	SERVO_MODEL(5, 240): "SCDZZ",
	SERVO_MODEL(6, 0): "SMXX-360M",
	SERVO_MODEL(6, 3): "SM30-360M",
	SERVO_MODEL(6, 8): "SM60-360M",
	SERVO_MODEL(6, 12): "SM80-360M",
	SERVO_MODEL(6, 16): "SM100-360M",
	SERVO_MODEL(6, 20): "SM150-360M",
	SERVO_MODEL(6, 24): "SM85-360M",
	SERVO_MODEL(6, 26): "SM60-360M",
	SERVO_MODEL(8, 0): "SM30BL",
	SERVO_MODEL(8, 1): "SM30BL",
	SERVO_MODEL(8, 2): "SM30BL",
	SERVO_MODEL(8, 3): "SM30BL",
	SERVO_MODEL(8, 4): "SM30BL",
	SERVO_MODEL(8, 5): "SM30BL",
	SERVO_MODEL(8, 6): "SM30BL",
	SERVO_MODEL(8, 7): "SM30BL",
	SERVO_MODEL(8, 8): "SM30BL",
	SERVO_MODEL(8, 9): "SM30BL",
	SERVO_MODEL(8, 10): "SM30BL",
	SERVO_MODEL(8, 11): "SM30BL",
	SERVO_MODEL(8, 12): "SM30BL",
	SERVO_MODEL(8, 13): "SM30BL",
	SERVO_MODEL(8, 14): "SM30BL",
	SERVO_MODEL(8, 15): "SM30BL",
	SERVO_MODEL(8, 16): "SM30BL",
	SERVO_MODEL(8, 17): "SM30BL",
	SERVO_MODEL(8, 18): "SM30BL",
	SERVO_MODEL(8, 19): "SM30BL",
	SERVO_MODEL(8, 25): "SM29BL(LJ)",
	SERVO_MODEL(8, 29): "SM29BL(FT)",
	SERVO_MODEL(8, 30): "SM30BL(FT)",
	SERVO_MODEL(8, 20): "SM30BL(LJ)",
	SERVO_MODEL(8, 40): "SM40BLHV",
	SERVO_MODEL(8, 42): "SM45BLHV",
	SERVO_MODEL(8, 44): "SM85BLHV",
	SERVO_MODEL(8, 120): "SM120BLHV",
	SERVO_MODEL(8, 220): "SM200BLHV",
	SERVO_MODEL(9, 0): "STSXX",
	SERVO_MODEL(9, 2): "STS3032",
	SERVO_MODEL(9, 3): "STS3215",
	SERVO_MODEL(9, 4): "STS3040",
	SERVO_MODEL(9, 5): "STS3020",
	SERVO_MODEL(9, 6): "STS3046",
	SERVO_MODEL(9, 20): "SCSXX-2",
	SERVO_MODEL(9, 15): "SCS15-2",
	SERVO_MODEL(9, 35): "SCS225",
	SERVO_MODEL(9, 40): "SCS40-2"
}

def getModelType(mid):
	return ServoModels.get(mid, "Unknown")

def getModelSeries(name):
	return "STS" if name.startswith("STS") \
		else "SCS" if name.startswith("SC") \
		else "SMBL" if name.startswith("SM") and "BL" in name \
		else "SMCL"

class Servo:
	def __init__(self):
		self.model_ = None
		self.id_ = -1
		self.bus_ = None # FIXME
	def firstb(self, val):
		return (val >> 8) & 0xFF if self.bus_.end_ else val & 0xFF
	def secondb(self, val):
		return val & 0xFF if self.bus_.end_ else (val >> 8) & 0xFF
	def enable_torque(self, id, enable):
		return self.bus_.write_byte(id, 40, enable)
	def rotation_mode(self, id):
		return self.bus_.write_byte(id, 33, 0)
	def write_pos_ex(self, id, goal, speed, acc):
		handler = scservo_sdk.sms_sts(self.bus_.port_handler_)
		res, error = handler.WritePosEx(id, goal, speed, acc)
		return res
	def read_position(self, id):
		#return self.bus_.read_word(id, 56)
		handler = scservo_sdk.sms_sts(self.bus_.port_handler_)
		pos, res, error = handler.ReadPos(id)
		return pos
	def read_load(self, id):
		return self.bus_.read_word(id, 60)
	def read_speed(self, id):
		#return self.bus_.read_word(id, 58)
		handler = scservo_sdk.sms_sts(self.bus_.port_handler_)
		speed, res, error = handler.ReadSpeed(id)
		return speed
	def read_current(self, id):
		return self.bus_.read_word(id, 60)
	def read_temperature(self, id):
		return self.bus_.read_byte(id, 63)
	def read_voltage(self, id):
		return self.bus_.read_byte(id, 62)
	def read_move(self, id):
		return self.bus_.read_byte(id, 66)
	def read_goal(self, id):
		return self.bus_.read_word(id, 42)
