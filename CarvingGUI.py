"""
Server version: {tcp_gateway,{ok,"4.67.1-r91102","1.0"}}.
Last update: 09 June 2020
Created: 08 June 2020

GUI to control SPECS Carving manipulator

@author: Victor Rogalev
"""

import sys
import PyQt5.QtWidgets
import CarvingUI


def main():
    app = PyQt5.QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    form = CarvingUI.CarvingControlApp()  # We set the form
    form.setWindowTitle('Carving Master 2020')  # Change window name
    # form.resize(500, 500)  # Resize the form
    form.show()  # Show the form
    sys.exit(app.exec_())  # Handle exit case


if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function