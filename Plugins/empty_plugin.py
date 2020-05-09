import maya.api.OpenMaya as om
import maya.cmds as cmds

# This is the base template for a plugin in Maya

def maya_useNewAPI():
    pass

def initializePlugin(plugin):
    vendor = "Timothy Stoltzner Rasmussen"
    version = "1.0.0"

    om.MFnPlugin(plugin, vendor, version)

def uninitializePlugin(plugin):
    pass

