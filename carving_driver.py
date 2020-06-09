"""Low-level driver for carving motor"""
# -*- coding: utf-8 -*-
"""
Last update: 09 June 2020
Created: 08 June 2020

@author: Victor Rogalev
"""
import PyQt5.QtCore
import PyQt5.QtWidgets
import sys
import socket
import select
import logging


class CarvingNetworkControl(PyQt5.QtCore.QThread):
connection_flag: bool
    new_value_trigger = PyQt5.QtCore.pyqtSignal('QString')

    def __init__(self, host, port, **kwargs):
        """Initialize TCP connection and get the control ready"""
        super(self.__class__, self).__init__()
        self.connection_flag = False
        self.host = host
        self.port = port
        print('establishing connection with host ', self.host)
        self.mySocket = socket.socket()
        """The recent SPECS update uses this send and wait protocol - not clear why yet"""
        """Timeout and byte size parameters taken from Labview example gateway in SPECS folder"""
        try:
            self.mySocket.connect((self.host, self.port))
            print(self.mySocket.getsockname())
            self.mySocket.setblocking(0)
            timeout = 2
            ready = select.select([self.mySocket], [], [], timeout)
            if ready[0]:
                self.send_reply = self.mySocket.recv(200).decode()
            else:
                self.send_reply = ""
                print("no reply from server")
            loop_flag = True
            while loop_flag:
                timeout = 0.005
                ready = select.select([self.mySocket], [], [], timeout)
                if ready[0]:
                    self.wait_reply = self.mySocket.recv(1000).decode()
                else:
                    print ("no reply from server")
                    self.wait_reply = ""
                    loop_flag = False
            self.connection_flag = True
            self.reply = self.send_reply + self.wait_reply
        except Exception as e:
            logging.exception(e)
            self.reply = ""
            self.connection_flag = False
            self.mySocket.close()
            print('no connection')
        print('Received from server: ' + self.reply)
        """Sequence of commands to get the manipulator control ready"""
        if self.send_command("{req,'MCU8',clear_owner}.\r\n")
        self.send_command("{req,'MCU8',force_owner}.\r\n")
        self.send_command("{req,'MCU8',go_online}.\r\n")
        self.send_command("{req,'MCU8',get_state}.\r\n")

        self.start_timer()

    def start_timer(self):
        """Every self.timing [ms] checking connection with server and trying to get positions"""
        self.timing = 2000
        self.timer_x = PyQt5.QtCore.QTimer(self)
        self.timer_x.timeout.connect(self.get_position)
        self.timer_x.start(self.timing)

    def stop_manipulator(self):
        self.timer_x.stop()
        self.send_command("{req, 'MCU8', stop}.")
        self.timer_x.start(self.timing)

    def get_position(self):
        """ Get axis positions from MCU8 """
        self.send_command("{req,'MCU8',get_position}.\r\n")

    def send_command(self, command):
        """ Ask server and receive reply """
        try:
            self.message = command
            print('attempt to send: ', self.message)
            self.mySocket.setblocking(0)

            self.mySocket.send(self.message.encode())
            print('message send')
            timeout = 2
            ready = select.select([self.mySocket], [], [], timeout)
            if ready[0]:
                self.send_reply = self.mySocket.recv(200).decode()
            else:
                print ("no reply from server")
                self.send_reply = ""
            loop_flag = True
            while loop_flag:
                timeout = 0.005
                ready = select.select([self.mySocket], [], [], timeout)
                if ready[0]:
                    self.wait_reply = self.mySocket.recv(1000).decode()
                else:
                    print ("no reply from server")
                    self.wait_reply = ""
                    loop_flag = False
            self.reply = self.send_reply + self.wait_reply
        except Exception as e:
            logging.exception(e)
            self.reply = ""
            print('error sending/receiving a command from manipulator server')
            self.connection_flag = False
            pass
        self.new_value_trigger.emit(self.reply)
        return self.reply

    def close(self):
        try:
            self.mySocket.close()
        except:
            pass
        self.timer_x.stop()
        self.timer_x.deleteLater()


def main():
    app = PyQt5.QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    My_Carving_Object = CarvingNetworkControl("localhost", 40002)
    My_Carving_Object.start()
    sys.exit(app.exec_())  # Handle exit case

if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function
