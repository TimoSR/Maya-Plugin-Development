import maya.cmds as cmds
import maya.mel as mel

"""
Using: Maya API 1.0, Python 2.7
Author: Timothy Stoltzner Rasmussen
"""


class ReTimer(object):

    # https://www.programiz.com/python-programming/methods/built-in/classmethod

    @classmethod
    def set_current_time(cls, time):
        """
        This method will set
        :param time:
        """
        cmds.currentTime(time)

    @classmethod
    def get_selected_range(cls):
        """
        This method will
        :return: Selected Range
        """
        # Establishing a connection to the playback slider, using a mel command
        playback_slider = mel.eval("$tempVar = $gPlayBackSlider")
        # Range Controller for the playback slider
        selected_range = cmds.timeControl(playback_slider, q=True, rangeArray=True)

        return selected_range

    @classmethod
    def find_keyframe(cls, which, time=None):
        """
        Queries the frame of a keyframe, based on a string value passed in.
        :param which: which keyframe to query (first, last, next or previous).
        :param time: Defaults to None, as it is not required for every which value.
        :return: returns the value of the find key-frame command.
        """
        # Dictionary containing all the command flags, that will be passed into the find key frames command.
        kwargs = {"which": which}
        # Checking if the flag is next or previous.
        if which in ["next", "previous"]:
            # Kwargs allows to pass key-worded variable length of arguments.
            # Passing in start and end frame match contained in a tuple.
            kwargs["time"] = (time, time)
        # Returning the value of the find key-frame command.
        return cmds.findKeyframe(**kwargs)


if __name__ == "__main__":
    ReTimer.set_current_time(10)
