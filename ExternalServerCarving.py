"""
Start server and wait for incoming commands from other external programms (mainly ARPES GUI). Once the signal is obtained
- move the manipulator, when finished - signal back to external program.
@author: Victor Rogalev
"""
from PyQt5.QtCore import QObject, QRunnable, QThreadPool, QTimer, pyqtSignal, pyqtSlot
import time
import socket


class WorkerSignals(QObject):
    incoming_command_signal = pyqtSignal(str)


class ExternalServer(QRunnable):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.signals = WorkerSignals()
        self.host = socket.gethostbyname(socket.gethostname())  # temporary
        self.port = 63210
        print('new server initialized')

    @pyqtSlot()
    def run(self):
        """
        Main functions of server:
        1. start server waiting for clients to connect, if connected - get commands, if
        """
        self.s = socket.socket()  # Create a socket object
        self.s.bind((self.host, self.port))  # Bind to the port
        self.s.listen()  # Enable client connection.
        print('Server started!\n Waiting for clients...')

        """ Here comes infinite loop constantly trying to accept connection """
        while True:
            print('now will try to accept connection')
            try:
                self.c, self.addr = self.s.accept()  # Establish connection with client.
                print('Got connection from', self.addr)
                # _thread.start_new_thread(self.on_new_client, (c,))
                self.on_new_client(self.c)
                time.sleep(1)  # seconds
            except:
                pass

    def on_new_client(self, client):
        self.client = client
        while True:
            time.sleep(0.5)  # while loop discriminator - otherwise overload
            print ("waiting for incoming command")
            msg = self.client.recv(1024)
            if msg.decode():
                print("received from host: ", msg.decode())
                reply = "OK, "+msg.decode()
                self.client.send(reply.encode())
                self.signals.incoming_command_signal.emit(msg.decode())
            else:
                pass

        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()

    def command_finished(self):
        try:
            msg = "finished"
            self.c.send(msg.encode())
        except Exception as e:
            print (e)
            pass
