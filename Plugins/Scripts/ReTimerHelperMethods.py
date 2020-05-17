import maya.cmds as cmds
import maya.mel as mel
from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui

"""
Using: Maya API 1.0, Python 2.7.11
Author: Timothy Stoltzner Rasmussen
Requirements: A simple animation in maya, to showcase timeline editing. 
"""


class ReTimerHelperMethods(object):

    # Method Types Python
    # https://levelup.gitconnected.com/method-types-in-python-2c95d46281cd
    # Using cls, as this won't be initialized with parameters.
    # What is @classmethod
    # https://www.programiz.com/python-programming/methods/built-in/classmethod

    @classmethod
    def re_time_keys(cls, re_time_value, incremental, move_to_next):
        """
        Re-time the selected keys (range).
        :param re_time_value: Is the number of frames, how it is interpreted depends on incremental.
        :param incremental: If False, then the re_time_value will be the exact number of frames, that should be between
        keyframes. This will be the top row buttons in the UI. When True the re_time value will be how many frames
        should be inserted between the keyframes in the selected range.
        :param move_to_next:
        :return:
        """

        # Using the defined helper methods, I query Maya for time values.

        # The user selected range in the playback slider.
        range_start_time, range_end_time = cls.get_selected_range()

        # The keyframe of the start of the selected range.
        start_keyframe_time = cls.get_start_keyframe_time(range_start_time)

        # The very last keyframe for any of the selected objects.
        last_keyframe_time = cls.get_last_keyframe_time()

        # The start keyframe time, if we have a range, the current_time will always be the start of that range.
        current_time = start_keyframe_time

        # A list to store all of the soon to be calculated new keyframe times. start_keyframe_time is the anchor,
        # while its time will not change, nor will any of the frame to the left of it. It will be required to calculate
        # the new key frame times.
        new_keyframe_times = [start_keyframe_time]

        # A list to store current keyframe time
        current_keyframe_values = [start_keyframe_time]

        # This while loop is used to iterate over each of the key frames, starting at the start keyframe time,
        # which the time is initially set to, and the loop end at the current time is equal to the last keyframe time.
        while current_time != last_keyframe_time:
            # Getting the next keyframe time. This will be used in the end of the loop to set the current_time to the
            # next keyframes time until the loop reaches the last_keyframes_time.
            next_keyframe_time = cls.find_keyframe("next", current_time)
            # If incremental is True.
            if incremental:
                # Find the time difference between the current keyframe time and the next.
                time_diff = next_keyframe_time - current_time
                # If current time is less than the end time of the range.
                if current_time < range_end_time:
                    # Increment the time difference with the re_time_value.
                    time_diff += re_time_value

                    # One important thing, is that I need to handle one specific case, where too many frames is
                    # being removed. There must always be 1 frame between keyframes, and keyframes cannot jump over
                    # one another.

                    # Therefore I check if time_diff is less than one, if so, I force it to be one.
                    if time_diff < 1:
                        time_diff = 1

            # Calculation of new keyframe times, when the re-time value is absolute.
            else:
                # Because the re-time value is the exact number of frames, that should separate keyframes.
                # The time difference for any keyframes in the selected range will be set to this value.

                # Keyframes within the selected range
                if current_time < range_end_time:
                    time_diff = re_time_value
                # Keyframes outside the selected range.
                else:
                    # Will keep the same number of frames between  the next keyframe, and will only be moved in
                    # relation to the previous keyframe.
                    time_diff = next_keyframe_time - current_time

            # Calculating the final re-timed value for this keyframe, and add it to the new_keyframes_times list.
            # To calculate the final value. I add the last keyframes new time and the time difference.
            new_keyframe_times.append(new_keyframe_times[-1] + time_diff)
            current_time = new_keyframe_times

            # Storing the new current time.
            current_keyframe_values.append(current_time)

        # Printing the contents of each list
        print("Current: {0}".format(current_keyframe_values))
        print("Re-timed: {0}".format(new_keyframe_times))

        # Checking the length of the new keyframe times list is bigger then one.
        if len(new_keyframe_times) > 1:
            # If there more then one value, begin the recursive re-timer.
            cls.re_time_keys_recursive(start_keyframe_time, 0, new_keyframe_times)

        # Storing the first keyframe time.
        first_keyframe_time = cls.find_keyframe("first")

        # The implementation of the move_to_next functionality, set in the parameters.
        if move_to_next and range_start_time >= first_keyframe_time:
            # When move_to_next is True and the range start time is after the very first keyframe, the current time
            # will be set to the next keyframe, after the start keyframe time.
            next_keyframe_time = cls.find_keyframe("next", start_keyframe_time)
            cls.set_current_time(next_keyframe_time)
        elif range_end_time > first_keyframe_time:
            # When move_to_next is False and range end time is before the first keyframe, after re-timing the current
            # time, will be set to the start keyframe time (This is the first keyframe of the range).
            cls.set_current_time(start_keyframe_time)
        else:
            # If neither of the two above conditions is met, set the current time to the ranges start time.
            cls.set_current_time(range_start_time)

    @classmethod
    def re_time_keys_recursive(cls, current_time, index, new_keyframe_times):
        """
        A recursive method to re-time keyframe times.
        Starting with the first keyframe, verifying it can be moved, otherwise wait to the next frame has been
        moved, then move it.
        :param current_time: The chosen start keyframes time.  
        :param index: The start index.
        :param new_keyframe_times: List holding the keyframe times.
        :return:
        """

        # Exit when index is larger or equal to length of new key frame times list.
        if index >= len(new_keyframe_times):
            return

        # Storing the updated key frame time.
        updated_keyframe_time = new_keyframe_times[index]

        # Getting the next keyframe.
        next_keyframe_time = cls.find_keyframe("next", current_time)

        # If the keyframe can be moved.
        if updated_keyframe_time < next_keyframe_time:
            # Change the time immediately to the updated time.
            cls.change_time_of_keyframe(current_time, updated_keyframe_time)
            # Move the next keyframe
            cls.re_time_keys_recursive(next_keyframe_time, index + 1, new_keyframe_times)
        # If not
        else:
            # Move the next keyframe
            cls.re_time_keys_recursive(next_keyframe_time, index + 1, new_keyframe_times)
            # When the next keyframe is moved, it is safe to change the time of the current keyframe.
            cls.change_time_of_keyframe(current_time, updated_keyframe_time)

    @classmethod
    def set_current_time(cls, time):
        """
        Set the current time.
        :param time:
        """
        cmds.currentTime(time)

    @classmethod
    def get_selected_range(cls):
        """
        Get the selected range.
        :return: Selected Range
        """
        # Passing the mel command to connect to the playback slider.
        playback_slider = mel.eval("$tempVar = $gPlayBackSlider")
        # Passing the selected range of the playback slider.
        selected_range = cmds.timeControl(playback_slider, q=True, rangeArray=True)

        return selected_range

    @classmethod
    def find_keyframe(cls, which, time=None):
        """
        Queries the frame of a keyframe, based on a string value passed in.
        :param which: which keyframe to query (first, last, next or previous).
        :param time: Defaults to None, as it is not required for every which value.
        :return: returns the value of the find key_frame command.
        """
        # Dictionary containing all the command flags, that will be passed into the find key frames command.
        kwargs = {"which": which}
        # Checking if the flag is next or previous.
        if which in ["next", "previous"]:
            # Kwargs allows to pass key-worded variable length of arguments.
            # Adding the time flag to dictionary, passing in the time of the start and end frame.
            kwargs["time"] = (time, time)
        # Returning the value of the find key_frame command.
        # Can also be written as cmds.findKeyframe(which=which, time=time) but time is not guaranteed to be used.
        return cmds.findKeyframe(**kwargs)

    @classmethod
    def change_time_of_keyframe(cls, current_time, new_time):
        """
        Changes the time a keyframe is on.
        Can't move keys past other keys on the timeline.
        :param current_time:
        :param new_time:
        :return:
        """
        # Maya keyframe command.
        # Time is the same time because its targeting the same frame.
        # TimeChange is the time we want to change to.
        cmds.keyframe(edit=True, time=(current_time, current_time), timeChange=new_time)

    @classmethod
    def get_start_keyframe_time(cls, range_start_time):
        """
        Get the start keyframe time or the previous.
        :param range_start_time:
        :return: The current chosen or previous keyframe if no keyframe exist.
        """
        # Maya keyframe command.
        start_times = cmds.keyframe(query=True, time=(range_start_time, range_start_time))
        # If there is a list returned with any values.
        if start_times:
            # I return the keyframe.
            return start_times[0]
        # If no keyframes exists I return the previous keyframe.
        # Using the find_keyframe method.
        start_time = cls.find_keyframe("previous", range_start_time)
        return start_time

    @classmethod
    def get_last_keyframe_time(cls):
        """
        :return: The last Keyframe time.
        """
        return cls.find_keyframe("last")

# Extends QDialog class
class RetimingUi(QtWidgets.QDialog):

    # Constants
    WINDOW_TITLE = "Retiming Tool"
    ABSOLUTE_BUTTON_WIDTH = 50
    RELATIVE_BUTTON_WIDTH = 64
    RETIMING_PROPERTY_NAME = "retiming_data"

    dlg_instance = None

    @classmethod
    def display(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = RetimingUi()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    @classmethod
    def maya_main_window(cls):
        """
        Used to parent this dialog to Mayas main window.
        Return the Maya main window widget as a Python object
        """
        main_window_ptr = omui.MQtUtil.mainWindow()
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

    def __init__(self):
        super(RetimingUi, self).__init__(self.maya_main_window())

        # Setting the window title of the main window.
        self.setWindowTitle(self.WINDOW_TITLE)

        # Setting the window title of the main window.
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
        self.create_connections()

    def create_widgets(self):
        self.absolute_buttons = []
        for i in range(1, 7):
            btn = QtWidgets.QPushButton("{0}f".format(i))
            btn.setFixedWidth(self.ABSOLUTE_BUTTON_WIDTH)
            btn.setProperty(self.RETIMING_PROPERTY_NAME, [i, False])
            self.absolute_buttons.append(btn)

        self.relative_buttons = []
        for i in [-2, -1, 1, 2]:
            btn = QtWidgets.QPushButton("{0}f".format(i))
            btn.setFixedWidth(self.RELATIVE_BUTTON_WIDTH)
            btn.setProperty(self.RETIMING_PROPERTY_NAME, [i, True])
            self.relative_buttons.append(btn)

        self.move_to_next_cb = QtWidgets.QCheckBox("Move to Next Frame")

    def create_layouts(self):
        absolute_re_time_layout = QtWidgets.QHBoxLayout()
        absolute_re_time_layout.setSpacing(2)
        for btn in self.absolute_buttons:
            absolute_re_time_layout.addWidget(btn)

        relative_re_time_layout = QtWidgets.QHBoxLayout()
        relative_re_time_layout.setSpacing(2)
        for btn in self.relative_buttons:
            relative_re_time_layout.addWidget(btn)
            if relative_re_time_layout.count() == 2:
                relative_re_time_layout.addStretch()

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        main_layout.addLayout(absolute_re_time_layout)
        main_layout.addLayout(relative_re_time_layout)
        main_layout.addWidget(self.move_to_next_cb)

    def create_connections(self):
        for btn in self.absolute_buttons:
            btn.clicked.connect(self.retime)

        for btn in self.relative_buttons:
            btn.clicked.connect(self.retime)

    def retime(self):
        btn = self.sender()
        if btn:
            retiming_data = btn.property(self.RETIMING_PROPERTY_NAME)
            move_to_next = self.move_to_next_cb.isChecked()

            ReTimerHelperMethods.re_time_keys(retiming_data[0], retiming_data[1], move_to_next)


if __name__ == "__main__":

    try:
        retiming_ui.close()  # pylint: disable=E0601
        retiming_ui.deleteLater()
    except:
        pass

    retiming_ui = RetimingUi()
    retiming_ui.show()
