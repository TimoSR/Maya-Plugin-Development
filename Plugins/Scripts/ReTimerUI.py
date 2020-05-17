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
        pass

    def create_layouts(self):
        pass

    def create_connection(self):
        pass


if __name__ == "__main__":

    re_timing_ui = ReTimerUI()

    try:
        re_timing_ui.close()
        re_timing_ui.deleteLater()

    except:
        pass

    re_timing_ui.show()
