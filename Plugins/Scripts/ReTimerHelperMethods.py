import traceback
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om #Maya API 2.0
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
            current_time = next_keyframe_time

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
    RETIMING_PROPERTY_NAME = "re_timing_data"

    # Storing an instance of this dialog.
    # Storing as class level variable.
    dlg_instance = None

    # Adding a display method to the class, for production release.
    @classmethod
    def display(cls):
        # I check if there isn't an instance created.
        if not cls.dlg_instance:
            # Storing as class level variable.
            cls.dlg_instance = RetimingUi()

        # I check if the instance is hidden.
        if cls.dlg_instance.isHidden():
            # If it is hidden I show it.
            cls.dlg_instance.show()
        else:
            # Otherwise I will raise the window and activate it.
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
        # A list to store the top-row buttons
        self.absolute_buttons = []

        # Creating 6 buttons, moving up to 6 frames as a maximum.
        for i in range(1, 7):
            # The text on the button.
            btn = QtWidgets.QPushButton("{0}f".format(i))
            # Using the constant to set a fixed width
            btn.setFixedWidth(self.ABSOLUTE_BUTTON_WIDTH)
            # Storing the value inside the widget itself, later this will allow the re_time method to pull out how
            # many frames, aswell whether or not it is absolute re-timing or relative re-timing. Passing in a list,
            # with two values, the first is the current value of i, this will be the number of frames, that will be
            # re-timed with, as whether or not it is incremental timing.
            # Because this is absolute buttons, it is not incremental, and i will set the second value to False.
            btn.setProperty(self.RETIMING_PROPERTY_NAME, [i, False])
            # Now I add the new absolute button to the list.
            self.absolute_buttons.append(btn)

        # A list to store the bottom-row buttons.
        self.relative_buttons = []

        # Creating 4 Buttons.
        for i in [-2, -1, 1, 2]:
            # The text on the button.
            btn = QtWidgets.QPushButton("{0}f".format(i))
            # Using the constant to set a fixed width
            btn.setFixedWidth(self.RELATIVE_BUTTON_WIDTH)
            # Storing the value inside the widget itself, later this will allow the re_time method to pull out how
            # many frames, aswell whether or not it is absolute re-timing or relative re-timing. Passing in a list,
            # with two values, the first is the current value of i, this will be the number of frames, that will be
            # re-timed with, as whether or not it is incremental timing.
            # Because this is relative button, it is incremental, so I set the value to True.
            btn.setProperty(self.RETIMING_PROPERTY_NAME, [i, True])
            # Now I add the new relative button to the list.
            self.relative_buttons.append(btn)

        # To enable move to next frame, I set a checkbox to give the option to enable and disable.
        self.move_to_next_cb = QtWidgets.QCheckBox("Move to Next Frame")

    def create_layouts(self):
        # The layout for my top-row buttons. In a horizontal layout.
        absolute_re_time_layout = QtWidgets.QHBoxLayout()
        # The spacing between buttons.
        absolute_re_time_layout.setSpacing(2)
        # Iterating over my list of absolute buttons.
        for btn in self.absolute_buttons:
            absolute_re_time_layout.addWidget(btn)

        # The layout for my bottom-row buttons. In a horizontal layout.
        relative_re_time_layout = QtWidgets.QHBoxLayout()
        # The spacing between buttons.
        relative_re_time_layout.setSpacing(2)
        # Iterating over my list of relative buttons.
        for btn in self.relative_buttons:
            relative_re_time_layout.addWidget(btn)
            # If there is two widgets in this layout.
            if relative_re_time_layout.count() == 2:
                # Add a stretch between the negative and positive numbers.
                relative_re_time_layout.addStretch()

        # Building the UI.
        # Adding my main layout, which is a vertical box layout layout, parented to dialog.
        main_layout = QtWidgets.QVBoxLayout(self)
        # Setting the margins.
        main_layout.setContentsMargins(2, 2, 2, 2)
        # Setting the spacing
        main_layout.setSpacing(2)
        # I now add the two button layouts.
        main_layout.addLayout(absolute_re_time_layout)
        main_layout.addLayout(relative_re_time_layout)
        # Adding the checkbox.
        main_layout.addWidget(self.move_to_next_cb)

    def create_connections(self):
        # Creating the clicked signal connected to the retime slot.
        # For the absolute buttons.
        for btn in self.absolute_buttons:
            btn.clicked.connect(self.retime)
        # For the relative buttons.
        for btn in self.relative_buttons:
            btn.clicked.connect(self.retime)

    def retime(self):
        # Waiting for a signal to be received from a widget(button) click.
        # I query this using the sender method.
        btn = self.sender()
        # If a signal is received and therefore was a sender.
        if btn:
            # I retrieve the data stored as a property. Storing ot in retiming_data, getting the data with the
            # property method passing in the key used to store the data.
            retiming_data = btn.property(self.RETIMING_PROPERTY_NAME)
            # I query if the move_to_next is checked.
            move_to_next = self.move_to_next_cb.isChecked()

            # Using the undo info command, that would group multiple undo operations into a single undo.
            # I create a undo chunk sorrounding the RetimerHelperMethods re-time keys.
            # Open flag.
            cmds.undoInfo(openChunk=True)
            # Hindering not reaching the undoInfo, by handling exceptions.
            try:
                # I now call the RetimeHelperMethods re_time_keys method.
                # I pass in the number of frames and of it is a incremental or absolute change, and if move_to_next is enabled.
                ReTimerHelperMethods.re_time_keys(retiming_data[0], retiming_data[1], move_to_next)
            except:
                # Printing the error to the editor.
                traceback.print_exc()
                # Displaying the error to maya.
                om.MGlobal.displayError("Re-time error occurred. See the script editor for details.")
            # Close fag.
            cmds.undoInfo(closeChunk=True)

if __name__ == "__main__":

    try:
        retiming_ui.close()  # pylint: disable=E0601
        retiming_ui.deleteLater()
    except:
        pass

    retiming_ui = RetimingUi()
    retiming_ui.show()
