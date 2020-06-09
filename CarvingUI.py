"""
Server version: {tcp_gateway,{ok,"4.67.1-r91102","1.0"}}.
Last update: 09 June 2020
Created: 08 June 2020

UI to control SPECS Carving manipulator

@author: Victor Rogalev
"""
from __future__ import unicode_literals
from PyQt5.QtWidgets import QWidget
from CarvingDriver import CarvingControlDriver
from PyQt5 import QtCore, QtWidgets
import logging
import gc


class Ui_MainWindow(object):
    def __init__(self):
        self.label = QtWidgets.QLabel(self)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(380, 150)
        self.label.setGeometry(QtCore.QRect(0, 0, MainWindow.width(), MainWindow.height()))
        self.label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label.setLineWidth(1)
        self.label.setText("")
        self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")


class CarvingControlApp(QWidget, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        """ Special background color and start value for temperature GUI """

        self.label.setText("starting carving control")
        """ Make a separate thread to accept pressure values from server """
        self.MyCarving = CarvingControlDriver("localhost", 40002)
        self.MyCarving.new_value_signal.connect(self.update_screen)
        self.MyCarving.start()  # start this separate thread to get pressure
        gc.collect()

    def update_screen(self, reply):
        """ Update window
        """
        self.reply = reply
        try:
            self.label.setText(self.reply)
        except Exception as e:
            logging.exception(e)
            pass
        gc.collect()

    def resizeEvent(self, evt):
        """ Possibility to resize GUI window """
        font = self.font()
        font.setPixelSize(self.height() * 0.7)
        self.label.setFont(font)
        self.label.setGeometry(0, 0, self.width(), self.height())
        gc.collect()

    def __del__(self):
        try:
            self.MyCarving.close()
        except:
            pass
        self.MyCarving.timer_x.stop()
        self.MyCarving.timer_x.deleteLater()

    def closeEvent(self, event):
        try:
            self.MyCarving.close()
        except:
            pass
        self.MyCarving.timer_x.stop()
        self.MyCarving.timer_x.deleteLater()
