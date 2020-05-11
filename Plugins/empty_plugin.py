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

if __name__ == "__main__":
    plugin_name = "empty_plugin.py"
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadsPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadsPlugin("{0}")'.format(plugin_name))