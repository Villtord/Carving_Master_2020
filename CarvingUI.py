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
from CarvingBasicUI import Ui_MainWindow
from PyQt5 import QtCore, QtWidgets
import logging
import gc


class CarvingControlApp(QWidget, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        """     Imported from CarvingBasicUI:
                self.axes_names_tuple = (" X ", " Y ", " Z ", "Pol", "Azi", "Tilt" )
                self.axes_objects_dict = {" X ":{0:QLabelObject, 1:QLabelObject, 2:QLineEditObject,
                                                 3:QPushButtonObject, 4:QLineEditObject, 5:QPushButtonObject},
                                          " Y ":{0:QLabelObject, 1:QLabelObject, 2:QLineEditObject,
                                                 3:QPushButtonObject,4:QLineEditObject, 5:QPushButtonObject}...}
                self.predefined_buttons_names_tuple = (" ARPES ", " SCREW ", " EXCH ", " FREE ", " STOP ")
                self.predefined_buttons_objects_dict = {" ARPES ":QPushButtonObject," SCREW ":QPushButtonObject},..."""

        self.predefined_positions_dict = {self.predefined_buttons_names_tuple[0]:(0.0, 0.0, 0.0, 0.0, 90.0, 0.0),
                                          self.predefined_buttons_names_tuple[1]:(0.0, 0.0, 215.0, -45.0, 0.0, 0.0),
                                          self.predefined_buttons_names_tuple[2]:(0.0, 0.0, 202.0, -130.0, 0.0, -17.0),
                                          self.predefined_buttons_names_tuple[3]:(8.0, -8.0, 202.0, -130.0, 0.0, 0.0)}

        """Connect signals and slots from predefined buttons/labels"""
        for i in range(len(self.predefined_buttons_names_tuple)-1):
            position_name = self.predefined_buttons_names_tuple[i]
            """direct construction of lambda with argument and extra 
            variable a - otherwise b results in False/True??? """
            self.predefined_buttons_objects_dict[position_name].clicked.connect(lambda a,b=self.predefined_positions_dict[position_name]: self.MyCarving.set_position(b))

        """ Connect stop button """
        self.predefined_buttons_objects_dict[self.predefined_buttons_names_tuple[4]].clicked.connect(lambda: self.MyCarving.stop_manipulator())

        """ Make a separate thread to monitor/control Carving """
        self.MyCarving = CarvingControlDriver("localhost", 40002)
        self.MyCarving.positions_signal.connect(self.update_positions)
        self.MyCarving.start()  # start this separate thread to get pressure
        gc.collect()

    def update_positions(self, reply):
        """ Update manipulator positions """
        self.reply = reply
        if "ok" in self.reply:
            print(self.reply)
            self.axes_positions = [float(i.split(',')[-1]) for i in self.reply.split('}')[:-3]]
            print(self.axes_positions)
            for i in range(len(self.axes_names_tuple)):
                try:
                    self.axes_objects_dict[self.axes_names_tuple[i]][1].setText("{:1.3f}".format(self.axes_positions[i]))
                except Exception as e:
                    logging.exception(e)
                    pass
        else:
            print("no/wrong reply from MCU while updating positions")
            pass
        gc.collect()

    def resizeEvent(self, evt):
        """ Possibility to resize GUI window """
        font = self.font()
        font.setPixelSize(self.height() * 0.7)
        # self.label.setFont(font)
        # self.label.setGeometry(0, 0, self.width(), self.height())
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
