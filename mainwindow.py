import sys
from PyQt6 import QtWidgets, QtSerialPort, QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QIntValidator, QRegularExpressionValidator
from ui_mainwindow import Ui_MainWindow
import servo

I32_MAX = 2 ** 31 - 1

def mkitem(x):
	return QtGui.QStandardItem(str(x))

class SCSerial:
	def set_timeout(self, t):
		pass
	def ping(self, id):
		return -1

class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		super(QMainWindow, self).__init__(parent)
		# window
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.setWindowTitle("FT Servo Debug pyQt")
		
		self.select_servo_ = servo.Servo()

		# timer
		self.graph_timer_ = QtCore.QTimer(self)
		self.graph_timer_.timeout.connect(self.onGraphTimerTimeout)
		self.graph_timer_.start(30)
		#serial port
		self.serial_ = QtSerialPort.QSerialPort(self)
		self.scserial_ = SCSerial() # TODO init API

		self.setupComSettings()
		self.setupServoList()
		
		self.setupServoControl()
		self.setupAutoDebug()
		self.setupDataAnalysis()
		
		self.setupProgramming()
		
		self.setIntRangeLineEdit(self.ui.upLimitLineEdit, 0, 1_200)
		self.setIntRangeLineEdit(self.ui.downLimitLineEdit, 0, 1_200)

		self.is_searching_ = False
		self.sweep_running_ = False
		self.setp_running_ = False
		self.setp_increase_ = False
		self.mode_ = "WRITE"

	def isServoValidNow(self):
		return not (self.is_searching_ or not self.serial_.isOpen() or
			self.select_servo_.id < 0)
	
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
		self.port_search_timer_.start(500)

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
		self.setIntRangeLineEdit(self.ui.setpLineEdit, 1, I32_MAX)
		self.setIntRangeLineEdit(self.ui.setpDelayLineEdit, 1, I32_MAX)
		
		self.ui.sweepButton.clicked.connect(self.onSweepButtonClicked)
		self.ui.setpButton.clicked.connect(self.onSetpButtonClicked)
		
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
		self.updateProgMemTable()
		
	def setEnableComSettings(self, state):
		self.ui.ComComboBox.setEnabled(state)
		self.ui.BaudComboBox.setEnabled(state)
		self.ui.ParityComboBox.setEnabled(state)
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
		self.servo_list_model_.appendRow([mkitem(id), mkitem(name)])
	
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
			(address, name, size, default_value, dir_bit, is_eprom, is_readonly, min_val, max_val) = item
			area = "EPROM" if is_eprom else "SRAM"
			rw = "R" if is_readonly else "R/W"
			rowList = [mkitem(address), mkitem(name), mkitem(default_value), mkitem(area), mkitem(rw)]
			self.prog_mem_model_.appendRow(rowList)
	
	def setIntRangeLineEdit(self, edit, minval, maxval):
		edit.setValidator(QIntValidator(minval, maxval, self))
	
	def setIntLineEdit(self, edit):
		edit.setValidator(QReularExpressionValidator(QtCore.QRegularExpression("-?\\d*", self)))
	
	def selectServorSeries(self, series):
		if series == "SCS":
			self.scserial_.set_end(1)
		else:
			self.scserial_.set_end(0)
		self.select_servo_.model_ = series
		upgradeProgMemTable()
	
	def getMemConfig(self, series):
		if series == "SCS":
			return servo.SCSMemConfig
		else:
			return servo.STSMemConfig
	
	def writePos(self, pos, time, speed, acc):
		pass
		
	def syncWritePos(pos, time, speed, acc):
		pass
	
	def regWritePoss(self, pos, time, speed, acc):
		pass
	
	def onPortSearchTimerTimeout(self):
		#print("port seach timeout")
		if self.serial_.isOpen():
			return
		
		self.ui.ComComboBox.clear()
		for info in QtSerialPort.QSerialPortInfo.availablePorts():
			self.ui.ComComboBox.addItem(info.portName())
		
	def onConnectButtonClicked(self):
		if self.serial_.isOpen():
			self.serial_.close()
			self.ui.ComOpenButton.setText("Open")
			self.setEnableComSettings(True)
			self.select_servo_.id_ = -1
		else:
			self.serial_.setPortName(self.ui.ComComboBox.currentText())
			self.serial_.setBaudRate(int(self.ui.BaudComboBox.currentText()))
			pidx = self.ui.ParityComboBox.currentIndex()
			p = self.serial_.Parity.NoParity
			if pidx == 1:
				p = self.serial_.Parity.OddParity
			elif pidx == 2:
				p = self.serial_.Parity.EvenParity
			self.serial_.setParity(p)
			self.serial_.setDataBits(self.serial_.DataBits.Data8)
			self.serial_.setStopBits(self.serial_.StopBits.OneStop)
			self.serial_.setFlowControl(self.serial_.FlowControl.NoFlowControl)
			if self.serial_.open(self.serial_.OpenModeFlag.ReadWrite):
				self.ui.ComOpenButton.setText("Close")
				self.setEnableComSettings(False)
			else:
				self.ui.ComOpenButton.setText("Open")
			self.scserial_.set_timeout(int(self.ui.timeoutLineEdit.text()))
	
	def onSearchButtonClicked(self):
		if not self.serial_.isOpen():
			print("serial not open")
			return
			
		self.is_searching = not self.is_searching_

		if self.is_searching:
			self.ui.SearchButton.setText("Stop")
			self.clearServoList()
			self.id_list_.clear()
			self.search_id_ = 0
			self.search_timer_.start(10)
			self.onSearchTimerTimeout()
		else:
			self.ui.SearchButton.setText("Search")
			self.search_timer_.stop()
			self.ui.ServoSearchText.setText("Stop")
			
	def onSearchTimerTimeout(self):
		#print("search timer timeout")
		self.search_timer.stop()
		if not self.is_searching_:
			return

		if 0xfd < self.search_id_ or not self.serial.isOpen():
			self.is_searching_ = False
			self.ui.SearchButton.setText("Search")
			self.ui.ServoSearchText.setText("Stop")
		else:
			self.ui.ServoSearchText.setText(f"Ping ID:{search_id} Servo...")
			ret = self.scserial_.ping(self.search_id_)
			if 0 < ret:
				mid = self.scserial_.read_model_number(ret)
				name = servo.getModeltype(mid)
				self.appendServoList(ret, name)
				self.id_list_ += ret
				self.selectServorSeries(servo.getModelSeries(name))
			self.search_id_ += 1
			self.search_timer_.start(1)
	
	def onServoListSelection(self):
		selectedRows = self.ui.ServoListView.selectionModel().selectedRows()
		row = selectedRows[0].row()
		index = self.servo_list_model_.index(row, 0)
		self.select_servo.id_ = int(self.servo_list_model_.data(index))
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
			self.scs_serial_.enable_torque(self.select_servo_.id_, self.ui.torqueEnableCheckbox.isChecked())
		else:
			self.sms_sts_serial_.enable_torque(self.select_servo_.id_, self.ui.torqueEnableCheckbox.isChecked())

	def onModeRadioButtonsToggled(self, checked):
		if checked:
			if self.ui.writeRadioButton.isChecked():
				self.mode_ = "WRITE"
			elif self.ui.syncWriteRadioButton.isChecked():
				self.mode_ = "SYNC_WRITE"
			elif self.ui.regWriteRadioButton.isChecked():
				self.mode_ = "REG_WRITE"

			self.ui.actionPushButton.setEnable(self.mode_ == "REG_WRITE")
	
	def onActionButtonClicked(self):
		if self.isServoValidNow():
			return

		if self.mode_ == "REG_WRITE":
			self.scserial_.reg_write_action(self.select_servo_.id_)

	def onSweepButtonClicked(self):
		if not self.isServoValidNow():
			return

		if self.sweep_running_:
			self.sweep_running = False
			self.ui.sweepButton.setText("Sweep")
			self.ui.setpButton.setEnabled(True)
			self.auto_debug_timer_.stop()
		else:
			self.sweep_running_ = True
			self.ui.sweepButton.setText("Stop")
			self.ui.setpButton.setEnabled(False)
			self.latest_auto_debug_goal_ = int(self.ui.startLineEdit.text())

			if self.select_servo_.model_ == "SCS":
				self.scs_serial_.write_pos(self.select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
			else:
				self.sms_sts_serial_.rotation_mode(self.select_servo_.id_)
				self.sms_sts_serial_.write_pos_ex(self.select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
			self.auto_debug_timer_.start(int(self.ui.sweepLineEdit.text()))
	
	def onSetpButtonClicked(self):
		if not self.isServoValidNow():
			return

		if self.setp_running_:
			self.setp_running_ = False
			self.ui.setpButton.setText("Setp")
			self.ui.sweepButton.setEnabled(True)
			self.auto_debug_timer_.stop()
		else:
			self.setp_running_ = True
			self.setp_increase_ = True
			self.ui.setpButton.setText("Stop")
			self.ui.sweepButton.setEnabled(False)
			self.latest_auto_debug_goal_ = int(self.ui.startLineEdit.text())
			if self.select_servo_.model_ == "SCS":
				self.scs_serial_.write_pos(select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
			else:
				self.sms_sts_serial_.rotation_mode(self.select_servo_.id_)
				self.sms_sts_serial_.write_pos(select_servo_.id_, self.latest_auto_debug_goal_, 0, 0)
			self.auto_debug_timer.start(int(self.ui.setpDelayLineEdit.text()))
		
	def onAutoDebugTimerTimeout(self):
		print("auto debug timer timeout")
		pass
	
	def onExportButtonClicked(self):
		print("export button clicked")
		pass
		
	def onClearButtonClicked(self):
		print("clear button clicked")
		pass
	
	def onDataAnalysisTimerTimeout(self):
		#print("data analysis timer timeout")
		pass

	def onProgTimerTimeout(self):
		#print("prog timer timeout")
		pass
		
	def onMemoryTableSelection(self):
		print("memory table selection")
		pass
		
	def onMemSetButtonClicked(self):
		print("mem set button clicked")
		pass
		
	def onGraphTimerTimeout(self):
		#print("graph timer timeout")
		pass

	def onServoReadTimerTimeout(self):
		pass
