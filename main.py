#!/usr/bin/env python

from PyQt6.QtWidgets import QApplication
from mainwindow import MainWindow

import sys

app = QApplication(sys.argv)
app.setOrganizationName("feetech-servo-tool")
app.setApplicationName("feetech-servo-tool")

window = MainWindow()
window.show()

app.exec()
