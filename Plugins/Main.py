import maya.cmds as cmds

# Using the Maya 1.0 API

def gear_creator(standard_teeth=10, standard_length=0.3):
    """
    This function will create a gear with the given parameters
    Args:
        standard_teeth: The number of teeth to create
        standard_length: The length of the teeth
    Returns:
        A tuple of the transform, constructor and extrude node
    """

    # Teeth are every second face, so doubling the number of teeth to get the number of spans required.
    spans = standard_teeth * 2

    # The polyPipe command will create a polygon pipe the subdivisionsAxis will say how many divisions it will have
    # along it's length. It returns a list of [transform, constructor]. Instead of getting a list and then extracting
    # it's members, it is directly expanded it to the variables. The transform is the name of the node created
    # and the constructor is the node that creates the pipe and controls its parameters
    transform, constructor = cmds.polyPipe(subdivisionsAxis=spans)

    # Creating a list to select all the faces that will become the teeth.
    # This will return a list of numbers in the range 40 to 60, with steps of 2.
    side_faces = range(spans * 2, spans * 3, 2)

    print "Selecting the faces %s" % side_faces

    # Clearing the selection, to ensure only faces is added.
    cmds.select(clear=True)

    # Looping through the faces in the list of side_faces
    for face in side_faces:
        # The '%s.f[%s]' expands to something like pPipe1.f[20]
        # ADD selecting the wanted face on the created polygonPipe.
        cmds.select("%s.f[%s]" % (transform, face), add=True)

    # Extruding the selected faces by the given length
    # This gives back the value of the extrude node inside a list
    extrude = cmds.polyExtrudeFacet(localTranslateZ=standard_length)[0]

    print extrude

    # Returning a tuple of (transform, constructor, extrude). A tuple is similar to a list but cannot be modified.
    # The transform is our gear node, the constructor is the node that creates the original pipe and
    # the extrude is the node that extrudes the faces
    return transform, constructor, extrude


