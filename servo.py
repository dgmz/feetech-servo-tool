
from collections import namedtuple
import scservo_sdk

# Register addresses for the wheel-mode and position-mode helpers.
# Addresses listed here are stable across STS, SMBL, and SMCL (same
# memory layout for the position / acc / time / velocity block).
# Naming follows the Feetech docs / MemConfig ("position" / "velocity")
# rather than the SDK's "angle" / "speed". The two registers that DO
# differ between SMCL and STS/SMBL (Work Mode, Lock) are handled via
# the per-series tables further down.
REG_MIN_POSITION_LIMIT = scservo_sdk.SMS_STS_MIN_ANGLE_LIMIT_L
REG_MAX_POSITION_LIMIT = scservo_sdk.SMS_STS_MAX_ANGLE_LIMIT_L
REG_GOAL_POSITION = scservo_sdk.SMS_STS_GOAL_POSITION_L
REG_GOAL_VELOCITY = scservo_sdk.SMS_STS_GOAL_SPEED_L

# Work Mode register values. The SDK doesn't expose named constants
# for these — its WheelMode() helper writes the literal 1. Series
# support varies: SMBL caps at 2 (no Step mode); SCS lacks the
# register entirely.
WORK_MODE_POSITION = 0
WORK_MODE_WHEEL = 1
WORK_MODE_PWM = 2
WORK_MODE_STEP = 3

# Single-turn position range defaults. Min is 0 across all series;
# max varies by series (see _POSITION_MAX_BY_SERIES further down).
POSITION_MIN = 0
DEFAULT_POSITION_MAX = 4095


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


# Per-series capability tables, keyed by series string (matching the
# values returned by getModelSeries below). These sit alongside
# MemConfig as parallel per-series data: MemConfig is per-register,
# these are per-series properties.

# Work Mode register address. STS and SMBL share the SMS_STS layout
# (reg 33); SMCL puts it at reg 35. The SMCL value is mirrored from
# MemConfig["SMCL"] and unverified against an authoritative online
# source — Feetech's FTServo_Arduino SMS_STS.h asserts reg 33 for
# SMS+STS together but its scope re: SMCL (the 360M closed-loop
# variants, model code 6 in ServoModels) is unclear. TODO: confirm
# on SMCL hardware (e.g. SM30-360M).
_REG_WORK_MODE_BY_SERIES = {
	"STS": scservo_sdk.SMS_STS_MODE,   # 33
	"SMBL": scservo_sdk.SMS_STS_MODE,  # 33
	"SMCL": 35,                        # per MemConfig["SMCL"], not SDK
}

# Lock register address. Same STS/SMBL vs SMCL split.
_REG_LOCK_BY_SERIES = {
	"STS": scservo_sdk.SMS_STS_LOCK,   # 55
	"SMBL": scservo_sdk.SMS_STS_LOCK,  # 55
	"SMCL": 48,                        # per MemConfig["SMCL"], not SDK
}

# Single-turn position max per series. Sourced from datasheets — not
# MemConfig (which tracks per-register validator ranges, not encoder
# resolution). 12-bit encoders for STS/SMBL/SMCL, 10-bit for SCS.
_POSITION_MAX_BY_SERIES = {
	"STS": 4095,
	"SMBL": 4095,
	"SMCL": 4095,
	"SCS": 1023,
}

# Goal Velocity (reg 46) max magnitude in wheel mode. Per the ST3215
# register map (Waveshare wiki / python-st3215), reg 46 accepts up to
# 3400 step/s on STS3215 with bit 15 as the direction bit
# (sign-magnitude). SMBL's authoritative max isn't in the sources
# consulted; the STS value is used as a conservative shared cap. Keys
# also define which series have wheel-mode support in this tool — SCS
# has no Work Mode register and SMCL puts it at a different address
# that this tool doesn't wire up for wheel mode.
_VELOCITY_MAX_BY_SERIES = {
	"STS": 3400,
	"SMBL": 3400,
}
WHEEL_MODE_SUPPORTED_SERIES = tuple(_VELOCITY_MAX_BY_SERIES.keys())


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


def reg_work_mode_for_series(series):
	return _REG_WORK_MODE_BY_SERIES.get(series)


def reg_lock_for_series(series):
	return _REG_LOCK_BY_SERIES.get(series)


def position_max_for_series(series):
	return _POSITION_MAX_BY_SERIES.get(series, DEFAULT_POSITION_MAX)


def velocity_max_for_series(series):
	# Falls back to a conservative cap for any unrecognised series;
	# wheel-mode UI is gated on WHEEL_MODE_SUPPORTED_SERIES so this
	# fallback isn't hit in practice.
	return _VELOCITY_MAX_BY_SERIES.get(series, 1000)


class Servo:

	def __init__(self, bus):
		self.model_ = None
		self.id_ = -1
		self.bus_ = bus


	def firstb(self, val):
		return (val >> 8) & 0xFF if self.bus_.end_ else val & 0xFF
	

	def secondb(self, val):
		return val & 0xFF if self.bus_.end_ else (val >> 8) & 0xFF
	

	def enable_torque(self, id, enable):
		return self.bus_.write_byte(id, 40, enable)
	

	def set_position_mode(self, id, series):
		# Assert standard position mode with default position-range limits.
		# Read-before-write means this is a no-op when already correct.
		# series is caller-provided because Servo() instances used as
		# proto handlers don't carry the model state themselves.
		return self.apply_mode_config(id, series, WORK_MODE_POSITION, POSITION_MIN, position_max_for_series(series))


	def read_work_mode(self, id, series):
		reg = reg_work_mode_for_series(series)
		if reg is None:
			return None
		return self.bus_.read_byte(id, reg)


	def apply_mode_config(self, id, series, target_mode, target_min_limit, target_max_limit):
		# Read current EPROM values and only write the registers that differ,
		# skipping the unlock/lock dance entirely when nothing needs to change.
		# Position-limit targets must be non-negative: read_word/write_word
		# pass raw 16-bit values through, but the position limit registers
		# are sign-magnitude (bit 15 = sign), so a negative target would
		# need to be encoded before comparing against the raw read.
		work_mode_reg = reg_work_mode_for_series(series)
		lock_reg = reg_lock_for_series(series)
		if work_mode_reg is None or lock_reg is None:
			# Unknown series — refuse to touch unknown register addresses.
			return False
		current_mode = self.bus_.read_byte(id, work_mode_reg)
		current_min = self.bus_.read_word(id, REG_MIN_POSITION_LIMIT)
		current_max = self.bus_.read_word(id, REG_MAX_POSITION_LIMIT)
		if current_mode is None or current_min is None or current_max is None:
			return False
		needs_mode = current_mode != target_mode
		needs_min = current_min != target_min_limit
		needs_max = current_max != target_max_limit
		if not (needs_mode or needs_min or needs_max):
			return True
		self.bus_.write_byte(id, lock_reg, 0)
		if needs_min:
			self.bus_.write_word(id, REG_MIN_POSITION_LIMIT, target_min_limit)
		if needs_max:
			self.bus_.write_word(id, REG_MAX_POSITION_LIMIT, target_max_limit)
		if needs_mode:
			self.bus_.write_byte(id, work_mode_reg, target_mode)
		self.bus_.write_byte(id, lock_reg, 1)
		return True


	def set_wheel_mode(self, id, series):
		# Zeroing both position limits puts the firmware in multi-turn /
		# wheel mode interpretation regardless of work mode value; pairing
		# it with WORK_MODE_WHEEL switches velocity control on.
		return self.apply_mode_config(id, series, WORK_MODE_WHEEL, 0, 0)


	def exit_wheel_mode(self, id, series):
		return self.apply_mode_config(id, series, WORK_MODE_POSITION, POSITION_MIN, position_max_for_series(series))


	def write_velocity(self, id, velocity, acc):
		handler = scservo_sdk.sms_sts(self.bus_.port_handler_)
		res, error = handler.WriteSpec(id, velocity, acc)
		return res


	def write_pos(self, id, goal, time, speed):
		# TODO: implement?
		raise NotImplementedError
	

	def write_pos_ex(self, id, goal, speed, acc):
		handler = scservo_sdk.sms_sts(self.bus_.port_handler_)
		res, error = handler.WritePosEx(id, goal, speed, acc)
		return res
	

	def sync_write_pos(self, ids, goals, times, speeds):
		#TODO: implement?
		raise NotImplementedError
	

	def sync_write_pos_ex(self, ids, goals, speeds, accels):
		handler = scservo_sdk.sms_sts(self.bus_.port_handler_)
		for i in range(len(ids)):
			#FIXME: handle errors
			handler.SyncWritePosEx(ids[i], goals[i], speeds[i], accels[i])
			res = handler.groupSyncWrite.txPacket()
		return res
	

	def reg_write_pos(self, id, goal, time, speed):
		#TODO: implement?
		raise NotImplementedError
	

	def reg_write_pos_ex(self, id, goal, speed, acc):
		handler = scservo_sdk.sms_sts(self.bus_.port_handler_)
		res, error = handler.RegWritePosEx(id, goal, speed, acc)
		return res
	

	def read_position(self, id):
		# The reported value shifts by the Position Offset Value (EPROM
		# register 31) when toggling between position mode and wheel mode
		# on the same servo, with no physical motion. The firmware applies
		# that offset in position mode but reports raw encoder counts in
		# wheel mode (limits zeroed → multi-turn). Default offset is 0;
		# factory variance and the one-key midpoint-calibration feature can
		# both leave non-zero values in EPROM.
		#return self.bus_.read_word(id, 56)
		handler = scservo_sdk.sms_sts(self.bus_.port_handler_)
		pos, res, error = handler.ReadPos(id)
		return pos
	

	def read_load(self, id):
		handler = scservo_sdk.sms_sts(self.bus_.port_handler_)
		val, res, error = handler.read2ByteTxRx(id, 60)
		if 0 == res:
			return handler.scs_tohost(val, 10)
		return 0
	

	def read_speed(self, id):
		#return self.bus_.read_word(id, 58)
		handler = scservo_sdk.sms_sts(self.bus_.port_handler_)
		speed, res, error = handler.ReadSpeed(id)
		return speed
	

	def read_current(self, id):
		handler = scservo_sdk.sms_sts(self.bus_.port_handler_)
		val, res, error = handler.read2ByteTxRx(id, 69)
		if 0 == res:
			return handler.scs_tohost(val, 10)
		return 0
		#return self.bus_.read_word(id, 69) or 0
	

	def read_temperature(self, id):
		return self.bus_.read_byte(id, 63) or 0
	

	def read_voltage(self, id):
		return self.bus_.read_byte(id, 62) or 0
	

	def read_move(self, id):
		return self.bus_.read_byte(id, 66) or 0
	
	
	def read_goal(self, id):
		return self.bus_.read_word(id, 42) or 0


	def read_goal_velocity(self, id):
		handler = scservo_sdk.sms_sts(self.bus_.port_handler_)
		val, res, error = handler.read2ByteTxRx(id, REG_GOAL_VELOCITY)
		if 0 == res:
			return handler.scs_tohost(val, 15)
		return 0
