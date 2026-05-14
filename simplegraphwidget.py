import math

from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QWidget
from collections import deque


# Must match the polling cadence in mainwindow.py; together with BUFFER_LEN
# they determine how much history the graph shows (300 * 30ms = 9s at zoom 0).
SAMPLE_PERIOD_MS = 30
BUFFER_LEN = 300


def mapping(val, in_min, in_max, out_min, out_max):
	return out_min + (val - in_min) * (out_max - out_min) / (in_max - in_min)


class Series:

	def __init__(self, maxlen, color, gain, min, max, step):
		self.buffer = deque(maxlen=maxlen)
		self.color = color
		self.gain = gain
		self.min = min
		self.max = max
		self.step = step
		self.visible = False


	def append(self, raw):
		# Auto-expand the axis bounds monotonically (never shrink) so the
		# trace stays inside the plot region. Rounded to a multiple of
		# `step` so the bound lands on a "clean" value for the axis label.
		self.buffer.append(raw)
		v = raw * self.gain
		if v > self.max:
			self.max = math.ceil(v / self.step) * self.step
		elif v < self.min:
			self.min = math.floor(v / self.step) * self.step


	def plot(self, w, scale, hoffset, y_min, y_max):
		points = []
		for i, v in enumerate(self.buffer):
			# Shift indices so a partially-full buffer anchors its newest
			# sample to the right edge (x=w+hoffset) instead of stretching
			# the few existing samples across the whole plot.
			x = mapping(self.buffer.maxlen - len(self.buffer) + i, 0, self.buffer.maxlen, w - w * scale + hoffset, w + hoffset)
			y = mapping(v * self.gain, self.min, self.max, y_min, y_max)
			points += [(x, y)]
		return points


class SimpleGraphWidget(QWidget):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.series = {
			"pos":     Series(BUFFER_LEN, QtGui.QColor("black"),       1.0,    0, 4095, 500),
			"torque":  Series(BUFFER_LEN, QtGui.QColor("red"),         1.0, -100,  100,  50),
			"speed":   Series(BUFFER_LEN, QtGui.QColor("green"),       1.0, -500,  500, 500),
			"current": Series(BUFFER_LEN, QtGui.QColor("cyan"),        1.0,    0,  500, 100),
			"temp":    Series(BUFFER_LEN, QtGui.QColor("yellowgreen"), 1.0,   20,   30,   5),
			"voltage": Series(BUFFER_LEN, QtGui.QColor("magenta"),     1.0,   90,  130,  10),
		}

		self.down_limit = 0
		self.up_limit = 0
		self.horizontal = 0
		self.zoom = 1

		self.label_font = QtGui.QFont()
		self.label_font.setPointSize(8)

		self.timer_ = QtCore.QTimer(self)
		self.timer_.timeout.connect(self.onTimeout)
		self.timer_.start(20)
		#self.phase_ = 0.0


	def reset_data(self):
		for s in self.series:
			self.series[s].buffer.clear()


	def append_data(self, pos, torque, speed, current, temp, voltage):
		self.series["pos"].append(pos)
		self.series["torque"].append(torque)
		self.series["speed"].append(speed)
		self.series["current"].append(current)
		self.series["temp"].append(temp)
		self.series["voltage"].append(voltage)


	def onTimeout(self):
		self.update()


	def paintEvent(self, event):
		painter = QtGui.QPainter(self)

		w = self.width()
		h = self.height()

		fm = QtGui.QFontMetrics(self.label_font)
		font_h = fm.height()
		visible_series = [s for s in self.series.values() if s.visible]
		margin_bottom = font_h + 4
		plot_h = h - margin_bottom

		# Below this height, plot_h // 11.5 rounds down to 0 and the
		# zoom/grid math divides by zero. Qt occasionally repaints widgets
		# at near-zero size (hide/show, layout transients) so just bail.
		if w <= 0 or plot_h < 12:
			return

		grid_pen = QtGui.QPen()
		grid_pen.setStyle(QtCore.Qt.PenStyle.CustomDashLine)
		grid_pen.setDashPattern([12, 4])
		grid_pen.setWidthF(1.0)
		grid_pen.setColor(QtGui.QColor('lightGray'))
		painter.setPen(grid_pen)

		# Zoom and horizontal sliders are in [0, 100]. Zoom controls both
		# the visible time window (scale) and grid line spacing; hoffset
		# pans the view to the right (showing older data).
		max_scale = 6.0
		min_grid_size = plot_h // 11.5  # square-ish cells: vertical spacing drives horizontal too
		max_grid_size = min_grid_size * max_scale
		grid_size = mapping(self.zoom, 0.0, 100.0, min_grid_size, max_grid_size)
		hoffset = mapping(self.horizontal, 0.0, 100, 0, w)
		scale = mapping(self.zoom, 0.0, 100.0, 1.0, max_scale)

		# Vertical gridlines drawn right-to-left from x=w; collected so the
		# X-axis time-label pass below can reuse the same positions.
		gridline_xs = []
		for i in range(int(w // grid_size) + 1):
			x = w - i * grid_size
			if x >= 0:
				painter.drawLine(int(x), 0, int(x), int(plot_h))
				gridline_xs.append(x)

		# 11 horizontal gridlines centered on plot_h/2. grid_y_min/max are
		# the top and bottom gridlines (smaller y = higher on screen) and
		# define the rectangle that each series' min/max maps into.
		for i in range(11):
			y = plot_h // 2 + (i - 5) * (plot_h // 11.5)
			painter.drawLine(0, int(y), int(w), int(y))

		grid_y_min = plot_h // 2 - 5 * (plot_h // 11.5)
		grid_y_max = plot_h // 2 + 5 * (plot_h // 11.5)

		pen = QtGui.QPen()
		pen.setWidthF(1.2)
		painter.setPen(pen)

		painter.setRenderHint(painter.RenderHint.Antialiasing, True)
		for s in visible_series:
			pen.setColor(s.color)
			painter.setPen(pen)
			points = s.plot(w, scale, hoffset, grid_y_max, grid_y_min)
			if not points:
				continue
			# drawPath() is hideously slow, use drawLine() instead
			(x0, y0) = points[0]
			for (x1, y1) in points[1:]:
				painter.drawLine(int(x0), int(y0), int(x1), int(y1))
				x0, y0 = x1, y1

		# Torque limit overlays: drawn as a symmetric pair (+/-) against
		# a fixed -1000..1000 axis (the torque series' native range), even
		# if the torque series isn't currently visible. Skip lines that
		# would fall outside that range — otherwise they'd render off-grid.
		for limit in [self.up_limit, self.down_limit]:
			if not limit:
				continue
			pen.setColor(QtGui.QColor('plum'))
			painter.setPen(pen)
			for l in (limit, -limit):
				if -1000 <= l <= 1000:
					y = mapping(l, -1000, 1000, grid_y_max, grid_y_min)
					painter.drawLine(0, int(y), int(w), int(y))

		painter.setRenderHint(painter.RenderHint.Antialiasing, False)
		painter.setFont(self.label_font)

		# X-axis time labels: walk gridlines right-to-left so the rightmost
		# label ("0.0s") always wins; subsequent labels are only drawn if
		# they don't overlap the previous one (4 px gap).
		text_pen = QtGui.QPen(QtGui.QColor('black'))
		painter.setPen(text_pen)
		label_y = int(plot_h + font_h - 2)
		last_label_left = float('inf')
		for x in sorted(gridline_xs, reverse=True):
			samples_from_right = (w + hoffset - x) / (w * scale) * BUFFER_LEN
			time_sec = -samples_from_right * SAMPLE_PERIOD_MS / 1000.0
			if time_sec == 0:
				time_sec = 0.0  # collapse "-0.0" to "0.0"
			label = f"{time_sec:.1f}s"
			label_w = fm.horizontalAdvance(label)
			label_x = int(x - label_w / 2)
			if label_x + label_w > w:
				label_x = w - label_w
			if label_x < 0:
				label_x = 0
			if label_x + label_w + 4 < last_label_left:
				painter.drawText(label_x, label_y, label)
				last_label_left = label_x

		# Y-axis labels: each visible series gets up to three inline labels
		# in its own colour — current value (rightmost visible sample),
		# data max, and data min. Labels are anchored to the point they
		# describe so the reader can match a value to a peak at a glance.
		#
		# Two passes: collect candidate (priority, ...) tuples, then draw
		# in priority order with overlap avoidance. priority 0 (current)
		# wins ties because it's the value users care about most; priority
		# 1 (min/max) may be skipped if no overlap-free slot is available.
		pending = []
		for s in visible_series:
			if not s.buffer:
				continue
			buf = s.buffer
			# Only consider samples whose x lands inside the visible plot
			# rect — zoom>1 + pan can push older samples off-screen, and
			# their extrema would otherwise produce labels at the edges.
			visible_pts = []
			for i, v in enumerate(buf):
				x = mapping(buf.maxlen - len(buf) + i, 0, buf.maxlen, w - w * scale + hoffset, w + hoffset)
				if 0 <= x <= w:
					visible_pts.append((x, v))
			if not visible_pts:
				continue

			# Rightmost-on-ties (>= / <=) so a flat plateau labels at its
			# most recent point rather than its first.
			cur_idx = len(visible_pts) - 1
			max_idx = 0
			min_idx = 0
			for i, (_, v) in enumerate(visible_pts):
				if v >= visible_pts[max_idx][1]:
					max_idx = i
				if v <= visible_pts[min_idx][1]:
					min_idx = i
			cur_x, cur_v = visible_pts[cur_idx]
			max_x, max_v = visible_pts[max_idx]
			min_x, min_v = visible_pts[min_idx]
			# Convert raw buffer values to axis-space once (the gain factor
			# is identity today but the field is wired through for the
			# follow-up unit-conversion work).
			cur_d = cur_v * s.gain
			max_d = max_v * s.gain
			min_d = min_v * s.gain
			cur_y = mapping(cur_d, s.min, s.max, grid_y_max, grid_y_min)
			max_y = mapping(max_d, s.min, s.max, grid_y_max, grid_y_min)
			min_y = mapping(min_d, s.min, s.max, grid_y_max, grid_y_min)

			pending.append((0, s.color, str(int(round(cur_d))), cur_x, cur_y))
			# Skip min/max labels when the trace is near-flat (extrema
			# within one font height) or when an extremum coincides with
			# the current-value point — the current label already covers it.
			if abs(max_y - min_y) >= font_h:
				if max_idx != cur_idx:
					pending.append((1, s.color, str(int(round(max_d))), max_x, max_y))
				if min_idx != cur_idx:
					pending.append((1, s.color, str(int(round(min_d))), min_x, min_y))

		pending.sort(key=lambda l: l[0])
		drawn_rects = []
		for _, color, label, x_pt, y_pt in pending:
			lw = fm.horizontalAdvance(label)
			lx = max(0, min(int(x_pt - lw / 2), w - lw))
			# Try "above the point" first (preferred for upward extrema),
			# fall back to "below". If both collide with an already-drawn
			# label, skip this label entirely.
			candidates = [
				(lx, int(y_pt - 4 - font_h), lx + lw, int(y_pt - 4)),
				(lx, int(y_pt + 1), lx + lw, int(y_pt + 1 + font_h)),
			]
			for rect in candidates:
				x1, y1, x2, y2 = rect
				if y1 < 0 or y2 > plot_h:
					continue
				if any(not (x2 <= r[0] or x1 >= r[2] or y2 <= r[1] or y1 >= r[3]) for r in drawn_rects):
					continue
				text_pen.setColor(color)
				painter.setPen(text_pen)
				painter.drawText(x1, y2 - 2, label)
				drawn_rects.append(rect)
				break


if __name__ == "__main__":

	import sys
	from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton
	from random import randint


	class MainWindow(QMainWindow):

		def __init__(self):
			super().__init__()
			self.setWindowTitle("Hello from PyQt6")
			self.graph = SimpleGraphWidget()
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

