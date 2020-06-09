"""Low-level driver for carving motor"""
# -*- coding: utf-8 -*-
"""
Last update: 08 June 2020
Created: 08 June 2020

@author: Victor Rogalev
"""
import PyQt5.QtCore
import socket
import select
import logging

import sys

import PyQt5.QtWidgets



def main():
    app = PyQt5.QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    My_Carving_Object = CarvingNetworkControl("localhost", 40002)
    My_Carving_Object.start()
    sys.exit(app.exec_())  # Handle exit case


class CarvingNetworkControl(PyQt5.QtCore.QThread):

    def __init__(self, host, port, **kwargs):
        super(self.__class__, self).__init__()
        print("initializing")
        self.connection_flag = False
        self.host = host
        self.port = port
        print(self.host, self.port)
        """Every self.timing [ms] checking connection with server and trying to get positions"""
        self.timing = 1000
        self.timer_x = PyQt5.QtCore.QTimer(self)
        self.timer_x.timeout.connect(self.get_position)
        self.timer_x.start(self.timing)

    def get_position(self):
        print("in get_pos loop")





if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function