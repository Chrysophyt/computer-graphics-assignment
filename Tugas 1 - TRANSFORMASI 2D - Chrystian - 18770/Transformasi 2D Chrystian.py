import tkinter as tk
import time
import math as mt
from threading import Thread
#Animate bug performance degradasi over time
#selected x&y
selectedX = 0
selectedY = 0

#current x&y
x = 0
y = 0

#untuk keperluan garis 
p1 = [-1, -1]
p2 = [-1, -1]
lineID = [] #untuk menyimpan id_garis untuk dapat dihapus ketika tidak diperlukan
TriangleLineID = []
startHolding = False #untuk inisiasi kapan mouse mulai tahan

#triangle
trianglePoints = [[100, 100], [100, 200], [180, 200]]

#fungsi pemudah buat UI
def addText(win, textString, rowNum, colNum, stickySettings, rowspanNum = 1, columnspanNum = 1): #default size text = 1, stickySettings = {'W', 'E'} West/ East
    setGrid(tk.Label(win, text = textString), rowNum, colNum, stickySettings, rowspanNum, columnspanNum)

def setGrid(tkObject, rowNum, colNum, stickySettings, rowspanNum = 1, columnspanNum = 1): #default objext size = 1
    tkObject.grid(row = rowNum, column = colNum, sticky = stickySettings, rowspan = rowspanNum, columnspan = columnspanNum)

def addTextLabel(win, textString):
    return tk.Label(win, text = textString)
    
#ketika mouse diklik dan tahan
def mouseClickAndHold(event):
    if(str(event.widget)!='.!canvas'): #jika bukan dari canvas("viewport") jangan register
        return
    
    global lineID, startHolding, viewport, p1, p2, point1, point2

    if(startHolding == False): #inisiasi
        if(len(lineID)!=0): #if ada garis yang sudah ada di window sebelumnya akan hapus
            viewport.delete(lineID.pop())

        p1=[event.x, event.y] #titik asal
        changeP1nP2(point1, p1) #update ke UI
        #print(p1) #debug purpose
        lineID.append(viewport.create_line(p1, p1, width = 2)) #buat line dan push ke LineID
        startHolding = True #ubah state ke True
        return

    p2=[event.x, event.y] #ubah p2
    #print(p2) #debug purpose
    changeP1nP2(point2, p2) #update UI

    viewport.delete(lineID.pop()) #garis sebelumnya di 'pop' dan hapus
    lineID.append(viewport.create_line(p1, p2, width = 2)) #garus baru di push

# ketika mouse klik di lepas
def mouseRelease(event):
    global startHolding
    startHolding = False

# ketika mouse hovering
def mouseHover(event):
    if(str(event.widget)!='.!canvas'): 
        return
    global x, y
    x = event.x
    y = event.y
    updateCoordinates(x,y)

# ketika mouse klik
def mouseClick(event):
    if(str(event.widget)!='.!canvas'): #jika bukan dari canvas(viewport) jangan register
        return
    global selectedX, selectedY
    selectedX = event.x
    selectedY = event.y
    selectClickCoordinates(selectedX, selectedY)

def selectClickCoordinates(x, y): #untuk menselect koordinat ketika mouse klik
    global selectLabel
    if(selectLabel==0): #jika UI SelectLabel belum dibuat
        addText(window, "Selected : ", 5, 4, 'W', 1, 5)
        selectLabel = addTextLabel(window, "("+str(x)+", "+str(y)+")")
        setGrid(selectLabel, 5, 8, 'W', 1, 13)
        return
    selectLabel.config(text="("+str(x)+", "+str(y)+")")

#sub program mouseHover untuk mengupdate UI
def updateCoordinates(x, y):
    global currentLabel
    if(currentLabel==0):
        addText(window, "Current : ", 5, 0, 'W', 1, 2)
        currentLabel = addTextLabel(window, "("+str(x)+", "+str(y)+")")
        setGrid(currentLabel, 5, 2, 'W', 1, 2)
        return
    currentLabel.config(text="("+str(x)+", "+str(y)+")")

#untuk ubah nilai garis dan UI P1 dan P2
def updateP1nP2(TextLabel, point, id):
    global p1, p2
    if(id == 1):
        p1 = point
    else:
        p2 = point
    TextLabel.config(text = "("+str(point[0])+","+str(point[1])+")")
    updateLine()


#untuk ubah UI P1 dan P2
def changeP1nP2(TextLabel, point):
    TextLabel.config(text = "("+str(point[0])+","+str(point[1])+")")

#cek updateLine jika terjadi seleksi baru dari p1/ p2
def updateLine():
    global viewport, p1, p2, lineID
    if(p1[0]==-1 or p2[0]==-1):
        return
    if(len(lineID)==0):
        lineID.append(viewport.create_line(p1, p2, width = 2))
        return
    viewport.delete(lineID.pop())
    lineID.append(viewport.create_line(p1, p2, width = 2))

def buttonTranslate(buttonObject):
    buttonObject.config(state='disable')

    rad = 0
    offset = [0, 0]
    if((p2[0]**2+p2[1]**2) < (p1[0]**2+p1[1]**2)):
        offset = [-1*p2[0], -1*p2[1]]
        rad = mt.atan2(p1[1]-p2[1], p1[0]-p2[0])
    else:
        offset = [-1*p1[0], -1*p1[1]]
        rad = mt.atan2(p2[1]-p1[1], p2[0]-p1[0])
    #agar tidak minus

    #translate
    threadTask1 = Thread(target= lambda:transform_translate([p1, p2], offset, lineID))
    threadTask2 = Thread(target= lambda:transform_translate(trianglePoints, offset, TriangleLineID))

    threadTask1.start()
    threadTask2.start()

    while(threadTask1.isAlive()):
        viewport.update()

    #rotate
    threadTask1 = Thread(target= lambda:transform_rotate([p1, p2], rad, True, lineID))
    threadTask2 = Thread(target= lambda:transform_rotate(trianglePoints, rad, True, TriangleLineID))

    threadTask1.start()
    threadTask2.start()

    while(threadTask1.isAlive()):
        viewport.update()
    
    transform_scale(trianglePoints, [1, -1], TriangleLineID)

    #rotate
    threadTask1 = Thread(target= lambda:transform_rotate([p1, p2], rad, False, lineID))
    threadTask2 = Thread(target= lambda:transform_rotate(trianglePoints, rad, False, TriangleLineID))

    threadTask1.start()
    threadTask2.start()

    while(threadTask1.isAlive()):
        viewport.update()

    #translate
    threadTask1 = Thread(target= lambda:transform_translate([p1, p2], [i * -1 for i in offset], lineID))
    threadTask2 = Thread(target= lambda:transform_translate(trianglePoints, [i * -1 for i in offset], TriangleLineID))

    threadTask1.start()
    threadTask2.start()

    while(threadTask1.isAlive()):
        viewport.update()
    
    buttonObject.config(state='normal')

def buttonInstantTranslate():
    global viewport
    rad = 0
    offset = [0, 0]
    if((p2[0]**2+p2[1]**2) < (p1[0]**2+p1[1]**2)):
        offset = [-1*p2[0], -1*p2[1]]
        rad = mt.atan2(p1[1]-p2[1], p1[0]-p2[0])
    else:
        offset = [-1*p1[0], -1*p1[1]]
        rad = mt.atan2(p2[1]-p1[1], p2[0]-p1[0])

    #transform
    for point in trianglePoints:
        point[0]+=offset[0]
        point[1]+=offset[1]

    #rotate
    cos_val = mt.cos(2*mt.pi - rad)
    sin_val = mt.sin(2*mt.pi - rad)
    for point in trianglePoints:
        new_x = point[0] * cos_val - point[1] * sin_val
        new_y = point[0] * sin_val + point[1] * cos_val
        point[0] = new_x
        point[1] = new_y
    
    #scale
    for point in trianglePoints:
        point[1]*=-1

    #rotate back
    cos_val = mt.cos(rad)
    sin_val = mt.sin(rad)
    for point in trianglePoints:
        new_x = point[0] * cos_val - point[1] * sin_val
        new_y = point[0] * sin_val + point[1] * cos_val
        point[0] = new_x
        point[1] = new_y

    #transform back
    for point in trianglePoints:
        point[0]+=-1*offset[0]
        point[1]+=-1*offset[1]
    for IDs in TriangleLineID:
        viewport.delete(IDs)
    TriangleLineID.append(viewport.create_line(trianglePoints[0], trianglePoints[1], trianglePoints[2], trianglePoints[0], width=2))

    

def transform_translate(coordinates, offset, lineID):
    global viewport
    offset_iteration = [0, 0] #data sudah berapakali iterasi
    deltaOffset = [0, 0] #apakah tambah atau kurang

    coordinatesCount = len(coordinates)
    #print(offset) #debug purposes
    if(offset[0]!=0 and offset[1]!=0):
        deltaOffset[0] = offset[0]/abs(offset[0])
        deltaOffset[1] = offset[1]/abs(offset[1]) 


    for i in range(2): # translate x = {0} then y = {1}
        while (offset_iteration[i]< abs(offset[i])):
            for coordinate in coordinates:
                coordinate[i]+=deltaOffset[i]

            for identification in lineID:
                viewport.delete(identification)
            
            if(coordinatesCount==2):
                lineID.append(viewport.create_line(coordinates[0], coordinates[1], width=2))
                global point1, point2
                changeP1nP2(point1, coordinates[0])
                changeP1nP2(point2, coordinates[1])

            else:
                lineID.append(viewport.create_line(coordinates[0], coordinates[1], coordinates[2], coordinates[0], width=2))
            offset_iteration[i]+=1       
            #viewport.update() 
            time.sleep(0.01)

def transform_rotate(coordinates, degrees, clockwise, lineID): #deg in rad & not accurate
    global viewport
    #print (coordinates, rad)
    currentIterationDegree=0
    coordinatesCount = len(coordinates)
    #print(offset) #debug purposes
    iterationDegree = 0
    if(clockwise):
        iterationDegree = 1
    else:
        iterationDegree = -1
    #print("rotating : " + str(round(mt.degrees(degrees)))+"deg")
    degrees = mt.degrees(degrees) + 360
    degrees %= 360

    currentDegree=[]
    r=[]
    for x in range(coordinatesCount):
        r.append(mt.sqrt(coordinates[x][0]**2+coordinates[x][1]**2))
        currentDegree.append(mt.degrees(mt.atan2(coordinates[x][0], coordinates[x][1])))

    for _ in range(round(degrees)):
        #print(currentDegree)
        for x in range(coordinatesCount):
            currentDegree[x] +=iterationDegree

        for x in range(coordinatesCount):
            #print(r[x], coordinates[x][0], currentDegree[x])
            coordinates[x][0] = round( r[x] * mt.sin(mt.radians(currentDegree[x])))
            coordinates[x][1] = round( r[x] * mt.cos(mt.radians(currentDegree[x])))


        for identification in lineID:
            viewport.delete(identification)
        
        if(coordinatesCount==2):
            lineID.append(viewport.create_line(coordinates[0], coordinates[1], width=2))
            global point1, point2
            changeP1nP2(point1, coordinates[0])
            changeP1nP2(point2, coordinates[1])
        else:
            lineID.append(viewport.create_line(coordinates[0], coordinates[1], coordinates[2], coordinates[0], width=2))
        currentIterationDegree += abs(iterationDegree)        

def transform_scale(coordinates, k, lineID):
    global viewport
    coordinatesCount = len(coordinates)
    for x in range(coordinatesCount):
        coordinates[x][0] *=k[0]
        coordinates[x][1] *=k[1]

    #delete old
    for identification in lineID:   
        viewport.delete(identification)

    #create new
    if(coordinatesCount==2):
        lineID.append(viewport.create_line(coordinates[0], coordinates[1], width=2))
        global point1, point2
        changeP1nP2(point1, coordinates[0])
        changeP1nP2(point2, coordinates[1])
    else:
        lineID.append(viewport.create_line(coordinates[0], coordinates[1], coordinates[2], coordinates[0], width=2))
    

window = tk.Tk()
window.title("Transformasi Segitiga")
window.resizable(0,0) #window unresizeable (fixed)      

#Photo                                                        row, col
img = tk.PhotoImage(file='logo.png')
setGrid(tk.Label(window, image = img),                          0, 0, 'W', 3, 1)

#Label
addText(window, "Grafika Komputer [MII-2207]",                  0, 1, 'W', 1, 10)
addText(window, "Tugas Transformasi 2D",                        1, 1, 'W', 1, 10)
addText(window, " Chrystian - 18/430257/PA/18770 ",             2, 1, 'W', 1, 10)

#Text entry
addText(window, "Point 1: ",                                    3, 3, 'W')
point1 = addTextLabel(window, "")
setGrid(point1,                                                 3, 4, 'W')

addText(window, "Point 2: ",                                    4, 3, 'W')
point2 = addTextLabel(window, "")
setGrid(point2,                                                 4, 4, 'W')

#Button for text
num = [0]
setGrid(tk.Button(window, text="Set P1", width=9, 
command=lambda: updateP1nP2(point1, [selectedX, selectedY], 1)),  3, 0,'N', 1, 2)
setGrid(tk.Button(window, text="Set P2", width=9, 
command=lambda: updateP1nP2(point2, [selectedX, selectedY], 2)),  4, 0,'N', 1, 2)

#for initialization nanti akan dipakai
selectLabel = 0
currentLabel = 0

buttonTransformObject = tk.Button(window, text="Animate", width=10)
buttonTransformObject.config(command=lambda: buttonTranslate(buttonTransformObject))
setGrid(buttonTransformObject, 6, 0,'W', 1, 2)

buttonInstantTransformObject = tk.Button(window, text="Transform", width=12)
buttonInstantTransformObject.config(command=lambda: buttonInstantTranslate())
setGrid(buttonInstantTransformObject, 6, 4,'W', 1, 6)

#Canvas
viewport = tk.Canvas(window, bg='#dedede', height=500, width=500)
setGrid(viewport, 7, 0, 'W', 1, 100)

TriangleLineID.append(viewport.create_line(trianglePoints[0], trianglePoints[1], trianglePoints[2], trianglePoints[0], width=2))


window.bind("<Button 1>", mouseClick)
window.bind("<Motion>", mouseHover)
window.bind('<B1-Motion>', mouseClickAndHold)
window.bind('<ButtonRelease-1>', mouseRelease)



window.mainloop()
