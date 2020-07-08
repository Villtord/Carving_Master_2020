"""
Server version: {tcp_gateway,{ok,"4.67.1-r91102","1.0"}}.
Last update: 10 June 2020
Created: 08 June 2020

Basic UI to control SPECS Carving manipulator

@author: Victor Rogalev
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QAction


class Ui_MainWindow(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        self.w = 300
        self.h = 500
        self.setGeometry(300, 300, self.w, self.h)
        self.my_menu_bar = self.menuBar()
        self.options_menu = self.my_menu_bar.addMenu('Options')
        # self.statusbar = self.statusBar()
        # self.statusbar.showMessage('Ready')

        self.toggle_mode_action = QAction('God Mode', self, checkable=True)
        self.toggle_mode_action.setStatusTip('Enable God Mode')
        self.toggle_mode_action.setChecked(False)
        self.options_menu.addAction(self.toggle_mode_action)

        self.setup_ui()

    def setup_ui(self):

        self.layoutWidget = QtWidgets.QWidget(self)
        # self.layoutWidget.setGeometry(QtCore.QRect(10, 10, self.w-10, self.h-10))
        self.layoutWidget.setObjectName("layoutWidget")
        self.layoutWidget.setStyleSheet("background-color:grey;")
        self.setCentralWidget(self.layoutWidget)

        self.MainVerticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.MainHorizontalLayout = QtWidgets.QHBoxLayout()

        """Create axes control labels/buttons and pack them into a dictionary self.axes_objects_dict which looks like
        {" X ":SingleAxisControlDict, " Y ":SingleAxisControlDict,...}"""
        self.VerticalLayoutXYZ = QtWidgets.QVBoxLayout()
        self.VerticalLayoutXYZ.setContentsMargins(0, 0, 0, 0)
        self.VerticalLayoutXYZ.setObjectName("VerticalLayoutXYZ")
        self.axes_names_tuple = (" X ", " Y ", " Z ",  "Pol", "Azi", "Tilt")
        self.axes_objects_dict = {}
        for i in range(len(self.axes_names_tuple)):
            self.SetAxisHorizontalLayout()
            self.SingleAxisControlDict[0].setText(self.axes_names_tuple[i])
            self.axes_objects_dict[self.axes_names_tuple[i]]=self.SingleAxisControlDict

        """Predefined positions and stop button vertical layout"""
        self.VerticalLayoutPredefined = QtWidgets.QVBoxLayout()
        self.VerticalLayoutPredefined.setContentsMargins(0, 0, 0, 0)
        self.predefined_buttons_names_tuple = (" ARPES ", " SCREW ", " EXCH ", " FREE ", " STOP ")
        self.predefined_buttons_objects_dict = {}
        for i in range(len(self.predefined_buttons_names_tuple)):
            self.predefined_buttons_objects_dict[self.predefined_buttons_names_tuple[i]]=self.SetPredefinedButtons()
            self.predefined_buttons_objects_dict[self.predefined_buttons_names_tuple[i]].setText(self.predefined_buttons_names_tuple[i])


        self.HorizontalLayoutPath = QtWidgets.QHBoxLayout()
        # self.HorizontalLayoutPath.setContentsMargins(0, 0, 0, 0)
        """Set up the backlash RadioButton"""
        self.backlash_radiobutton = QtWidgets.QRadioButton("BACKLASH", self.layoutWidget)
        self.StyleSheetOn = "QRadioButton::indicator {width: 15px; height: 15px; border-radius: 7px;} " \
                            "QRadioButton::indicator:checked { background-color: lime; border: 2px solid gray;} " \
                            "QRadioButton::indicator:unchecked { background-color: black; border: 2px solid gray;}"

        self.backlash_radiobutton.setStyleSheet(self.StyleSheetOn)
        self.backlash_radiobutton.toggle()
        self.HorizontalLayoutPath.addWidget(self.backlash_radiobutton)

        """Path buttons horizontal layout"""
        self.path_buttons_names_tuple = (" Add PATH ", " Edit PATH ", " Clear PATH ", " Generate PATH ")
        self.path_buttons_objects_dict = {}
        for i in range(len(self.path_buttons_names_tuple)):
            self.path_buttons_objects_dict[self.path_buttons_names_tuple[i]]=self.SetPathButtons()
            self.path_buttons_objects_dict[self.path_buttons_names_tuple[i]].setText(self.path_buttons_names_tuple[i])

        "Add label to show image from camera on it"
        self.camera_image_label = QtWidgets.QLabel(self.layoutWidget)
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        # sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        # self.camera_image.setSizePolicy(sizePolicy)
        self.camera_image_label.setGeometry(QtCore.QRect(0, 0, self.w, 200))
        self.camera_image_label.setText("HERE WILL BE IMAGE FROM CAMERA")

        """Combine all layouts"""
        self.MainHorizontalLayout.addLayout(self.VerticalLayoutXYZ)
        self.MainHorizontalLayout.addLayout(self.VerticalLayoutPredefined)
        self.MainVerticalLayout.addLayout(self.MainHorizontalLayout)
        self.MainVerticalLayout.addLayout(self.HorizontalLayoutPath)
        self.MainVerticalLayout.addWidget(self.camera_image_label)


    def SetPathButtons(self):
        "PushButton to work with path positions and generate path"
        self.pushButton = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(False)
        font.setKerning(True)
        self.pushButton.setFont(font)
        self.pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.pushButton.setCheckable(False)
        self.HorizontalLayoutPath.addWidget(self.pushButton)
        return self.pushButton

    def SetPredefinedButtons(self):
        "PushButton to move the axis to a predefined position"
        self.pushButton = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setFixedHeight(50)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.pushButton.setFont(font)
        self.pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.pushButton.setCheckable(False)
        self.VerticalLayoutPredefined.addWidget(self.pushButton)
        return self.pushButton

    def SetAxisHorizontalLayout(self):
        self.SingleAxisControlDict = {}
        self.HorizontalLayout = QtWidgets.QHBoxLayout()

        "Label showing name of the axis"
        self.Label = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.Label.sizePolicy().hasHeightForWidth())
        self.Label.setFixedWidth(30)
        self.Label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.Label.setFont(font)
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.HorizontalLayout.addWidget(self.Label)
        self.SingleAxisControlDict[0] = self.Label
        self.HorizontalLayout.addStretch()

        "Label showing current position of the axis"
        self.Label = QtWidgets.QLabel(self.layoutWidget)
        # sizePolicy.setHeightForWidth(self.Label.sizePolicy().hasHeightForWidth())
        self.Label.setFixedWidth(90)
        self.Label.setSizePolicy(sizePolicy)
        self.Label.setFont(font)
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Label.setStyleSheet("color: rgb(52,181,52); background: rgb(0,0,0);")
        self.Label.setText(" 0.00 ")
        self.HorizontalLayout.addWidget(self.Label)
        self.SingleAxisControlDict[1]=self.Label

        "LineEdit to enter the required position of the axis"
        self.LineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(self.LineEdit.sizePolicy().hasHeightForWidth())
        self.LineEdit.setSizePolicy(sizePolicy)
        self.LineEdit.setFont(font)
        self.LineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.HorizontalLayout.addWidget(self.LineEdit)
        self.SingleAxisControlDict[2]=self.LineEdit
        self.HorizontalLayout.addStretch()

        # self.spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        # self.HorizontalLayout.addItem(self.spacerItem)

        "PushButton to move the axis by delta to the lower values"
        self.pushButton = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.pushButton.setFont(font)
        self.pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.pushButton.setCheckable(False)
        self.pushButton.setText("<<")
        self.HorizontalLayout.addWidget(self.pushButton)
        self.SingleAxisControlDict[3] = self.pushButton
        self.HorizontalLayout.addStretch()

        "LineEdit to enter the required position of delta to move the axis"
        self.LineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LineEdit.sizePolicy().hasHeightForWidth())
        self.LineEdit.setSizePolicy(sizePolicy)
        font.setPointSize(16)
        self.LineEdit.setFont(font)
        self.LineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.LineEdit.setText("0.10")
        self.HorizontalLayout.addWidget(self.LineEdit)
        self.SingleAxisControlDict[4]=self.LineEdit
        self.HorizontalLayout.addStretch()

        "PushButton to move the axis by delta to the lower values"
        self.pushButton = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.pushButton.setFont(font)
        self.pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.pushButton.setCheckable(False)
        self.pushButton.setText(">>")
        self.HorizontalLayout.addWidget(self.pushButton)
        self.SingleAxisControlDict[5] = self.pushButton
        self.HorizontalLayout.addStretch()

        self.VerticalLayoutXYZ.addLayout(self.HorizontalLayout)