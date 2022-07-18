def StripToTriangle(triangleStripList, faceDir=[]):
    faces = []
    cte = 0
    if 0 in faceDir:
        faceWinding = True
    else:
        faceWinding = False
    
    for i in range(2, len(triangleStripList)):
        if triangleStripList[i] == 0xFFFF or triangleStripList[i - 1] == 0xFFFF or triangleStripList[i - 2] == 0xFFFF:
            if i % 2 == 0:
                cte = -1
            else:
                cte = 0
            if triangleStripList[i] in faceDir or triangleStripList[i - 1] in faceDir or triangleStripList[i - 2] in faceDir:
                faceWinding = True
            else:
                faceWinding = False
        else:
            if (i + cte) % 2 == 0:
                a = triangleStripList[i - 2]
                b = triangleStripList[i - 1]
                c = triangleStripList[i]
            else:
                a = triangleStripList[i - 1]
                b = triangleStripList[i - 2]
                c = triangleStripList[i]

            if a != b and b != c and c != a:
                if faceWinding == False:
                    faces.append([a, b, c])
                elif faceWinding == True:
                    faces.append([c, b, a])
    return faces