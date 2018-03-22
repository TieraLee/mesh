class Face(object):
    def __init__(self, tri):
        self.triNum = tri
        self.normal = None
        self.vertices = []

    def setNormal(self, normal):
        self.normal = normal

    def appendVertex(self, vertex):
        self.vertices.append(vertex)

    def getNormal(self):
        return self.normal

    def isInFace(self, vertex):
        return vertex in self.vertices
    
    
class Corner(object):
    def __init__(self,index, position):
        self.cornerVertex = index
        self.position = position
        self.triNum = position/3
        self.next = 3 * self.triNum + (position + 1) % 3
        self.prev = 3 * self.triNum + (position + 2) % 3
        self.centroid = None

    def setCentroid(self, centroid):
        self.centroid = centroid

    def rightCorner(self, opposite):
        return opposite[self.next]

class CornerTable(object):
    def __init__(self):
        self.geometryTable = {}
        self.vectorTable = {}
        self.oppositesTable = {}
        self.faces = {}

    def addToVectorTable(self, index1, index2, index3):
        pos = len(self.vectorTable)
        x = Corner(index1, pos)
        y = Corner(index2, pos + 1)
        z = Corner(index3, pos + 2)
        self.vectorTable[pos] = x
        self.vectorTable[pos + 1] = y
        self.vectorTable[pos + 2] = z
    
    def calculateSurfaceNormal(self, v0, v1, v2):
        vec0 = PVector(v0[0],v0[1],v0[2])
        vec1 = PVector(v1[0],v1[1],v1[2])
        vec2 = PVector(v2[0],v2[1],v2[2])
        vec1.sub(vec0)
        vec2.sub(vec0)
        vector = vec2.cross(vec1)
        vector.normalize()
        return (vector.x,  vector.y, vector.z)

    def vertexNormal(self, vertex):
        normalList = []
        for index, face in self.faces.iteritems():
            if face.isInFace(vertex):
                normalList.append(face.getNormal())

        x,y,z = 0.0, 0.0, 0.0
        for normal in normalList:
            x += normal[0]
            y += normal[1]
            z += normal[2]
        listLength = len(normalList)
        if listLength > 0:
            return (x/listLength,  y/listLength, z/listLength)
        return (0.0, 0.0, 0.0)

    def addVertices(self, vertices):
        count = len(self.geometryTable)
        self.geometryTable[count] = vertices


    def setCentroid(self, index, centroid):
        index *= 3
        self.vectorTable[index].setCentroid(centroid)
        self.vectorTable[index + 1].setCentroid(centroid)
        self.vectorTable[index + 2].setCentroid(centroid)

    def getLength(self):
        return len(self.vectorTable)/3
    
    def plotFace(self, index):
        index *= 3
        index1 = self.vectorTable[index].cornerVertex
        index2 = self.vectorTable[index + 1].cornerVertex
        index3 = self.vectorTable[index + 2].cornerVertex
        return self.geometryTable[index1], self.geometryTable[index2], self.geometryTable[index3]

    def calculateOpposites(self):
        for i ,corner1 in self.vectorTable.iteritems():
            for j ,corner2 in self.vectorTable.iteritems():
                if i != j:
                    if (self.vectorTable[corner1.next].cornerVertex == self.vectorTable[corner2.prev].cornerVertex
                        and self.vectorTable[corner1.prev].cornerVertex == self.vectorTable[corner2.next].cornerVertex):
                        self.oppositesTable[corner1.position] = corner2
                        self.oppositesTable[corner2.position] = corner1


    def traceDual(self):
        self.calculateOpposites()
        geoTable2 = {}
        for face in range(self.getLength()):
            vertex1, vertex2, vertex3 = self.plotFace(face)
            x = (vertex1[0] + vertex2[0] + vertex3[0])/3.0
            y = (vertex1[1] + vertex2[1] + vertex3[1])/3.0
            z = (vertex1[2] + vertex2[2] + vertex3[2])/3.0
            geoTable2[face] = (x,y,z)
            self.setCentroid(face, (x,y,z))

        vert2 = {}
        numTriangles = 0
        for index ,vertex in self.geometryTable.iteritems():
            corner = self.findCorner(vertex)
            centroids, nextCenter = self.swing(corner)
            for index in range(len(centroids)):
                geoTablePos = self.vertexIndex(centroids[index] ,geoTable2)
                if index + 1 == len(centroids):
                    next = self.vertexIndex(centroids[0] ,geoTable2)
                else:
                    next = self.vertexIndex(centroids[index + 1] ,geoTable2)
                pos = len(vert2)
                corner1 = Corner(geoTablePos, pos)
                corner2 = Corner(next, pos + 1)
                centroid = Corner(len(geoTable2), pos + 2)
                vert2[len(vert2)] = corner1
                vert2[len(vert2)] = corner2
                vert2[len(vert2)] = centroid

            geoTable2[len(geoTable2)] = nextCenter
            numTriangles += 1

        self.geometryTable.clear()
        self.vectorTable.clear()
        self.oppositesTable.clear()
        self.faces.clear()
        self.geometryTable = geoTable2
        self.vectorTable = vert2
        self.calculateOpposites()
        self.calculateFaces()


    def calculateFaces(self):
        if len(self.faces) != self.getLength():
            self.faces.clear()
            for index in range(self.getLength()):
                index *= 3
                vertex1 = self.geometryTable[self.vectorTable[index].cornerVertex]
                vertex2 = self.geometryTable[self.vectorTable[index + 1].cornerVertex]
                vertex3 = self.geometryTable[self.vectorTable[index + 2].cornerVertex]
                surfaceNormal = self.calculateSurfaceNormal(vertex1, vertex2, vertex3)
                face = Face(index)
                face.setNormal(surfaceNormal)
                face.appendVertex(vertex1)
                face.appendVertex(vertex2)
                face.appendVertex(vertex3)
                self.faces[len(self.faces)] = face

    def findCorner(self, vertex):
        for index, corner in self.vectorTable.iteritems():
            if self.geometryTable[corner.cornerVertex] == vertex:
                return corner

    def vertexIndex(self, vertex, vertices):
        for index, v in vertices.iteritems():
            if v == vertex:
                return index


    def swing(self, startingCorner):
        centroids = [startingCorner.centroid]
        next = startingCorner.rightCorner(self.oppositesTable)
        while True:
            next = self.vectorTable[next.next]
            if (next == startingCorner):
                break

            centroids.append(next.centroid)
            next = next.rightCorner(self.oppositesTable)

        x,y,z = 0.0,0.0,0.0
        for item in centroids:
            x += item[0]
            y += item[1]
            z += item[2]

        centroidLength = len(centroids)
        return centroids , (x/centroidLength, y/centroidLength, z/centroidLength)