
from collections import namedtuple

MemItem = namedtuple("MemItem", ["address", "name", "size", "default_value", "direction", "is_eprom", "is_readonly", "min", "max"])

STSMemConfig = [
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
    MemItem(56, "Present Position", 2, 0, 15, False, True, -1, -1),
    MemItem(58, "Present Velocity", 2, 0, 15, False, True, -1, -1),
    MemItem(60, "Present PWM", 2, 0, 10, False, True, -1, -1),
    MemItem(62, "Present Input Voltage", 1, 0, -1, False, True, -1, -1),
    MemItem(63, "Present Temperature", 1, 0, -1, False, True, -1, -1),
    MemItem(64, "Sync Write Flag", 1, 0, -1, False, True, -1, -1),
    MemItem(65, "Hardware Error Status", 1, 0, -1, False, True, -1, -1),
    MemItem(66, "Moving Status", 1, 0, -1, False, True, -1, -1),
    MemItem(69, "Present Current", 2, 0, 15, False, True, -1, -1),
]

SCSMemConfig = [
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
    MemItem(56, "Present Position", 2, 0, 15, False, True, -1, -1),
    MemItem(58, "Present Velocity", 2, 0, 15, False, True, -1, -1),
    MemItem(60, "Present PWM", 2, 0, 10, False, True, -1, -1),
    MemItem(62, "Present Input Voltage", 1, 0, -1, False, True, -1, -1),
    MemItem(63, "Present Temperature", 1, 0, -1, False, True, -1, -1),
    MemItem(64, "Sync Write Flag", 1, 0, -1, False, True, -1, -1),
    MemItem(65, "Hardware Error Status", 1, 0, -1, False, True, -1, -1),
    MemItem(66, "Moving Status", 1, 0, -1, False, True, -1, -1),
]


def getModelType(mid):
	if mid == 1:
		return "XXX"
	return None

def getModelSeries(name):
	return "STS"

class Servo:
	def __init__(self):
		self.model_ = None
		self.id_ = -1
	
