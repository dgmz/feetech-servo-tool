from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QWidget
from collections import deque


def mapping(val, in_min, in_max, out_min, out_max):
	return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

class Series:
	def __init__(self, maxlen, color, gain, min, max):
		self.buffer = deque(maxlen=maxlen)
		self.color = color
		self.gain = gain
		self.min = min
		self.max = max
		self.visible = False

	def plot(self, w, scale, hoffset, y_min, y_max):
		points = []
		for i, v in enumerate(self.buffer):
			x = mapping(self.buffer.maxlen - len(self.buffer) + i, 0, self.buffer.maxlen, w - w * scale + hoffset, w + hoffset)
			y = mapping(self.gain * v, self.min, self.max, y_min, y_max)
			points += [(x, y)]
		return points


class SimpeGraphWiget(QWidget):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.series = {
			"pos":     Series(300, QtGui.QColor("black"),       1.0,     0, 4000),
			"torque":  Series(300, QtGui.QColor("orange"),      1.0, -1000, 1000),
			"speed":   Series(300, QtGui.QColor("green"),       0.2, -1000, 1000),
			"current": Series(300, QtGui.QColor("cyan"),        1.0, -1000, 1000),
			"temp":    Series(300, QtGui.QColor("yellowgreen"), 1.0, -1000, 1000),
			"voltage": Series(300, QtGui.QColor("magenta"),     1.0, -1000, 1000)
		}

		self.down_limit = 0
		self.up_limit = 0
		self.horizontal = 0
		self.zoom = 1

		self.timer_ = QtCore.QTimer(self)
		self.timer_.timeout.connect(self.onTimeout)
		self.timer_.start(20)
		#self.phase_ = 0.0

	def reset_data(self):
		for s in self.series:
			self.series[s].buffer.clear()

	def append_data(self, pos, torque, speed, current, temp, voltage):
		self.series["pos"].buffer.append(pos)
		self.series["torque"].buffer.append(torque)
		self.series["speed"].buffer.append(speed)
		self.series["current"].buffer.append(current)
		self.series["temp"].buffer.append(temp)
		self.series["voltage"].buffer.append(voltage)

	def onTimeout(self):
		self.update()

	def paintEvent(self, event):
		painter = QtGui.QPainter(self)

		w = self.width()
		h = self.height()

		grid_pen = QtGui.QPen()
		grid_pen.setStyle(QtCore.Qt.PenStyle.CustomDashLine)
		grid_pen.setDashPattern([12, 4])
		grid_pen.setWidthF(1.0)
		grid_pen.setColor(QtGui.QColor('black'))
		painter.setPen(grid_pen)

		max_scale = 6.0
		min_grid_size = h // 11.5
		max_grid_size = min_grid_size * max_scale
		grid_size = mapping(self.zoom, 0.0, 100.0, min_grid_size, max_grid_size) 
		hoffset = mapping(self.horizontal, 0.0, 100, 0, w) 
		scale = mapping(self.zoom, 0.0, 100.0, 1.0, max_scale)

		for i in range(int(w // grid_size) + 1):
			x = w - i * grid_size
			painter.drawLine(int(x), 0, int(x), int(h))

		for i in range(11):
			y = h // 2 + (i - 5) * (h // 11.5)
			painter.drawLine(0, int(y), int(w), int(y))

		grid_y_min = h // 2 - 5 * (h // 11.5)
		grid_y_max = h // 2 + 5 * (h // 11.5)

		pen = QtGui.QPen()
		pen.setWidthF(1.2)
		painter.setPen(pen)

		painter.setRenderHint(painter.RenderHint.Antialiasing, True)
		for s in self.series:
			serie = self.series[s]
			if serie.visible:
				pen.setColor(serie.color)
				painter.setPen(pen)
				points = serie.plot(w, scale, hoffset, grid_y_min, grid_y_max)
				if points:
					# drawPath() is hideously slow, use drawLine() instead
					(x0, y0) = points[0]
					for (x1, y1) in points[1:]:
						painter.drawLine(int(x0), int(y0), int(x1), int(y1))
						x0, y0 = x1, y1

		for limit in [self.up_limit, self.down_limit]:
			if limit:
				pen.setColor(QtGui.QColor('plum'))
				painter.setPen(pen)
				y = mapping(limit, -1000, 1000, grid_y_max, grid_y_min)
				painter.drawLine(0, int(y), int(w), int(y))
				y = mapping(-limit, -1000, 1000, grid_y_max, grid_y_min)
				painter.drawLine(0, int(y), int(w), int(y))

if __name__ == "__main__":

	import sys
	from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton
	from random import randint

	class MainWindow(QMainWindow):

		def __init__(self):
			super().__init__()
			self.setWindowTitle("Hello from PyQt6")
			self.graph = SimpeGraphWiget()
			self.graph.series["pos"].visible = True
			self.graph.series["torque"].visible = True
			self.graph.series["speed"].visible = True
			self.graph.series["current"].visible = True
			self.graph.series["temp"].visible = True
			self.graph.series["voltage"].visible = True

			self.setCentralWidget(self.graph)
			self.show()
			self.timer = QtCore.QTimer()
			self.timer.timeout.connect(self.onTimeout)
			self.timer.start(100)

		def onTimeout(self):
			self.graph.append_data(
				randint(0, 4000),
				randint(-1000, -600),
				randint(-600, -300),
				randint(-300, 300),
				randint(300, 600),
				randint(600, 1000)
			)

	app = QApplication(sys.argv)
	w = MainWindow()
	app.exec()

