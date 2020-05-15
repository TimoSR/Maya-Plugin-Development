import maya.cmds as cmds

"""
# Using: Maya API 1.0, Python 2.7.11 
# Author: Timothy Stoltzner Rasmussen
"""


class Gear(object):

    standard_length = None
    standard_teeth = None

    """
    TestScript:
    my_gear1 = Gear()
    my_gear1.create()
    my_gear1.change_teeth(30, 1)
    my_gear1.change_length(2)
    """

    def __init__(self, standard_teeth=10, standard_length=0.3):
        """
        To use the gear class you need to assign the teeth amount and the length.
        It will otherwise use the standard defined values.

        :param standard_teeth: Amount of gear teeth
        :param standard_length: The length of the teeth
        """
        self.standard_teeth = standard_teeth
        self.standard_length = standard_length
        self.spans = standard_teeth * 2
        self.shape = None
        self.transform = None
        self.constructor = None
        self.extrude = None

    def create(self):

        self.create_pipe()

        self.make_teeth()

    def create_pipe(self):
        # Setting the shape and transform to the class variables
        self.transform, self.shape = cmds.polyPipe(subdivisionsAxis=self.spans)

        # Finding the polyPipe node and set it equal to the constructor
        for node in cmds.listConnections("{0}.inMesh".format(self.transform)):
            if cmds.objectType(node) == "polyPipe":
                self.constructor = node
                break

    def make_teeth(self):
        # Clearing the selection to ensure, selection is clean.
        cmds.select(clear=True)

        # Creating a list to select all the faces that will become the teeth.
        # This will return a list of numbers in the range spans * 2 to spans * 3, with steps of 2.
        side_faces = self.get_teeth_faces(self.standard_teeth)

        # Looping through the faces in the list of side_faces
        for face in side_faces:
            # The '%s.f[%s]' expands to something like pPipe1.f[20]
            # ADD selecting the wanted faces on the created polygonPipe.
            cmds.select("{0}.{1}".format(self.transform, face), add=True)

        # Instead of returning a value, the extrude note will be stored onto the class
        # as a class variable
        self.extrude = cmds.polyExtrudeFacet(localTranslateZ=self.standard_length)[0]
        cmds.select(clear=True)

    def change_length(self, length=standard_length):
        # Because the extrude node is on the class, I can get it directly
        # By doing it like this, Maya don't need to tell what extrude note to change.
        cmds.polyExtrudeFacet(self.extrude, edit=True, ltz=length)

    def change_teeth(self, teeth=standard_teeth, length=standard_length):
        # By knowing what constructor is used within maya, I refer to it directly
        cmds.polyPipe(self.constructor, edit=True, sa=teeth * 2)
        # Calling modify_extrude directly
        self.modify_extrude(teeth, length)

    def get_teeth_faces(self, teeth=standard_teeth):

        spans = teeth * 2
        # Creating a list to select all the faces that will become the teeth.
        # This will return a list of numbers in the range spans * 2 to spans * 3, with steps of 2.
        side_faces = range(spans * 2, spans * 3, 2)

        # The list for collecting the faces
        faces = []

        for face in side_faces:
            faces.append("f[{0}]".format(face))

        return faces

    def modify_extrude(self, teeth=standard_teeth, length=standard_length):
        faces = self.get_teeth_faces(teeth)

        # The extrude node has an attribute called inputComponents
        # To change it I use a simple SetAttr call instead of recreating the extrude which can be expensive
        # Read this as:
        # cmds.setAttr('extrudeNode.inputComponents', 2, 'f[1]', 'f[2]', type='componentList'
        # *args = [] = face1, face2, face3

        cmds.setAttr("{0}.inputComponents".format(self.extrude), len(faces), *faces, type="componentList")

        self.change_length(length)



