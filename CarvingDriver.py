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
    actual_position_signal = PyQt5.QtCore.pyqtSignal('QString')
    new_position_signal = PyQt5.QtCore.pyqtSignal('PyQt_PyObject')

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
                print(self.send_reply)
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
                        print("{req,'MCU8',go_online}. failed")
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
#        self.start_timer()

    def start_timer(self):
        """Every self.timing [ms] checking connection with server and trying to get positions"""
        self.timing = 2000
        self.timer_x = PyQt5.QtCore.QTimer(self)
        self.timer_x.timeout.connect(self.get_position)
        self.timer_x.start(self.timing)

    def stop_manipulator(self):
        self.timer_x.stop()
        self.send_command("{req, 'MCU8', stop}.\r\n")
        self.timer_x.start(self.timing)

    def get_position(self):
        """ Get axis positions from MCU8 """
        actual_positions = self.send_command("{req,'MCU8',get_position}.\r\n")
#        actual_positions = "{'MCU8',{ok,[{axis_pos,0,8.000244140625},{axis_pos,1,-7.999755859375},{axis_pos,2,202.00006103515625},{axis_pos,3,-130.00079013677276},{axis_pos,4,0.0},{axis_pos,5,0.0}]}}"
        self.actual_position_signal.emit(actual_positions)

    @property
    def get_state(self):
        """Get manipulator state: idle or busy"""
        carving_state = [False if "idle" in self.send_command("{req,'MCU8',get_state}.\r\n") else True]
        return carving_state

    def set_position(self, new_position):
        """
        :type new_position: list
        Position must be a list of 6 values (float,None) separated by , . NONE value means no command to move this axis.
        """
        self.timer_x.stop()
        self.new_position = new_position
        if None not in self.new_position:
            self.new_position_signal.emit(self.new_position)
        new_command = "{req,'MCU8',{set_position,["
        for i in range(len(self.new_position)):
            if self.new_position[i] is not None:
                new_command += '{axis_pos,' + f'{i},' + '{:.5f}'.format(self.new_position[i]) + '},'
        final_command = new_command[:-1] + "]}}.\r\n"
        self.send_command(final_command)
        self.timer_x.start(self.timing)

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
                print("no send reply from server")
                self.send_reply = ""
            loop_flag = True
            while loop_flag:
                timeout = 0.005
                ready = select.select([self.mySocket], [], [], timeout)
                if ready[0]:
                    self.wait_reply = self.mySocket.recv(1000).decode()
                else:
                    print("no wait reply from server")
                    self.wait_reply = ""
                    loop_flag = False
            self.reply = self.send_reply + self.wait_reply
            print(self.reply)
        except Exception as e:
            logging.exception(e)
            self.reply = ""
            print('error sending/receiving a command from manipulator server')
            self.connection_flag = False
            pass
        return self.reply

    def close(self):
        self.stop_manipulator()
        try:
            self.mySocket.close()
        except:
            pass
        self.timer_x.stop()
        self.timer_x.deleteLater()
