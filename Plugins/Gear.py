import maya.cmds as cmds


class Gear(object):

    def __init__(self, standard_teeth=10, standard_length=0.3):
        """
        To use the gear class you need to assign the teeth amount and the length.
        It will otherwise use the standard defined values.

        :param standard_teeth: Amount of gear teeth
        :param standard_length: The length of the teeth
        """
        self.standard_teeth = standard_teeth
        self.standard_length = standard_length
        self.spans = standard_length * 2
        self.shape = None
        self.transform = None
        self.constructor = None
        self.extrude = None

    def create(self):
        pass

    def create_pipe(self):
        # Setting the shape and transform to the class variables
        self.transform, self.shape = cmds.polyPipe(subdivisionsAxis=self.spans)

        for node in cmds.listConnections("%s.inMesh" % self.transform):
            if cmds.objectType(node) == "polyPipe":
                self.constructor = node
                break

    def make_teeth(self):
        # Clearing the selection to ensure, selection is clean.
        cmds.select(clear=True)

        faces = self.get_teeth_faces()

    def change_length(self):
        cmds.polyExtrudeFacet(self.extrude, edit=True, ltz=self.standard_length)

    def get_teeth_faces(self):
        # Creating a list to select all the faces that will become the teeth.
        # This will return a list of numbers in the range spans * 2 to spans * 3, with steps of 2.
        side_faces = range(self.spans * 2, self.spans * 3, 2)

        # The list for collecting the faces
        faces = []

        # Concatenation %d for numbers %s strings
        for face in side_faces:
            faces.append("f[%d]" % face)

        return faces


    def modify_extrude(self):
        faces = self.get_teeth_faces()

        # The extrude node has an attribute called inputComponents
        # To change it I use a simple SetAttr call instead of recreating the extrude which can be expensive
        # Read this as:
        # cmds.setAttr('extrudeNode.inputComponents', 2, 'f[1]', 'f[2]', type='componentList'
        # *args = [] = face1, face2, face3

        cmds.setAttr("%s.inputComponents" % self.extrude, len(faces), *faces, type="componentList")

        self.change_length()
