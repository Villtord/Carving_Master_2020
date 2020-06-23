"""
Server version: {tcp_gateway,{ok,"4.67.1-r91102","1.0"}}.
Last update: 23 June 2020
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
        """ Make a separate thread to monitor/control Carving """
        self.MyCarving = CarvingControlDriver("localhost", 40002)

        """     Imported from CarvingBasicUI:
                self.axes_names_tuple = (" X ", " Y ", " Z ", "Pol", "Azi", "Tilt" )
                self.axes_objects_dict = {" X ":{0:QLabelObject, 1:QLabelObject, 2:QLineEditObject,
                                                 3:QPushButtonObject, 4:QLineEditObject, 5:QPushButtonObject},
                                          " Y ":{0:QLabelObject, 1:QLabelObject, 2:QLineEditObject,
                                                 3:QPushButtonObject,4:QLineEditObject, 5:QPushButtonObject}...}
                self.predefined_buttons_names_tuple = (" ARPES ", " SCREW ", " EXCH ", " FREE ", " STOP ")
                self.predefined_buttons_objects_dict = {" ARPES ":QPushButtonObject," SCREW ":QPushButtonObject},..."""

        self.predefined_positions_dict = {self.predefined_buttons_names_tuple[0]: (0.0, 0.0, 0.0, 0.0, 90.0, 0.0),
                                          self.predefined_buttons_names_tuple[1]: (0.0, 0.0, 215.0, -45.0, 0.0, 0.0),
                                          self.predefined_buttons_names_tuple[2]: (0.0, 0.0, 202.0, -130.0, 0.0, -17.0),
                                          self.predefined_buttons_names_tuple[3]: (8.0, -8.0, 202.0, -130.0, 0.0, 0.0)}

        """Connect signals and slots from predefined buttons/labels"""
        for i in range(len(self.predefined_buttons_names_tuple) - 1):
            position_name = self.predefined_buttons_names_tuple[i]
            """direct construction lambda with argument and extra variable a - otherwise b results in False/True??? """
            self.predefined_buttons_objects_dict[position_name].clicked.connect(
                lambda a, b=self.predefined_positions_dict[position_name]: self.MyCarving.set_position(b))

        """Connect signals and slots from abs move axis buttons - moves only one axis where return was pressed!"""
        for axis_name in self.axes_names_tuple:
            self.axes_objects_dict[axis_name][2].returnPressed.connect(lambda b=axis_name: self.move_axis_abs(b))

        """Connect stop button"""
        self.predefined_buttons_objects_dict[self.predefined_buttons_names_tuple[4]].clicked.connect(
            lambda: self.MyCarving.stop_manipulator())

        self.start_flag = True  # flag to update abs move axis lineedits at first start of the GUI

        self.MyCarving.actual_position_signal.connect(self.update_positions)
        self.MyCarving.new_position_signal.connect(self.update_target_positions)
        self.MyCarving.start()  # start this separate thread to get pressure
        gc.collect()

    def move_axis_abs(self, axis_name):
        """Move one axis to the desired position from LineEdit field.
        New position must be a list of 6 values (float,None) separated by , .
        NONE value means no command to move this axis."""
        "replace comma with dot"
        if "," in self.axes_objects_dict[axis_name][2].text():
            self.axes_objects_dict[axis_name][2].setText(self.axes_objects_dict[axis_name][2].text().replace(",", "."))
        "construct new position vector but check before the backlash settings:if on move first to compensate backlash"
        try:
            if self.backlash_radiobutton.isChecked():
                if float(self.axes_objects_dict[axis_name][2].text()) < float(
                        self.axes_objects_dict[axis_name][1].text()):
                    backlash_position = tuple(
                        [float(self.axes_objects_dict[axis_name][2].text()) - 0.5 if name == axis_name else None
                         for name in self.axes_names_tuple])
                    self.MyCarving.set_position(backlash_position)
            new_position = tuple([float(self.axes_objects_dict[axis_name][2].text()) if name == axis_name else None
                                  for name in self.axes_names_tuple])
            self.MyCarving.set_position(new_position)
        except Exception as e:
            logging.exception(e)
            print('error reading new position value from LineEdit for abs move of axis' + axis_name)
            pass

    def update_positions(self, reply):
        """ Update manipulator positions """
        self.reply = reply
        if "ok" in self.reply:
            # print(self.reply)
            self.axes_positions = [float(i.split(',')[-1]) for i in self.reply.split('}')[:6]]
            # print(self.axes_positions)
            for i in range(len(self.axes_names_tuple)):
                try:
                    self.axes_objects_dict[self.axes_names_tuple[i]][1].setText(
                        "{:1.3f}".format(self.axes_positions[i]))
                except Exception as e:
                    logging.exception(e)
                    pass
            if self.start_flag:
                self.update_target_positions(self.axes_positions)
                self.start_flag = False
        else:
            print("no/wrong reply from MCU while updating positions")
            pass
        gc.collect()

    def update_target_positions(self, new_position):
        """Here we update abs axes move lineedits ones the new_position is received: mainly for predefined positions!"""
        self.new_target_position = new_position

        for i in range(len(self.axes_names_tuple)):
            self.axes_objects_dict[self.axes_names_tuple[i]][2].setText('{:.3f}'.format(self.new_target_position[i]))

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
