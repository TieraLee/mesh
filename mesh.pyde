# Sample code for starting the mesh processing project
#tlee320
from objects import *
rotate_flag = True    # automatic rotation of model?
time = 0   # keep track of passing time, for automatic rotation
isNormal = False
isWhite = False
isRandom = False
colors = []
# initalize stuff
def setup():
    size (600, 600, OPENGL)
    noStroke()
CornerTable = CornerTable()
# draw the current mesh
def draw():
    global time
    global CornerTable
    global isNormal
    global isWhite
    global isRandom
    global colors
    background(0)    # clear screen to black

    perspective (PI*0.333, 1.0, 0.01, 1000.0)
    camera (0, 0, 5, 0, 0, 0, 0, 1, 0)    # place the camera in the scene
    scale (1, -1, 1)    # change to right-handed coordinate system
    
    # create an ambient light source
    ambientLight (102, 102, 102)
  
    # create two directional light sources
    lightSpecular (204, 204, 204)
    directionalLight (102, 102, 102, -0.7, -0.7, -1)
    directionalLight (152, 152, 152, 0, 0, -1)
    
    pushMatrix();

    fill (50, 50, 200)            # set polygon color
    ambient (200, 200, 200)
    specular (0, 0, 0)            # no specular highlights
    shininess (1.0)
  
    rotate (time, 1.0, 0.0, 0.0)

    # THIS IS WHERE YOU SHOULD DRAW THE MESH
    for index in range(CornerTable.getLength()):
        vertex1, vertex2, vertex3 = CornerTable.plotFace(index)
        beginShape()
        
        ## dealing with color
        if isWhite:
            fill(255,255,255)
            
        if isRandom:
            x = int(random(0, 255))
            y = int(random(0, 255))
            z = int(random(0, 255))
            colors.append((x,y,z))
            x, y, z = colors[index]
            fill(x, y, z)
            
            
        if not isNormal:
            normX, normY, normZ = CornerTable.calculateSurfaceNormal(vertex1, vertex2, vertex3)
            normal(normX, normY, normZ)
            vertex(vertex1[0], vertex1[1], vertex1[2])
            vertex(vertex2[0], vertex2[1], vertex2[2])
            vertex(vertex3[0], vertex3[1], vertex3[2])
        else:
            CornerTable.calculateFaces()
            normX, normY, normZ = CornerTable.vertexNormal(vertex1)
            normal(normX, normY, normZ)
            vertex(vertex1[0], vertex1[1], vertex1[2])
            normX, normY, normZ = CornerTable.vertexNormal(vertex2)
            normal(normX, normY, normZ)
            vertex(vertex2[0], vertex2[1], vertex2[2])
            normX, normY, normZ = CornerTable.vertexNormal(vertex3)
            normal(normX, normY, normZ)
            vertex(vertex3[0], vertex3[1], vertex3[2])

        endShape(CLOSE)
    popMatrix()
    
    # maybe step forward in time (for object rotation)
    if rotate_flag:
        time += 0.02

# process key presses
def keyPressed():
    global rotate_flag
    global isNormal
    global isWhite
    global isRandom
    if key == ' ':
        rotate_flag = not rotate_flag
    elif key == '1':
        read_mesh ('tetra.ply')
    elif key == '2':
        read_mesh ('octa.ply')
    elif key == '3':
        read_mesh ('icos.ply')
    elif key == '4':
        read_mesh ('star.ply')
    elif key == '5':
        read_mesh ('torus.ply')
    elif key == 'n':
        isNormal = not isNormal
    elif key == 'r':
        isRandom = not isRandom
        isWhite = False
    elif key == 'w':
        isWhite = not isWhite
        isRandom = False
    elif key == 'd':
        CornerTable.traceDual()

    elif key == 'q':
        exit()

# read in a mesh file (THIS NEEDS TO BE MODIFIED !!!)
def read_mesh(filename):
    global CornerTable
    CornerTable.geometryTable.clear()
    CornerTable.vectorTable.clear()
    CornerTable.oppositesTable.clear()
    CornerTable.faces.clear()
    fname = "data/" + filename
    # read in the lines of a file
    with open(fname) as f:
        lines = f.readlines()
        
    # determine number of vertices (on first line)
    words = lines[0].split()
    num_vertices = int(words[1])
    print "number of vertices =", num_vertices

    # determine number of faces (on first second)
    words = lines[1].split()
    num_faces = int(words[1])
    print "number of faces =", num_faces

    # read in the vertices
    for i in range(num_vertices):
        words = lines[i+2].split()
        x = float(words[0])
        y = float(words[1])
        z = float(words[2])
        CornerTable.addVertices((x,y,z))
    
    # read in the faces
    for i in range(num_faces):
        j = i + num_vertices + 2
        words = lines[j].split()
        nverts = int(words[0])
        if nverts != 3:
            print "error: this face is not a triangle"
            exit()
        
        index1 = int(words[1])
        index2 = int(words[2])
        index3 = int(words[3])
        CornerTable.addToVectorTable(index1, index2, index3)
        