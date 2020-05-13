import maya.cmds as cmds
import maya.mel as mel

"""
Using: Maya API 1.0, Python 2.7
Author: Timothy Stoltzner Rasmussen
Requirements: A simple animation in maya, to showcase timeline editing. 
"""


class ReTimerHelperMethods(object):

    # Method Types Python
    # https://levelup.gitconnected.com/method-types-in-python-2c95d46281cd
    # What is @classmethod
    # https://www.programiz.com/python-programming/methods/built-in/classmethod

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