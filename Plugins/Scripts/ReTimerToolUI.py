from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance

import ReTimerHelperMethods
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui


class ReTimerToolUi(QtWidgets.QDialog):
    WINDOW_TITLE = "Re-timer Tool"
    ABSOLUTE_BUTTON_WIDTH = 50
    RELATIVE_BUTTON_WIDTH = 64

    @classmethod
    def maya_main_window(cls):
        """
        :return: The Maya main window widget as a widget as a Python object.
        """
        main_window_ptr = omui.MQtUtil.mainWindow()
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

    def __init__(self):

        super(ReTimerHelperMethods, self).__init__(self.maya_main_window())

        self.setWindowTitle(self.WINDOW_TITLE)

        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        

