import maya.cmds as cmds
import maya.mel as mel

"""
Using: Maya API 1.0
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


if __name__ == "__main__":
    ReTimer.set_current_time(10)
