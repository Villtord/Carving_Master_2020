"""
Server version: {tcp_gateway,{ok,"4.67.1-r91102","1.0"}}.
Last update: 23 June 2020
Created: 08 June 2020

UI to control SPECS Carving manipulator

@author: Victor Rogalev
"""
from __future__ import unicode_literals
from PyQt5.QtWidgets import QWidget, QMessageBox, QMainWindow
from CarvingDriver import CarvingControlDriver
from CarvingBasicUI import Ui_MainWindow
from CameraClass import get_image
from PyQt5 import QtGui, QtCore
import logging
import gc
import numpy as np

global god_mode_flag

god_mode_flag = False


def are_you_sure_decorator(func):
    def wrapper(self, *args):
        if not god_mode_flag:
            button_reply = QMessageBox.question(self, 'PyQt5 message', "ARE YOU SURE???",
                                                QMessageBox.Yes | QMessageBox.No,
                                                QMessageBox.No)
            if button_reply == QMessageBox.Yes:
                func(self, *args)
        else:
            func(self, *args)

    return wrapper


class CarvingControlApp(Ui_MainWindow):
    # class CarvingControlApp(QWidget, Ui_MainWindow):
    global god_mode_flag

    def __init__(self, *args):
        # super().__init__(self, *args, **kwargs)
        super(self.__class__, self).__init__(self, *args)
        self.initialize()
        self.start_flag = True  # flag to update abs move axis lineedits at first start of the GUI
        self.shift_value = 0.0  # default shift value for axes

    def initialize(self):

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
                lambda a, b=position_name: self.set_predefined_positions(b))

        """Connect signals and slots from abs move axis buttons - moves only one axis where return was pressed!"""
        for axis_name in self.axes_names_tuple:
            self.axes_objects_dict[axis_name][2].returnPressed.connect(lambda b=axis_name: self.move_axis_abs(b))

        """Connect signals and slots from relative move axis buttons"""
        for axis_name in self.axes_names_tuple:
            self.axes_objects_dict[axis_name][3].clicked.connect(lambda a, b=axis_name: self.move_axis_rel(b, "<<"))
            self.axes_objects_dict[axis_name][5].clicked.connect(lambda a, b=axis_name: self.move_axis_rel(b, ">>"))

        """Connect stop button"""
        self.predefined_buttons_objects_dict[self.predefined_buttons_names_tuple[4]].clicked.connect(
            lambda: self.MyCarving.stop_manipulator())

        """Connect toggle God Mode action"""
        self.toggle_mode_action.triggered.connect(self.toggle_god_mode)
        self.toggle_god_mode(False)

        self.MyCarving.actual_position_signal.connect(self.update_positions)
        self.MyCarving.new_position_signal.connect(self.update_target_positions)
        self.MyCarving.start()  # start this separate thread to get positions

        "Connect camera and show images - image settings can be defined in basler pylon sdk"
        self.image = get_image()
        new_image = QtGui.QPixmap("saved_pypylon_img.jpeg")
        self.camera_image.setPixmap(new_image.scaled(500,400,QtCore.Qt.KeepAspectRatio))
        # self.camera_image.setFixedWidth(400)
        self.camera_image.setFixedHeight(400)

        gc.collect()

    def toggle_god_mode(self, state):
        global god_mode_flag
        god_mode_flag = state
        if god_mode_flag:
            self.layoutWidget.setStyleSheet("background-color:pink;")
            self.predefined_buttons_objects_dict[self.predefined_buttons_names_tuple[4]].setStyleSheet("background"
                                                                                                       "-color:green;")
            for axis_name in self.axes_names_tuple:
                self.axes_objects_dict[axis_name][2].setStyleSheet("background-color:white;")
                self.axes_objects_dict[axis_name][4].setStyleSheet("background-color:white;")
        else:
            self.layoutWidget.setStyleSheet("background-color:grey;")
            self.predefined_buttons_objects_dict[self.predefined_buttons_names_tuple[4]].setStyleSheet(
                "background-color:red;")
            for axis_name in self.axes_names_tuple:
                self.axes_objects_dict[axis_name][2].setStyleSheet("background-color:white;")
                self.axes_objects_dict[axis_name][4].setStyleSheet("background-color:white;")

    "Are you sure confirmation window is not shown only if god_mode_flag is True"
    @are_you_sure_decorator
    def move_axis_abs(self, axis_name):
        """Move one axis to the desired position from LineEdit field.
        New position must be a list of 6 values (float,None) separated by , .
        NONE value means no command to move this axis."""
        "replace comma with dot"
        if "," in self.axes_objects_dict[axis_name][2].text():
            self.axes_objects_dict[axis_name][2].setText(
                self.axes_objects_dict[axis_name][2].text().replace(",", "."))
        "construct new position vector but check before the backlash settings:if on move first to compensate backlash"
        try:
            if self.backlash_radiobutton.isChecked():
                if float(self.axes_objects_dict[axis_name][2].text()) < self.axes_positions[
                    self.axes_names_tuple.index(axis_name)]:
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

    @are_you_sure_decorator
    def move_axis_rel(self, axis_name, direction):
        print("axis_name ", axis_name)
        print("direction ", direction)
        """Shift position along the axis by user-defined value left or right"""
        "replace comma with dot"
        if "," in self.axes_objects_dict[axis_name][4].text():
            self.axes_objects_dict[axis_name][4].setText(
                self.axes_objects_dict[axis_name][4].text().replace(",", "."))
        "get the shift value"
        try:
            self.shift_value = float(self.axes_objects_dict[axis_name][4].text())
        except Exception as e:
            logging.exception(e)
            print('error reading shift value from LineEdit for ' + axis_name)
            self.shift_value = 0.0
            pass
        "get new position value"
        if direction == "<<":
            self.target_shift_position = self.axes_positions[self.axes_names_tuple.index(axis_name)] - self.shift_value
        else:
            self.target_shift_position = self.axes_positions[self.axes_names_tuple.index(axis_name)] + self.shift_value

        "construct new position vector but check before the backlash settings:if on move first to compensate backlash"
        try:
            if self.backlash_radiobutton.isChecked():
                if self.target_shift_position < float(
                        self.axes_objects_dict[axis_name][1].text()):
                    backlash_position = tuple(
                        [self.target_shift_position - 0.5 if name == axis_name else None
                         for name in self.axes_names_tuple])
                    self.MyCarving.set_position(backlash_position)
            new_position = tuple([self.target_shift_position if name == axis_name else None
                                  for name in self.axes_names_tuple])
            print(new_position)
            self.MyCarving.set_position(new_position)
        except Exception as e:
            logging.exception(e)
            print('error reading new position value from LineEdit for abs move of axis' + axis_name)
            pass
        # get the current axis position
        # move axis accordingly

    "Are you sure confirmation window is not shown only if god_mode_flag is True"
    @are_you_sure_decorator
    def set_predefined_positions(self, position_name):
        self.MyCarving.set_position(self.predefined_positions_dict[position_name])

    def update_positions(self, reply):
        """ Update manipulator positions once the new_position_signal signal recieved from MyCarving"""
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
