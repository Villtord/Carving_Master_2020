"""
Server version: {tcp_gateway,{ok,"4.67.1-r91102","1.0"}}.
Last update: 09 June 2020
Created: 08 June 2020

A class which allows to talk to MCU8 motor control unit (SPECS) via TCP connection.
The reply is typically divided as follows:
0. Read 200 bytes, timeout 2 sec
1. Wait loop with read 1000 bytes, timeout 0.005 sec until timeout error
2. Optional for some commands: Wait loop with read 1000 bytes, timeout 0.01 sec

Timeout and byte size parameters taken from Labview example gateway in SPECS installation folder

@author: Victor Rogalev
"""
import PyQt5.QtCore
import PyQt5.QtWidgets
import sys
import socket
import select
import logging


class CarvingControlDriver(PyQt5.QtCore.QThread):
    new_value_signal = PyQt5.QtCore.pyqtSignal('QString')

    def __init__(self, host, port, **kwargs):
        """Initialize TCP connection and get the control ready
        :type host: string
        :type port: integer
        """
        super(self.__class__, self).__init__()
        self.connection_flag = False
        self.host = host
        self.port = port
        print('establishing connection with host, port', self.host, self.port)
        self.mySocket = socket.socket()
        """Initial socket connection - the reply is expected to be {tcp_gateway,{ok,"4.67.1-r91102","1.0"}}."""
        try:
            self.mySocket.connect((self.host, self.port))
            self.mySocket.setblocking(0)
            timeout = 2
            ready = select.select([self.mySocket], [], [], timeout)
            if ready[0]:
                self.send_reply = self.mySocket.recv(200).decode()
                print (self.send_reply)
            else:
                self.send_reply = ""
                print("no reply from server during socket connection")
            if "{tcp_gateway,{ok,\"4.67.1-r91102\",\"1.0\"}}." in self.send_reply:
                self.connection_flag = True
        except Exception as e:
            logging.exception(e)
            self.connection_flag = False
            self.mySocket.close()
            print('connection failed, socket closed')

        """Sequence of commands to get the manipulator control ready"""
        if self.connection_flag:
            try:
                local_reply = self.send_command("{req,'MCU8',clear_owner}.\r\n")
            except Exception as e:
                logging.exception(e)
                print("{req,'MCU8',clear_owner}. failed")
                local_reply = ""
                pass
            if "ok" in local_reply:
                try:
                    local_reply = self.send_command("{req,'MCU8',force_owner}.\r\n")
                except Exception as e:
                    logging.exception(e)
                    print("{req,'MCU8',force_owner}. failed")
                    local_reply = ""
                    pass
                if "ok" in local_reply:
                    try:
                        local_reply = self.send_command("{req,'MCU8',go_online}.\r\n")
                    except Exception as e:
                        logging.exception(e)
                        print ("{req,'MCU8',go_online}. failed")
                        local_reply = ""
                        pass
                    if "ok" in local_reply:
                        try:
                            local_reply = self.send_command("{req,'MCU8',get_state}.\r\n")
                            self.start_timer()
                        except Exception as e:
                            logging.exception(e)
                            print("{req,'MCU8',get_state}. failed")
                            local_reply = ""
                            pass

    def start_timer(self):
        """Every self.timing [ms] checking connection with server and trying to get positions"""
        self.timing = 1000
        self.timer_x = PyQt5.QtCore.QTimer(self)
        self.timer_x.timeout.connect(self.get_position)
        self.timer_x.start(self.timing)

    def stop_manipulator(self):
        self.timer_x.stop()
        self.send_command("{req, 'MCU8', stop}.\r\n")
        self.timer_x.start(self.timing)

    def get_position(self):
        """ Get axis positions from MCU8 """
        self.send_command("{req,'MCU8',get_position}.\r\n")

    @property
    def get_state(self):
        """Get manipulator state: idle or busy"""
        self.carving_state = [False if "idle" in self.send_command("{req,'MCU8',get_state}.\r\n") else True]
        return self.carving_state

    def set_position(self, axis, position):
        """
        :type axis, position: list
        """
        self.axis = axis
        self.position = position
        final_command = ""
        new_command = "{req,'MCU8',{set_position,["
        for i in range(len(axis)):
            new_command += "{axis_pos,"+f'{self.axis[i]},{self.position[i]}'+"},"
        final_command = new_command[:-1]+"]}}.\r\n"
        self.send_command(final_command)

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
        self.new_value_signal.emit(self.reply)
        return self.reply

    def close(self):
        self.stop_manipulator()
        try:
            self.mySocket.close()
        except:
            pass
        self.timer_x.stop()
        self.timer_x.deleteLater()
