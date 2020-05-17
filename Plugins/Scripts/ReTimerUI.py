from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance

import ReTimerHelperMethods
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui


# Extends QDialog class
class ReTimerUI(QtWidgets.QDialog):
    # Class constants
    WINDOW_TITLE = "Re-timer Tool"
    ABSOLUTE_BUTTON_WIDTH = 50
    RELATIVE_BUTTON_WIDTH = 64
    RE_TIMING_PROPERTY_NAME = "re_timing_data"

    @classmethod
    def maya_main_window(cls):
        """
        Used to parent this dialog to Mayas main window.
        :return: The Maya main window widget as a widget as a Python object.
        """
        main_window_ptr = omui.MQtUtil.mainWindow()
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

    def __init__(self):
        """
        The Constructor of the class.
        """

        super(ReTimerHelperMethods, self).__init__(self.maya_main_window())

        # Setting the window title of the main window.
        self.setWindowTitle(self.WINDOW_TITLE)

        # Setting different window flags based on the operating system.
        # If windows.
        if cmds.about(ntOS=True):
            # The question mark in the top right of the title bar, is removed from the dialog.
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        # Else if Mac OS
        elif cmds.about(macOS=True):
            # Setting the dialog to be interpreted as a tool, to keep the dialog from falling behind Mayas main window.
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layouts()
        self.create_connection()

    def create_widgets(self):
        self.absolute_buttons = []

        for i in range(1, 7):
            btn = QtWidgets.QPushButton("{0}f".format(i))
            btn.setFixedWidth(self.ABSOLUTE_BUTTON_WIDTH)
            btn.setProperty(self.RE_TIMING_PROPERTY_NAME, [i, False])
            self.absolute_buttons.append(btn)

        self.relative_buttons = []
        for i in [-2, -1, 1, 2]:
            btn = QtWidgets.QPushButton("{0}f".format(i))
            btn.setFixedWidth(self.RELATIVE_BUTTON_WIDTH)
            btn.setProperty(self.RE_TIMING_PROPERTY_NAME, [i, True])
            self.relative_buttons.append(btn)

        self.move_to_next_cb = QtWidgets.QCheckBox("Move to Next Frame")

    def create_layouts(self):
        absolute_re_time_layout = QtWidgets.QHBoxLayout
        absolute_re_time_layout.setSpacing(2)
        for btn in self.absolute_buttons:
            absolute_re_time_layout.addWidget(btn)

        relative_re_time_layout = QtWidgets.QHBoxLayout
        relative_re_time_layout.setSpacing(2)
        for btn in self.relative_buttons:
            absolute_re_time_layout.addWidget(btn)
            if relative_re_time_layout.count() == 2:
                relative_re_time_layout.addStretch()

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        main_layout.addLayout(absolute_re_time_layout)
        main_layout.addLayout(relative_re_time_layout)
        main_layout.addWidget(self.move_to_next_cb)

    def create_connection(self):
        for btn in self.absolute_buttons:
            btn.clicked.connect(self.retime)

        for btn in self.relative_buttons:
            btn.clicked.connect(self.retime)

    def retime(self):
        btn = self.sender()
        if btn:
            re_timing_data = btn.property(self.RE_TIMING_PROPERTY_NAME)
            move_to_next = self.move_to_next_cb.isChecked()

            ReTimerHelperMethod


if __name__ == "__main__":

    re_timing_ui = ReTimerUI()

    try:
        re_timing_ui.close()
        re_timing_ui.deleteLater()

    except:
        pass

    re_timing_ui.show()
