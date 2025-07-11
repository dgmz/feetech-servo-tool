import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QIntValidator, QRegularExpressionValidator
from ui_mainwindow import Ui_MainWindow
import serial.tools.list_ports
import scservo_sdk
import servo

I32_MAX = 2 ** 31 - 1

class ServoBus:
	def __init__(self):
		self.port_handler_ = None
		self.end_ = 0

	def open(self, port_name):
		if self.port_handler_ is not None:
			return False
		handler = scservo_sdk.PortHandler(port_name)
		if handler.openPort():
			self.port_handler_ = handler
		return self.port_handler_ is not None

	def is_open(self):
		return self.port_handler_ is not None

	def close(self):
		self.port_handler_.closePort()
		self.port_handler_ = None

	def set_baudrate(self, baudrate):
		return self.port_handler_.setBaudRate(baudrate)
	
	def set_timeout(self, t):
		self.port_handler_.setPacketTimeoutMillis(t)
		
	def ping(self, id):
		packet_handler = scservo_sdk.protocol_packet_handler(self.port_handler_, self.end_)
		model, result, error = packet_handler.ping(id)
		return result

	def read_model_number(self, id):
		packet_handler = scservo_sdk.protocol_packet_handler(self.port_handler_, self.end_)
		model, result, error = packet_handler.ping(id)
		return model

	def set_end(self, end):
		self.end_ = end

	def read_byte(self, id, address):
		packet_handler = scservo_sdk.protocol_packet_handler(self.port_handler_, self.end_)
		data, result, error = packet_handler.read1ByteTxRx(id, address)
		if result == 0:
			return data

	def read_word(self, id, address):
		packet_handler = scservo_sdk.protocol_packet_handler(self.port_handler_, self.end_)
		data, result, error = packet_handler.read2ByteTxRx(id, address)
		if result == 0:
			return data

	def write_byte(self, id, address, value):
		packet_handler = scservo_sdk.protocol_packet_handler(self.port_handler_, self.end_)
		result, error = packet_handler.write1ByteTxRx(id, address, value)
		return result

	def write_word(self, id, address, value):
		packet_handler = scservo_sdk.protocol_packet_handler(self.port_handler_, self.end_)
		result, error = packet_handler.write2ByteTxRx(id, address, value)
		return result

class ServoProtocol:
	def __init__(self, bus):
		self.bus_ = bus
	def enable_torque(self, id, enable):
		pass
	def rotation_mode(self, id):
		pass
	def write_pos_ex(self, id, goal, zero1, zero2):
		pass
	def read_position(self, id):
		return self.bus_.read_word(id, 56)
	def read_load(self, id):
		return self.bus_.read_word(id, 60)
	def read_speed(self, id):
		return self.bus_.read_word(id, 58)
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

class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		super(QMainWindow, self).__init__(parent)
		# window
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.ui.ParityComboBox.setEnabled(False)
		self.ui.ParityLabel.setEnabled(False)
		self.setWindowTitle("Feetech Servo Tool")
		
		self.select_servo_ = servo.Servo()

		# timer
		self.graph_timer_ = QtCore.QTimer(self)
		self.graph_timer_.timeout.connect(self.onGraphTimerTimeout)
		self.graph_timer_.start(30)
		#serial port
		self.servo_bus_ = ServoBus()
		
		self.sms_sts_proto_ = ServoProtocol(self.servo_bus_)
		self.scs_proto_ = ServoProtocol(self.servo_bus_)

		self.setupComSettings()
		self.setupServoList()
		
		self.setupServoControl()
		self.setupAutoDebug()
		self.setupDataAnalysis()
		
		self.setupProgramming()
		
		self.setIntRangeLineEdit(self.ui.upLimitLineEdit, 0, 1_200)
		self.setIntRangeLineEdit(self.ui.downLimitLineEdit, 0, 1_200)

		self.mode_ = "WRITE"
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
		self.setIntRangeLineEdit(self.ui.goalLineEdit, 0, 4095)
		self.setIntRangeLineEdit(self.ui.timeLineEdit, 0, I32_MAX)
		
		self.ui.setPushButton.clicked.connect(self.onSetButtonClicked)
		self.ui.torqueEnableCheckBox.stateChanged.connect(self.onTorqueEnableCheckBoxStateChanged)
		self.ui.actionPushButton.clicked.connect(self.onActionButtonClicked)
		
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
		
		self.ui.memoryTableView.selectionModel().selectionChanged.connect(self.onMemoryTableSelection)
		self.ui.memSetButton.clicked.connect(self.onMemSetButtonClicked)
		
		self.prog_timer_ = QtCore.QTimer(self)
		self.prog_timer_.timeout.connect(self.onProgTimerTimeout)
		self.prog_timer_.start(50)
		#self.updateProgMemTable()
		
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
		edit.setValidator(QReularExpressionValidator(QtCore.QRegularExpression("-?\\d*", self)))
	
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
		pass
		
	def syncWritePos(pos, time, speed, acc):
		pass
	
	def regWritePoss(self, pos, time, speed, acc):
		pass
	
	def onPortSearchTimerTimeout(self):
		#print("port seach timeout")
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
		else:
			if not self.servo_bus_.open(self.ui.ComComboBox.currentText()):
				print("Failed to open port")
			else:
				self.servo_bus_.set_baudrate(int(self.ui.BaudComboBox.currentText()))
				self.servo_bus_.set_timeout(int(self.ui.timeoutLineEdit.text()))
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
		selectedRows = self.ui.ServoListView.selectionModel().selectedRows()
		row = selectedRows[0].row()
		index = self.servo_list_model_.index(row, 0)
		self.select_servo_.id_ = int(self.servo_list_model_.data(index))
		index = self.servo_list_model_.index(row, 1)
		self.selectServorSeries(servo.getModelSeries(str(self.servo_list_model_.data(index))))
	
	def onGoalSliderValueChanged(self):
		goal = self.ui.goalSlider.value()
		self.ui.goalLineEdit.setText(str(goal))

		if not self.isServoValidNow():
			return

		if self.mode_ == "REG_WRITE":
			self.regWritePos(goal, 0, 0, 0)
		elif self.mode_ == "SYNC_WRITE":
			self.syncWritePos(goal, 0, 0, 0)
		elif self.mode_ == "WRITE":
			self.writePos(goal, 0, 0, 0)
		
	def onSetButtonClicked(self):
		goal = int(self.ui.goalLineEdit.text())
		speed = int(self.ui.speedLineEdit.text())
		acc = int(self.ui.accLineEdit.text())
		time = int(self.ui.timeLineEdit.text())
		self.ui.goalSlider.setValue(goal)

		if not self.isServoValidNow():
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
		if self.isServoValidNow():
			return

		if self.mode_ == "REG_WRITE":
			self.servo_bus_.reg_write_action(self.select_servo_.id_)

	def onSweepButtonClicked(self):
		if not self.isServoValidNow():
			return

		if self.sweep_running_:
			self.sweep_running = False
			self.ui.sweepButton.setText("Sweep")
			self.ui.stepButton.setEnabled(True)
			self.auto_debug_timer_.stop()
		else:
			self.sweep_running_ = True
			self.ui.sweepButton.setText("Stop")
			self.ui.stepButton.setEnabled(False)
			self.latest_auto_debug_goal_ = int(self.ui.startLineEdit.text())

			if self.select_servo_.model_ == "SCS":
				self.scs_proto_.write_pos(self.select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
			else:
				self.sms_sts_proto_.rotation_mode(self.select_servo_.id_)
				self.sms_sts_proto_.write_pos_ex(self.select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
			self.auto_debug_timer_.start(int(self.ui.sweepLineEdit.text()))
	
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
			self.latest_auto_debug_goal_ = int(self.ui.startLineEdit.text())
			if self.select_servo_.model_ == "SCS":
				self.scs_proto_.write_pos(select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
			else:
				self.sms_sts_proto_.rotation_mode(self.select_servo_.id_)
				self.sms_sts_proto_.write_pos(select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
			self.auto_debug_timer.start(int(self.ui.stepDelayLineEdit.text()))
		
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

		if self.seep_running_:
			start = int(self.ui.startLineEdit.text())
			end = int(self.ui.endLineEdit.text())
			if self.latest_auto_debug_goal_ == start:
				self.latest_auto_debug_goal_ = end
			else:
				self.latest_auto_debug_goal_ = start
			if self.select_servo_.model_ == "SCS":
				self.scs_proto_.write_pos(self.select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
			else:
				self.sms_sts_proto_.rotation_mode(self.select_servo_.id_)
				self.sms_sts_proto_.write_pos_ex(self.select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
		elif self.step_running_:
			start = int(self.ui.startLineEdit.text())
			end = int(self.ui.endLineEdit.text())
			step = int(self.ui.stepLineEdit.text())

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
				self.sms_sts_proto_.rotation_mode(self.select_servo_.id_)
				self.sms_sts_proto_.write_pos_ex(self.select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
		else:
			self.auto_debug_timer.stop()
	
	def onExportButtonClicked(self):
		if not self.isServoValidNow():
			return

		if self.is_recording_:
			self.is_recording_ = False
			self.ui.exportPushButton.setText("Export")
			self.ui.clearPushButton.setNabled(True)

			if self.record_section_data_:
				# FIXME: handle exceptions
				with open(self.record_file_name_, "a") as file:
					file.write(self.record_section_data_)
			self.ui.recSizeLineEdit.setText(self.record_data_count_)
		else:
			self.is_recording_ = True
			self.ui.exportPushButton.setText("Stop")
			self.ui.clearPushButton.setEnabled(False)
			self.record_section_data_ = ""
			self.record_data_count_ = 0
			rec_time = int(self.ui.recTimeLineEdit().text())
			self.file_write_interval_ = max(1, rec_time)
			file_name = self.ui.recFileNameLineEdit.text()
			self.record_file_name_ = os.path.expanduser(file_name)
			#FIXME: handle exceptions
			with open(self.record_file_name_, "w") as file:
				#FIXME: column headers should be
				# "No,Pos,Goal,Torque,Speed,Current,Temp,Voltage"
				file.write("No,Pos,Gol,Ft,V,C,T,Vol\n")
		
	def onClearButtonClicked(self):
		self.record_data_count_ = 0
		self.record_section_data_ = ""
		self.ui.recSizeLineEdit.setText(self.record_data_count_)
	
	def onDataAnalysisTimerTimeout(self):
		if not self.isServoValidNow():
			return

		if not self.is_recording_:
			return

		self.record_data_count += 1
		line = ",".join([str(self.record_data_count_),
			str(self.latest_pos_),
			str(self.latest_goal_),
			str(self.latest_torque_),
			str(self.latest_speed_),
			str(self.latest_current_),
			str(self.latest_temp_),
			str(self.latest_voltage_),
			"END"])
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
			val = int(self.ui.memSetLineEdit.text())
			self.servo_bus_.write_byte(self.select_servo_.id_, 55, 0) # unlock
			self.servo_bus_.write_byte(self.select_servo_.id_, 5, val)
			self.servo_bus_.write_byte(self.select_servo_.id_, 55, 1) # lock
			self.select_servo_.id_ = val
		else:
			val = int(self.ui.memSetLineEdit.text())
			if item.size == 2:
				self.servo_bus_.write_word(self.select_servo_.id_, item.address, val)
			else:
				self.servo_bus_.write_byte(self.select_servo_.id_, item.address, val)
		self.is_mem_writing_ = False
		
	def onGraphTimerTimeout(self):
		self.ui.graphWidget.up_limit = int(self.ui.upLimitLineEdit.text())
		self.ui.graphWidget.down_limit = int(self.ui.downLimitLineEdit.text())
		self.ui.graphWidget.horizontal = self.ui.horizontalSlider.value()
		self.ui.graphWidget.zoom = self.ui.zoomSlider.value()

		if self.is_searching_ or not self.servo_bus_.is_open() or self.select_servo_.id_ < 0:
			return

		self.ui.positionLabel.setText(str(self.latest_pos_))
		self.ui.torqueLabel.setText(str(self.latest_torque_))
		self.ui.speedLabel.setText(str(self.latest_speed_))
		self.ui.currentLabel.setText(str(self.latest_current_))
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
					self.latest_goal_ = self.sms_sts_proto_.read_goal(self.select_servo_.id_)
					self.ui.graphWidget.append_data(self.latest_pos_,
						self.latest_torque_,
						self.latest_speed_,
						self.latest_current_,
						self.latest_temp_,
						self.latest_voltage_)

		self.count_ = (self.count_ + 1) % 3
