import os
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QIntValidator, QRegularExpressionValidator
from ui_mainwindow import Ui_MainWindow
import serial.tools.list_ports
import servo
from servobus import ServoBus

I32_MAX = 2 ** 31 - 1
I16_MIN = -(2 ** 15)
I16_MAX = 2 ** 15 - 1

APP_DIR = os.path.abspath(os.path.dirname(__file__))

def int_or_default(v,default_v):
	try:
		return int(v)
	except ValueError:
		return default_v


class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		super(QMainWindow, self).__init__(parent)
		# window
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		# Pin Servo Feedback value column widths to the rendered width of
		# the widest plausible reading (signed 16-bit "-32768" also covers
		# voltage's "99.9V" formatting). Without this, column widths track
		# the current text and reflow on every update.
		value_col_w = self.ui.voltageLabel.fontMetrics().horizontalAdvance("-32768")
		self.ui.gridLayout_3.setColumnMinimumWidth(1, value_col_w)
		self.ui.gridLayout_3.setColumnMinimumWidth(3, value_col_w)
		self.ui.ParityComboBox.setEnabled(False)
		self.ui.ParityLabel.setEnabled(False)
		self.setWindowTitle("Feetech Servo Tool")
		self.setWindowIcon(QtGui.QIcon(os.path.join(APP_DIR, "icons", "feetech-tool.png")))
		
		self.select_servo_ = servo.Servo(None)

		# timer
		self.graph_timer_ = QtCore.QTimer(self)
		self.graph_timer_.timeout.connect(self.onGraphTimerTimeout)
		self.graph_timer_.start(30)
		#serial port
		self.servo_bus_ = ServoBus()
		
		self.sms_sts_proto_ = servo.Servo(self.servo_bus_)
		self.scs_proto_ = servo.Servo(self.servo_bus_)

		# Initialise mode-tracking state before setup* so any setup method
		# (or signal handler fired during setup) can read these without
		# AttributeError. work_mode_ uses the same int values as the
		# servo's Work Mode register (servo.WORK_MODE_*) so comparisons
		# against read_work_mode() return values are direct.
		self.mode_ = "WRITE"
		self.work_mode_ = servo.WORK_MODE_POSITION
		self.is_syncing_work_mode_ = False

		self.setupComSettings()
		self.setupServoList()
		self.setupServoControl()
		self.setupWorkMode()
		self.setupAutoDebug()
		self.setupDataAnalysis()
		self.setupProgramming()

		self.setIntRangeLineEdit(self.ui.upLimitLineEdit, 0, 1_200)
		self.setIntRangeLineEdit(self.ui.downLimitLineEdit, 0, 1_200)

		self.ui.actionAbout.triggered.connect(self.onAbout)

		self.id_list_ = []
		self.is_searching_ = False
		self.sweep_running_ = False
		self.step_running_ = False
		self.step_increase_ = False
		self.latest_auto_debug_goal_ = 0
		self.is_recording_ = False
		self.file_write_interval_ = 0
		self.record_data_count_ = 0
		self.record_file_name_ = None
		self.record_section_data_ = ""
		self.is_mem_writing_ = False

		self.count_ = 0
		self.latest_pos_ = 0
		self.latest_goal_ = 0
		self.latest_torque_ = 0
		self.latest_speed_ = 0
		self.latest_current_ = 0
		self.latest_temp_ = 0
		self.latest_voltage_ = 0
		self.latest_move_ = 0


	def onAbout(self):
		dlg = QtWidgets.QMessageBox(self)
		dlg.setWindowTitle("About")
		dlg.setText("Verion 0.1.0")
		dlg.exec()


	def isServoValidNow(self):
		return not self.is_searching_ and self.servo_bus_.is_open() \
			and self.select_servo_.id_ >= 0
	

	def setupComSettings(self):
		self.ui.BaudComboBox.addItems([
			"1000000", "500000", "250000", "256000", "128000", "115200",
			"76800", "57600", "38400", "19200", "9600", "4800"
		])
		self.ui.ParityComboBox.addItems(["NONE", "ODD", "EVEN"])
		self.setIntRangeLineEdit(self.ui.timeoutLineEdit, 0, 10_000)
		self.onPortSearchTimerTimeout() # fake event
		self.ui.ComOpenButton.clicked.connect(self.onConnectButtonClicked)
		self.port_search_timer_ = QtCore.QTimer(self)
		self.port_search_timer_.timeout.connect(self.onPortSearchTimerTimeout)
		self.port_search_timer_.start(1000)


	def setupServoList(self):
		self.ui.SearchButton.clicked.connect(self.onSearchButtonClicked)
		self.ui.ServoSearchText.setText("Stop")
		self.servo_list_model_ = QtGui.QStandardItemModel(0,2)
		self.ui.ServoListView.setModel(self.servo_list_model_)
		self.clearServoList()
		
		self.search_timer_ = QtCore.QTimer(self)
		self.search_timer_.timeout.connect(self.onSearchTimerTimeout)
		
		self.servo_read_timer_ = QtCore.QTimer(self)
		self.servo_read_timer_.timeout.connect(self.onServoReadTimerTimeout)
		self.servo_read_timer_.start(10)
		
		self.ui.ServoListView.selectionModel().selectionChanged.connect(self.onServoListSelection)


	def setupServoControl(self):
		self.ui.writeRadioButton.toggled.connect(self.onModeRadioButtonsToggled)
		self.ui.syncWriteRadioButton.toggled.connect(self.onModeRadioButtonsToggled)
		self.ui.regWriteRadioButton.toggled.connect(self.onModeRadioButtonsToggled)
		
		self.ui.goalSlider.valueChanged.connect(self.onGoalSliderValueChanged)
		
		self.setIntRangeLineEdit(self.ui.accLineEdit, 0, I32_MAX)
		self.setIntRangeLineEdit(self.ui.speedLineEdit, 0, I32_MAX)
		self.setIntRangeLineEdit(self.ui.goalLineEdit, I16_MIN, I16_MAX)
		self.setIntRangeLineEdit(self.ui.timeLineEdit, 0, I32_MAX)
		
		self.ui.setPushButton.clicked.connect(self.onSetButtonClicked)
		self.ui.torqueEnableCheckBox.stateChanged.connect(self.onTorqueEnableCheckBoxStateChanged)
		self.ui.actionPushButton.clicked.connect(self.onActionButtonClicked)


	def setupWorkMode(self):
		# A third mode (multi-turn extended position) could slot in here as a
		# QRadioButton wired to the same toggle handler; reconfigureForWorkMode
		# would gain a branch that widens the slider but keeps the position path.
		# The Position/Wheel button group is declared in mainwindow.ui as
		# workModeButtonGroup so it stays separate from the Write/Sync/Reg
		# group (otherwise all radios sharing groupBox_3 would auto-exclude).
		self.ui.positionModeRadioButton.toggled.connect(self.onWorkModeRadioButtonsToggled)
		self.ui.wheelModeRadioButton.toggled.connect(self.onWorkModeRadioButtonsToggled)
		self.ui.positionModeRadioButton.setEnabled(False)
		self.ui.wheelModeRadioButton.setEnabled(False)


	def onWorkModeRadioButtonsToggled(self, checked):
		if not checked:
			return
		if self.is_syncing_work_mode_:
			return
		if not self.isServoValidNow():
			return
		if not self.isWorkModeSupportedSeries():
			return
		series = self.select_servo_.model_
		if self.ui.wheelModeRadioButton.isChecked():
			if self.sms_sts_proto_.set_wheel_mode(self.select_servo_.id_, series):
				# Position-mode writes leave a non-zero Goal Velocity (reg 46)
				# in SRAM; without this the motor would lurch off at that
				# velocity the moment wheel mode takes effect.
				self.sms_sts_proto_.write_velocity(self.select_servo_.id_, 0, 0)
				self.work_mode_ = servo.WORK_MODE_WHEEL
				self.reconfigureForWorkMode()
			else:
				# Transition failed mid-flight; re-read the servo to reconcile
				# the radio state with reality.
				self.syncWorkModeFromServo()
		elif self.ui.positionModeRadioButton.isChecked():
			# Stop the motor before tearing down wheel mode to avoid a lurch
			# when limits get restored.
			if self.work_mode_ == servo.WORK_MODE_WHEEL:
				self.sms_sts_proto_.write_velocity(self.select_servo_.id_, 0, 0)
			if self.sms_sts_proto_.exit_wheel_mode(self.select_servo_.id_, series):
				self.work_mode_ = servo.WORK_MODE_POSITION
				self.reconfigureForWorkMode()
			else:
				self.syncWorkModeFromServo()


	def isWorkModeSupportedSeries(self):
		return self.select_servo_.model_ in servo.WHEEL_MODE_SUPPORTED_SERIES


	def reconfigureForWorkMode(self):
		# Update slider/label/validator to reflect work_mode_. Slider signals
		# are blocked so resetting its value doesn't fire a stray write.
		# Always re-enables the slider and Set button: syncWorkModeFromServo
		# disables them when it finds an unsupported mode (PWM/Step), and
		# this method is the recovery path after the user escapes back to
		# Position or Wheel.
		self.ui.goalSlider.blockSignals(True)
		try:
			# Clear any "Mode: PWM/Step (unsupported)" label left over from
			# the previous sync — we're now in a supported mode.
			self.ui.workModeStatusLabel.setText("")
			self.ui.goalSlider.setEnabled(True)
			self.ui.setPushButton.setEnabled(True)
			if self.work_mode_ == servo.WORK_MODE_WHEEL:
				vel_max = servo.velocity_max_for_series(self.select_servo_.model_)
				self.ui.goalSlider.setMinimum(-vel_max)
				self.ui.goalSlider.setMaximum(vel_max)
				self.ui.goalSlider.setValue(0)
				self.ui.goalLineEdit.setValidator(QIntValidator(-vel_max, vel_max, self))
				self.ui.goalLineEdit.setText("0")
				self.ui.label_13.setText("Velocity")
				self.ui.label_36.setText("Goal velocity:")
				# Sync/Reg write protocols aren't wired for velocity in this
				# round, so force the write radio and grey out the others.
				# The setChecked fires onModeRadioButtonsToggled, which sets
				# self.mode_ and disables the Action button — no need to
				# duplicate either of those side-effects here.
				self.ui.syncWriteRadioButton.setEnabled(False)
				self.ui.regWriteRadioButton.setEnabled(False)
				self.ui.writeRadioButton.setChecked(True)
				# In wheel mode the slider's "Velocity" IS the value written
				# to reg 46 (Goal Velocity) — the same register that "Speed"
				# would have written in position mode. So Speed is redundant
				# here, and Time only applies to position-mode timed moves.
				# Grey both out so the user doesn't enter values that go
				# nowhere.
				self.ui.speedLineEdit.setEnabled(False)
				self.ui.timeLineEdit.setEnabled(False)
			else:
				pos_max = servo.position_max_for_series(self.select_servo_.model_)
				self.ui.goalSlider.setMinimum(servo.POSITION_MIN)
				self.ui.goalSlider.setMaximum(pos_max)
				# Reset to 0 (rather than carrying over the previous slider
				# value, or leaving the UI default 2047) so that clicking
				# Set immediately after a mode change doesn't fire off a
				# stale or wheel-velocity value as a position command.
				self.ui.goalSlider.setValue(0)
				self.ui.goalLineEdit.setValidator(QIntValidator(I16_MIN, I16_MAX, self))
				self.ui.goalLineEdit.setText("0")
				self.ui.label_13.setText("Goal")
				self.ui.label_36.setText("Goal:")
				self.ui.syncWriteRadioButton.setEnabled(True)
				self.ui.regWriteRadioButton.setEnabled(True)
				self.ui.speedLineEdit.setEnabled(True)
				self.ui.timeLineEdit.setEnabled(True)
		finally:
			self.ui.goalSlider.blockSignals(False)


	def syncWorkModeFromServo(self):
		# Called after a servo is selected (or its series changes). Reads
		# register 33 and aligns the UI with the servo's persisted mode.
		# For unsupported series (no Work Mode register), locks the UI into
		# position-mode controls and disables the radios.
		# The is_syncing_work_mode_ flag suppresses onWorkModeRadioButtonsToggled
		# while we programmatically call setChecked() below — otherwise each
		# setChecked would fire the handler and trigger a redundant
		# set_wheel_mode / exit_wheel_mode write.
		self.is_syncing_work_mode_ = True
		try:
			self.ui.workModeStatusLabel.setText("")
			if not self.isWorkModeSupportedSeries() or not self.isServoValidNow():
				self.ui.positionModeRadioButton.setEnabled(False)
				self.ui.wheelModeRadioButton.setEnabled(False)
				self.ui.positionModeRadioButton.setChecked(True)
				self.work_mode_ = servo.WORK_MODE_POSITION
				self.reconfigureForWorkMode()
				return

			work_mode = self.sms_sts_proto_.read_work_mode(self.select_servo_.id_, self.select_servo_.model_)
			self.ui.positionModeRadioButton.setEnabled(True)
			self.ui.wheelModeRadioButton.setEnabled(True)
			if work_mode == servo.WORK_MODE_POSITION:
				self.ui.positionModeRadioButton.setChecked(True)
				self.work_mode_ = servo.WORK_MODE_POSITION
				self.reconfigureForWorkMode()
			elif work_mode == servo.WORK_MODE_WHEEL:
				self.ui.wheelModeRadioButton.setChecked(True)
				self.work_mode_ = servo.WORK_MODE_WHEEL
				self.reconfigureForWorkMode()
			else:
				# PWM, Step, or read failure / None. Reset work_mode_ and
				# labels to the position-mode style so the feedback readout
				# stops calling read_goal_velocity / showing "Goal velocity:"
				# for a servo that isn't actually in wheel mode. Then disable
				# the slider/Set button since neither write path applies, and
				# present both radios as unchecked so the UI reflects the
				# servo's unsupported state.
				self.work_mode_ = servo.WORK_MODE_POSITION
				self.reconfigureForWorkMode()
				self.ui.goalSlider.setEnabled(False)
				self.ui.setPushButton.setEnabled(False)
				# QButtonGroup is normally exclusive (always exactly one
				# checked); drop exclusivity briefly to allow the "all off"
				# state.
				self.ui.workModeButtonGroup.setExclusive(False)
				self.ui.positionModeRadioButton.setChecked(False)
				self.ui.wheelModeRadioButton.setChecked(False)
				self.ui.workModeButtonGroup.setExclusive(True)
				if work_mode == servo.WORK_MODE_PWM:
					self.ui.workModeStatusLabel.setText("Mode: PWM (unsupported)")
				elif work_mode == servo.WORK_MODE_STEP:
					self.ui.workModeStatusLabel.setText("Mode: Step (unsupported)")
				else:
					self.ui.workModeStatusLabel.setText("Mode: unknown")
		finally:
			self.is_syncing_work_mode_ = False


	def setupAutoDebug(self):
		self.setIntRangeLineEdit(self.ui.startLineEdit, 0, 4095)
		self.setIntRangeLineEdit(self.ui.endLineEdit, 0, 4095)
		self.setIntRangeLineEdit(self.ui.sweepLineEdit, 0, I32_MAX)
		self.setIntRangeLineEdit(self.ui.stepLineEdit, 1, I32_MAX)
		self.setIntRangeLineEdit(self.ui.stepDelayLineEdit, 1, I32_MAX)
		
		self.ui.sweepButton.clicked.connect(self.onSweepButtonClicked)
		self.ui.stepButton.clicked.connect(self.onStepButtonClicked)
		
		self.auto_debug_timer_ = QtCore.QTimer(self)
		self.auto_debug_timer_.timeout.connect(self.onAutoDebugTimerTimeout)


	def setupDataAnalysis(self):
		self.ui.exportPushButton.clicked.connect(self.onExportButtonClicked)
		self.ui.clearPushButton.clicked.connect(self.onClearButtonClicked)
		self.setIntRangeLineEdit(self.ui.recTimeLineEdit, 0, I32_MAX)
		
		self.data_analysis_timer_ = QtCore.QTimer(self)
		self.data_analysis_timer_.timeout.connect(self.onDataAnalysisTimerTimeout)
		self.data_analysis_timer_.start(50)


	def setupProgramming(self):
		self.prog_mem_model_ = QtGui.QStandardItemModel(0, 5)
		self.ui.memoryTableView.setModel(self.prog_mem_model_)
		self.clearProgMemTable()
		
		self.ui.SaveButton.clicked.connect(self.onSaveButtonClicked)
		self.ui.LoadButton.clicked.connect(self.onLoadButtonClicked)

		self.ui.memoryTableView.selectionModel().selectionChanged.connect(self.onMemoryTableSelection)
		self.ui.memSetButton.clicked.connect(self.onMemSetButtonClicked)
		
		self.prog_timer_ = QtCore.QTimer(self)
		self.prog_timer_.timeout.connect(self.onProgTimerTimeout)
		self.prog_timer_.start(50)


	def setEnableComSettings(self, state):
		self.ui.ComComboBox.setEnabled(state)
		self.ui.BaudComboBox.setEnabled(state)
		#self.ui.ParityComboBox.setEnabled(state)
		self.ui.timeoutLineEdit.setEnabled(state)


	def clearServoList(self):
		self.servo_list_model_.clear()
		self.servo_list_model_.setHorizontalHeaderLabels(["ID", "Module"])
		
		view = self.ui.ServoListView
		view.setSelectionMode(view.SelectionMode.SingleSelection)
		view.setSelectionBehavior(view.SelectionBehavior.SelectRows)
		view.setHorizontalScrollMode(view.ScrollMode.ScrollPerPixel)
		view.horizontalScrollBar().setDisabled(True)
		header = view.horizontalHeader()
		header.setSectionResizeMode(header.ResizeMode.Stretch)
		header.setSectionResizeMode(0, header.ResizeMode.Fixed)
		view.setColumnWidth(0, 50)
		view.verticalHeader().setVisible(False)
		view.setEditTriggers(view.EditTrigger.NoEditTriggers)
		

	def appendServoList(self, id, name):
		self.servo_list_model_.appendRow([QtGui.QStandardItem(str(id)), QtGui.QStandardItem(name)])


	def clearProgMemTable(self):
		self.prog_mem_model_.clear()
		self.prog_mem_model_.setHorizontalHeaderLabels(["Address", "Memory", "Value", "Area", "R/W"])
		view = self.ui.memoryTableView
		view.setSelectionMode(view.SelectionMode.SingleSelection)
		view.setSelectionBehavior(view.SelectionBehavior.SelectRows)
		view.verticalHeader().setVisible(False)
		header = view.horizontalHeader()
		header.setSectionResizeMode(header.ResizeMode.Fixed)
		header.setSectionResizeMode(1, header.ResizeMode.Stretch)
		view.setColumnWidth(0, 70)
		view.setColumnWidth(2, 70)
		view.setColumnWidth(3, 70)
		view.setColumnWidth(4, 70)
		view.setEditTriggers(view.EditTrigger.NoEditTriggers)


	def updateProgMemTable(self):
		self.clearProgMemTable()
		mem_config = self.getMemConfig(self.select_servo_.model_)
		
		for item in mem_config:
			area = "EPROM" if item.is_eprom else "SRAM"
			rw = "R" if item.is_readonly else "R/W"
			rowList = [QtGui.QStandardItem(str(x)) for x in (item.address, item.name, item.default_value, area, rw)]
			self.prog_mem_model_.appendRow(rowList)


	def setIntRangeLineEdit(self, edit, minval, maxval):
		edit.setValidator(QIntValidator(minval, maxval, self))
	

	def setIntLineEdit(self, edit):
		edit.setValidator(QRegularExpressionValidator(QtCore.QRegularExpression("-?\\d*", self)))
	

	def selectServorSeries(self, series):
		if series == "SCS":
			self.servo_bus_.set_end(1)
		else:
			self.servo_bus_.set_end(0)
		self.select_servo_.model_ = series
		self.updateProgMemTable()
	

	def getMemConfig(self, series):
		return servo.MemConfig.get(series)
	

	def writePos(self, pos, time, speed, acc):
		if self.select_servo_.model_ == "SCS":
			self.scs_proto_.write_pos(self.select_servo_.id_, pos, time, speed)
		else:
			self.sms_sts_proto_.write_pos_ex(self.select_servo_.id_, pos, speed, acc)
		
	
	def syncWritePos(self, pos, time, speed, acc):
		self.id_list_
		n = len(self.id_list_)
		if self.select_servo_.model_ == "SCS":
			self.scs_proto_.sync_write_pos(self.id_list_, [pos]*n, [time]*n, [speed]*n)
		else:
			self.sms_sts_proto_.sync_write_pos_ex(self.id_list_, [pos]*n, [speed]*n, [acc]*n)
	

	def regWritePos(self, pos, time, speed, acc):
		if self.select_servo_.model_ == "SCS":
			self.scs_proto_.reg_write_pos(self.select_servo_.id_, pos, time, speed)
		else:
			self.sms_sts_proto_.reg_write_pos_ex(self.select_servo_.id_, pos, speed, acc)
	

	def onPortSearchTimerTimeout(self):
		if self.servo_bus_.is_open():
			return

		previous = self.ui.ComComboBox.currentText()
		self.ui.ComComboBox.clear()
		for info in serial.tools.list_ports.comports():
			self.ui.ComComboBox.addItem(info.device)
		self.ui.ComComboBox.setCurrentIndex(self.ui.ComComboBox.findText(previous))
			
		
	def onConnectButtonClicked(self):
		if self.servo_bus_.is_open():
			self.servo_bus_.close()
			self.ui.ComOpenButton.setText("Open")
			self.setEnableComSettings(True)
			self.select_servo_.id_ = -1
			# isServoValidNow() is now False; this routes through the early
			# return that disables the Position/Wheel radios and snaps the
			# UI back to position-mode controls, so the radios don't lie
			# about a disconnected servo's state.
			self.syncWorkModeFromServo()
		else:
			if not self.servo_bus_.open(self.ui.ComComboBox.currentText()):
				print("Failed to open port")
			else:
				self.servo_bus_.set_baudrate(int_or_default(self.ui.BaudComboBox.currentText(), 1000000))
				self.servo_bus_.set_timeout(int_or_default(self.ui.timeoutLineEdit.text(), 50))
				self.ui.ComOpenButton.setText("Close")
				self.setEnableComSettings(False)
	

	def onSearchButtonClicked(self):
		if not self.servo_bus_.is_open():
			print("bus not open")
			return
			
		self.is_searching_ = not self.is_searching_

		if self.is_searching_:
			self.ui.SearchButton.setText("Stop")
			self.clearServoList()
			self.id_list_.clear()
			self.search_id_ = 0
			self.is_searching_ = True
			#self.search_timer_.start(10)
			self.onSearchTimerTimeout()
		else:
			self.ui.SearchButton.setText("Search")
			self.search_timer_.stop()
			self.ui.ServoSearchText.setText("Stop")
			
	
	def onSearchTimerTimeout(self):
		#print("search timer timeout")
		self.search_timer_.stop()
		if not self.is_searching_:
			print("not searching")
			return

		if 0xfd < self.search_id_ or not self.servo_bus_.is_open():
			self.is_searching_ = False
			self.ui.SearchButton.setText("Search")
			self.ui.ServoSearchText.setText("Stop")
		else:
			self.ui.ServoSearchText.setText(f"Ping ID:{self.search_id_} Servo...")
			mid = self.servo_bus_.read_model_number(self.search_id_)
			if 0 != mid:
				name = servo.getModelType(mid)
				self.appendServoList(self.search_id_, name)
				self.id_list_ += [self.search_id_]
				self.selectServorSeries(servo.getModelSeries(name))
			self.search_id_ += 1
			self.search_timer_.start(1)
	

	def onServoListSelection(self):
		if self.is_searching_:
			self.onSearchButtonClicked()
		selectedRows = self.ui.ServoListView.selectionModel().selectedRows()
		row = selectedRows[0].row()
		index = self.servo_list_model_.index(row, 0)
		self.select_servo_.id_ = int_or_default(self.servo_list_model_.data(index), None)
		index = self.servo_list_model_.index(row, 1)
		self.selectServorSeries(servo.getModelSeries(str(self.servo_list_model_.data(index))))
		self.syncWorkModeFromServo()
	

	def onGoalSliderValueChanged(self):
		goal = self.ui.goalSlider.value()
		self.ui.goalLineEdit.setText(str(goal))

		if not self.isServoValidNow():
			return

		if self.work_mode_ == servo.WORK_MODE_WHEEL:
			acc = int_or_default(self.ui.accLineEdit.text(), 0)
			self.sms_sts_proto_.write_velocity(self.select_servo_.id_, goal, acc)
			return

		if self.mode_ == "REG_WRITE":
			self.regWritePos(goal, 0, 0, 0)
		elif self.mode_ == "SYNC_WRITE":
			self.syncWritePos(goal, 0, 0, 0)
		elif self.mode_ == "WRITE":
			self.writePos(goal, 0, 0, 0)


	def onSetButtonClicked(self):
		goal = int_or_default(self.ui.goalLineEdit.text(), 0)
		speed = int_or_default(self.ui.speedLineEdit.text(), 0)
		acc = int_or_default(self.ui.accLineEdit.text(), 0)
		time = int_or_default(self.ui.timeLineEdit.text(), 0)
		self.ui.goalSlider.setValue(goal)

		if not self.isServoValidNow():
			print("servo not valid")
			return

		if self.work_mode_ == servo.WORK_MODE_WHEEL:
			self.sms_sts_proto_.write_velocity(self.select_servo_.id_, goal, acc)
			return

		if self.mode_ == "REG_WRITE":
			self.regWritePos(goal, time, speed, acc)
		elif self.mode_ == "SYNC_WRITE":
			self.syncWritePos(goal, time, speed, acc)
		elif self.mode_ == "WRITE":
			self.writePos(goal, time, speed, acc)


	def onTorqueEnableCheckBoxStateChanged(self):
		if not self.isServoValidNow():
			return

		if self.select_servo_.model_ == "SCS":
			self.scs_proto_.enable_torque(self.select_servo_.id_, self.ui.torqueEnableCheckBox.isChecked())
		else:
			self.sms_sts_proto_.enable_torque(self.select_servo_.id_, self.ui.torqueEnableCheckBox.isChecked())

	
	def onModeRadioButtonsToggled(self, checked):
		if checked:
			if self.ui.writeRadioButton.isChecked():
				self.mode_ = "WRITE"
			elif self.ui.syncWriteRadioButton.isChecked():
				self.mode_ = "SYNC_WRITE"
			elif self.ui.regWriteRadioButton.isChecked():
				self.mode_ = "REG_WRITE"

			self.ui.actionPushButton.setEnabled(self.mode_ == "REG_WRITE")
	

	def onActionButtonClicked(self):
		if not self.isServoValidNow():
			return

		if self.mode_ == "REG_WRITE":
			self.servo_bus_.reg_write_action(self.select_servo_.id_)


	def onSweepButtonClicked(self):
		if not self.isServoValidNow():
			return

		if self.sweep_running_:
			self.sweep_running_ = False
			self.ui.sweepButton.setText("Sweep")
			self.ui.stepButton.setEnabled(True)
			self.auto_debug_timer_.stop()
		else:
			self.sweep_running_ = True
			self.ui.sweepButton.setText("Stop")
			self.ui.stepButton.setEnabled(False)
			self.latest_auto_debug_goal_ = int_or_default(self.ui.startLineEdit.text(), 0)

			if self.select_servo_.model_ == "SCS":
				self.scs_proto_.write_pos(self.select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
			else:
				self.sms_sts_proto_.set_position_mode(self.select_servo_.id_, self.select_servo_.model_)
				# Always re-sync the UI: set_position_mode just wrote
				# Work Mode = 0, but the UI may still show wheel-mode
				# controls (from work_mode_ == WHEEL) or unsupported-mode
				# state (status label set, slider disabled). Both cases
				# need the sync; work_mode_ alone can't distinguish them
				# because the unsupported branch also leaves work_mode_
				# at POSITION.
				self.syncWorkModeFromServo()
				self.sms_sts_proto_.write_pos_ex(self.select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
			self.auto_debug_timer_.start(int_or_default(self.ui.sweepLineEdit.text(), 0))


	def onStepButtonClicked(self):
		if not self.isServoValidNow():
			return

		if self.step_running_:
			self.step_running_ = False
			self.ui.stepButton.setText("Step")
			self.ui.sweepButton.setEnabled(True)
			self.auto_debug_timer_.stop()
		else:
			self.step_running_ = True
			self.step_increase_ = True
			self.ui.stepButton.setText("Stop")
			self.ui.sweepButton.setEnabled(False)
			self.latest_auto_debug_goal_ = int_or_default(self.ui.startLineEdit.text(), 0)
			if self.select_servo_.model_ == "SCS":
				self.scs_proto_.write_pos(self.select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
			else:
				self.sms_sts_proto_.set_position_mode(self.select_servo_.id_, self.select_servo_.model_)
				self.syncWorkModeFromServo()
				self.sms_sts_proto_.write_pos_ex(self.select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
			self.auto_debug_timer_.start(int_or_default(self.ui.stepDelayLineEdit.text(), 0))


	def onAutoDebugTimerTimeout(self):
		if not self.isServoValidNow():
			self.auto_debug_timer.stop()
			self.sweep_running_ = False
			self.step_running_ = False
			self.ui.sweepButton.setText("Sweep")
			self.ui.sweepButton.setEnabled(True)
			self.ui.stepButton.setText("Step")
			self.ui.stepButton.setEnabled(True)
			return

		if self.sweep_running_:
			start = int_or_default(self.ui.startLineEdit.text(), 0)
			end = int_or_default(self.ui.endLineEdit.text(), 4095)
			if self.latest_auto_debug_goal_ == start:
				self.latest_auto_debug_goal_ = end
			else:
				self.latest_auto_debug_goal_ = start
			if self.select_servo_.model_ == "SCS":
				self.scs_proto_.write_pos(self.select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
			else:
				self.sms_sts_proto_.set_position_mode(self.select_servo_.id_, self.select_servo_.model_)
				self.sms_sts_proto_.write_pos_ex(self.select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
		elif self.step_running_:
			start = int_or_default(self.ui.startLineEdit.text(), 0)
			end = int_or_default(self.ui.endLineEdit.text(), 4095)
			step = int_or_default(self.ui.stepLineEdit.text(), 10)

			self.latest_auto_debug_goal_ += step if self.step_increase_ else -step

			if end < self.latest_auto_debug_goal_:
				self.latest_auto_debug_goal_ = end
				self.step_increase_ = False
			elif self.latest_auto_debug_goal_ < start:
				self.latest_auto_debug_goal_ = start
				self.step_increase_ = True

			if self.select_servo_.model_ == "SCS":
				self.scs_proto_.write_pos(self.select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
			else:
				self.sms_sts_proto_.set_position_mode(self.select_servo_.id_, self.select_servo_.model_)
				self.sms_sts_proto_.write_pos_ex(self.select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
		else:
			self.auto_debug_timer.stop()


	def onExportButtonClicked(self):
		if not self.isServoValidNow():
			return

		if self.is_recording_:
			self.is_recording_ = False
			self.ui.exportPushButton.setText("Export")
			self.ui.clearPushButton.setEnabled(True)

			if self.record_section_data_:
				# FIXME: handle exceptions
				with open(self.record_file_name_, "a") as file:
					file.write(self.record_section_data_)
			self.ui.recSizeLineEdit.setText(str(self.record_data_count_))
		else:
			self.is_recording_ = True
			self.ui.exportPushButton.setText("Stop")
			self.ui.clearPushButton.setEnabled(False)
			self.record_section_data_ = ""
			self.record_data_count_ = 0
			rec_interval = int_or_default(self.ui.recTimeLineEdit.text(), 10)
			self.file_write_interval_ = max(1, rec_interval)
			file_name = self.ui.recFileNameLineEdit.text()
			self.record_file_name_ = os.path.expanduser(file_name)
			#FIXME: handle exceptions
			with open(self.record_file_name_, "w") as file:
				file.write('"No","Pos","Goal","Torque","Speed","Current","Temp","Voltage"\n')


	def onClearButtonClicked(self):
		self.record_data_count_ = 0
		self.record_section_data_ = ""
		self.ui.recSizeLineEdit.setText(self.record_data_count_)


	def onDataAnalysisTimerTimeout(self):
		if not self.isServoValidNow():
			return

		if not self.is_recording_:
			return

		self.record_data_count_ += 1
		line = ",".join([str(self.record_data_count_),
			str(self.latest_pos_),
			str(self.latest_goal_),
			str(self.latest_torque_),
			str(self.latest_speed_),
			str(self.latest_current_),
			str(self.latest_temp_),
			str(self.latest_voltage_)])
		self.record_section_data_ += line + "\n"
		section_size = 20 * self.file_write_interval_ # FIXME: magic number

		if self.record_data_count_ % section_size == 0:
			# FIXME: handle exceptions
			with open(self.record_file_name_, "a") as file:
				file.write(self.record_section_data_)
			self.record_section_data_ = ""
			self.ui.recSizeLineEdit.setText(str(self.record_data_count_))


	def onProgTimerTimeout(self):
		if self.ui.tabWidget.currentIndex() != 1:
			return
			
		if not self.isServoValidNow():
			return

		if self.is_mem_writing_:
			return

		firstVisibleRow = self.ui.memoryTableView.indexAt(self.ui.memoryTableView.viewport().rect().topLeft()).row()
		lastVisibleRow = self.ui.memoryTableView.indexAt(self.ui.memoryTableView.viewport().rect().bottomLeft()).row()
		if firstVisibleRow != -1 and lastVisibleRow != -1:
			mem_config = self.getMemConfig(self.select_servo_.model_)
			for i in range(firstVisibleRow, lastVisibleRow + 1):
				item = mem_config[i]
				val = 0
				if item.size == 2:
					val = self.servo_bus_.read_word(self.select_servo_.id_, item.address)
				else:
					val = self.servo_bus_.read_byte(self.select_servo_.id_, item.address)

				model = self.ui.memoryTableView.model()
				model.setData(model.index(i,2), str(val))


	def onMemoryTableSelection(self):
		selectedRows = self.ui.memoryTableView.selectionModel().selectedRows()
		row = selectedRows[0].row()
		mem = self.prog_mem_model_
		index = mem.index(row, 1)
		self.ui.memLabel.setText(str(mem.data(index)))
		index = mem.index(row, 2)
		self.ui.memSetLineEdit.setText(str(mem.data(index)))
		mem_config = self.getMemConfig(self.select_servo_.model_)
		item = mem_config[row]
		self.ui.memSetLineEdit.setEnabled(not item.is_readonly)
		self.ui.memSetButton.setEnabled(not item.is_readonly)


	def onMemSetButtonClicked(self):
		self.is_mem_writing_ = True
		selectedRows = self.ui.memoryTableView.selectionModel().selectedRows()
		mem_config = self.getMemConfig(self.select_servo_.model_)
		item = mem_config[selectedRows[0].row()]

		# TODO No address reference
		if item.address == 5:
			# TODO: Support non-STS servos
			val = int_or_default(self.ui.memSetLineEdit.text(), 0)
			self.servo_bus_.write_byte(self.select_servo_.id_, 55, 0) # unlock
			self.servo_bus_.write_byte(self.select_servo_.id_, 5, val)
			self.servo_bus_.write_byte(self.select_servo_.id_, 55, 1) # lock
			self.select_servo_.id_ = val
		else:
			val = int_or_default(self.ui.memSetLineEdit.text(), 0)
			if item.size == 2:
				self.servo_bus_.write_word(self.select_servo_.id_, item.address, val)
			else:
				self.servo_bus_.write_byte(self.select_servo_.id_, item.address, val)
		self.is_mem_writing_ = False
		# Writes to Work Mode or the Min/Max Position Limits change the
		# servo's mode interpretation, so the Servo Control tab needs to
		# re-read and re-render. Without this, manually changing those
		# registers in the memory table only takes effect on app restart.
		if self.isWorkModeSupportedSeries() and item.address in (
			servo.REG_MIN_POSITION_LIMIT,
			servo.REG_MAX_POSITION_LIMIT,
			servo.reg_work_mode_for_series(self.select_servo_.model_),
		):
			self.syncWorkModeFromServo()


	def onGraphTimerTimeout(self):
		self.ui.graphWidget.up_limit = int_or_default(self.ui.upLimitLineEdit.text(), 0)
		self.ui.graphWidget.down_limit = int_or_default(self.ui.downLimitLineEdit.text(), 0)
		self.ui.graphWidget.horizontal = self.ui.horizontalSlider.value()
		self.ui.graphWidget.zoom = self.ui.zoomSlider.value()

		if self.is_searching_ or not self.servo_bus_.is_open() or self.select_servo_.id_ < 0:
			return

		self.ui.positionLabel.setText(str(self.latest_pos_))
		self.ui.torqueLabel.setText(str(self.latest_torque_))
		self.ui.speedLabel.setText(str(self.latest_speed_))
		self.ui.currentLabel.setText("%6.1fmA" % (self.latest_current_ * 6.5))
		self.ui.temperatureLabel.setText(str(self.latest_temp_))
		self.ui.voltageLabel.setText("%.1fV" % (self.latest_voltage_ * 0.1))
		self.ui.movingLabel.setText(str(self.latest_move_))
		self.ui.goalLabel.setText(str(self.latest_goal_))

		self.ui.graphWidget.series['pos'].visible = self.ui.posCheckBox.isChecked()
		self.ui.graphWidget.series['torque'].visible = self.ui.torqueCheckBox.isChecked()
		self.ui.graphWidget.series['speed'].visible = self.ui.speedCheckBox.isChecked()
		self.ui.graphWidget.series['current'].visible = self.ui.currentCheckBox.isChecked()
		self.ui.graphWidget.series['temp'].visible = self.ui.tempCheckBox.isChecked()
		self.ui.graphWidget.series['voltage'].visible = self.ui.voltageCheckBox.isChecked()


	def onServoReadTimerTimeout(self):
		if self.ui.tabWidget.currentIndex() != 0:
			return

		if self.isServoValidNow():
			if self.select_servo_.model_ == "SCS":
				if self.count_ == 0:
					self.latest_pos_ = self.scs_proto_.read_position(self.select_servo_.id_)
					print(f"pos: {self.latest_pos_}")
					self.latest_torque_ = self.scs_proto_.read_load(self.select_servo_.id_)
				elif self.count_ == 1:
					self.latest_speed_ = self.scs_proto_.read_speed(self.select_servo_.id_)
					self.latest_current_ = self.scs_proto_.read_current(self.select_servo_.id_)
				elif self.count_ == 2:
					self.latest_temp_ = self.scs_proto_.read_temperature(self.select_servo_.id_)
					self.latest_voltage_ = self.scs_proto_.read_voltage(self.select_servo_.id_)
					self.latest_move_ = self.scs_proto_.read_move(self.select_servo_.id_)
					self.latest_goal_ = self.scs_proto_.read_goal(self.select_servo_.id_)
					self.ui.graphWidget.append_data(self.latest_pos_,
						self.latest_torque_,
						self.latest_speed_,
						self.latest_current_,
						self.latest_temp_,
						self.latest_voltage_)
			else:
				if self.count_ == 0:
					self.latest_pos_ = self.sms_sts_proto_.read_position(self.select_servo_.id_)
					self.latest_torque_ = self.sms_sts_proto_.read_load(self.select_servo_.id_)
				elif self.count_ == 1:
					self.latest_speed_ = self.sms_sts_proto_.read_speed(self.select_servo_.id_)
					self.latest_current_ = self.sms_sts_proto_.read_current(self.select_servo_.id_)
					self.latest_temp_ = self.sms_sts_proto_.read_temperature(self.select_servo_.id_)
				elif self.count_ == 2:
					self.latest_voltage_ = self.sms_sts_proto_.read_voltage(self.select_servo_.id_)
					self.latest_move_ = self.sms_sts_proto_.read_move(self.select_servo_.id_)
					if self.work_mode_ == servo.WORK_MODE_WHEEL:
						self.latest_goal_ = self.sms_sts_proto_.read_goal_velocity(self.select_servo_.id_)
					else:
						self.latest_goal_ = self.sms_sts_proto_.read_goal(self.select_servo_.id_)
					self.ui.graphWidget.append_data(self.latest_pos_,
						self.latest_torque_,
						self.latest_speed_,
						self.latest_current_,
						self.latest_temp_,
						self.latest_voltage_)

		self.count_ = (self.count_ + 1) % 3

	def onSaveButtonClicked(self):
		pass

	def onLoadButtonClicked(self):
		pass