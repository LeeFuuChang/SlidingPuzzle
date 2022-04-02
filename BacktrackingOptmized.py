import pygame
pygame.init()



SIZE = 4
SHUFFLESPEED = 0.8
CRACKSPEED = 0.05



import random
from itertools import chain



def ShowState(state):
    for r in state:
        for c in r:
            print(c.n if c else 0, end=" ")
        print()

def KeptRange(x, a, b):
    _a, _b = max(a, b), min(a, b)
    if x > _a:
        return _a
    elif x < _b:
        return _b
    else:
        return x

def dist(x1, y1, x2, y2):
    return round( ( (x2-x1)**2 + (y2-y1)**2 )**(1/2), 3 )



class Cracker():
    def __init__(self, start, size):
        self.reset(start, size)

    def reset(self, start, size):
        self.size = size
        self.start = [ [c.clone() if c else None for c in r] for r in start ]
        self.hash = set([self.Stringnify(self.start)])
        self.table = {self.Stringnify(self.start):[]}
        self.path = [self.findEmpty(self.start)]

    def shortenPath(self, singleCycle, workingPath):
        singleCycleLength = len(singleCycle)
        workingPathLength = len(workingPath)
        closeLoopLength = singleCycleLength*(singleCycleLength-1)
        reversePathLength = closeLoopLength - workingPathLength + 2
        if reversePathLength >= workingPathLength: return False
        print(f"singleCycleLength: {singleCycleLength}")
        print(f"workingPathLength: {workingPathLength}")
        print(f"closeLoopLength: {closeLoopLength}")
        print(f"reversePathLength: {reversePathLength}")
        templateCycle = singleCycle*(singleCycleLength)
        return templateCycle[::-1][workingPathLength-1:workingPathLength+reversePathLength-1]

    def optPath(self, path):
        for singleLoopLength in range(4, self.size*self.size):
            startIdx = 0
            while(startIdx < len(path)-( singleLoopLength*(singleLoopLength-1)//2 ) ):
                singleLoopPath = path[startIdx:startIdx+singleLoopLength]
                bestCaseLooping = singleLoopPath*singleLoopLength
                toBeOptPath = []
                isLoopingPathFlag = True
                for singleLoopCount in range(singleLoopLength-1):
                    for singleLoopElementIdx in range(singleLoopLength):
                        LoopIdx = singleLoopLength*singleLoopCount + singleLoopElementIdx
                        isLoopingPathFlag = path[startIdx+LoopIdx]==bestCaseLooping[LoopIdx]
                        if isLoopingPathFlag:
                            toBeOptPath.append(path[startIdx+LoopIdx])
                        else:
                            break
                    if not isLoopingPathFlag: break
                if len(toBeOptPath) < singleLoopLength: 
                    startIdx += 1
                    continue
                optPath = self.shortenPath(singleLoopPath, toBeOptPath)
                if optPath:
                    print("toBe:", toBeOptPath)
                    print("optmized:", optPath)
                    path = path[:startIdx] + optPath + path[startIdx+LoopIdx:]
                startIdx += 1
        return path

    def saveState(self, state):
        s = self.Stringnify(state)
        if s in self.hash and len(self.table[s]) < len(self.path)+1:
            self.path = self.table[s][:]
        else:
            self.path.insert(0, self.findEmpty(state))
            self.path = self.optPath(self.path)
            self.table[s] = self.path[:]
            self.hash.add(s)
        # print(self.path, end="\n\n")

    def Stringnify(self, state):
        s = ""
        for c in chain.from_iterable(state):
            s += f"{ c.n if c else 0 }|"
        return s[:-1]

    def checkEqual(self, a, b):
        if a and b:
            return a.n == b.n
        else:
            return a == b

    def findEmpty(self, current):
        for i in range(self.size):
            for j in range(self.size):
                if current[i][j] is None: return (i, j)

    def crack(self):
        return self.path



class Disturber():
    def __init__(self, size):
        self.size = size

    def findSurrounding(self, x, y, avoid):
        result = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        return [ c for c in result if 0<=c[0]<self.size and 0<=c[1]<self.size and c!=avoid ]

    def findEmpty(self, current):
        for i in range(self.size):
            for j in range(self.size):
                if current[i][j] is None: return (i, j)

    def disturb(self, current, step):
        start = self.findEmpty(current)
        path = [
            start, 
            random.choice(
                self.findSurrounding(*start, start)
            )
        ]
        for i in range(step-1):
            path.append(
                random.choice(
                    self.findSurrounding(*path[-1], path[-2])
                )
            )
        return path



class Cubie():
    def __init__(self, game, x, y, n):
        self.game = game
        self.size = self.game.cubieSize
        self.x = x
        self.y = y
        self.realX = self.x
        self.realY = self.y
        self.n = n

        self.reset()

    def reset(self):
        self.dragPos = [0, 0]
        self.dragOffset = [0, 0]
        self.direction = (0, 0)

    def draw(self, window, c):
        x, y, _, _ = self.displayInfo()
        pygame.draw.rect(window, c, pygame.Rect(x, y, self.size, self.size))
        cx, cy = x+self.size/2, y+self.size/2
        text_sf, (text_w, text_h) = self.game.font.render(f"{self.n}", True, (0, 0, 0)), self.game.font.size(f"{self.n}")
        window.blit(text_sf, (cx-text_w/2, cy-text_h/2))

    def displayInfo(self):
        return (
            ( self.x*self.size )+( self.game.border*(self.x+1) )+self.dragOffset[0], 
            ( self.y*self.size )+( self.game.border*(self.y+1) )+self.dragOffset[1], 
            self.size, 
            self.size
        )

    def vector(self, x, y):
        cx, cy, _, _ = self.displayInfo()
        return x-cx, y-cy

    def cover(self, x, y):
        cx, cy, _, _ = self.displayInfo()
        return (cx < x < cx+self.size) and (cy < y < cy+self.size)

    def clone(self):
        return Cubie(self.game, self.x, self.y, self.n)



class MAP():
    def __init__(self, game):
        self.game = game
        self.original = [[None]*self.game.gameSize for i in range(self.game.gameSize)]
        self.map = [[None]*self.game.gameSize for i in range(self.game.gameSize)]
        self.blocks = []
        self.empty = [self.game.gameSize-1, self.game.gameSize-1]
        for i in range(self.game.gameSize):
            for j in range(self.game.gameSize):
                n = self.game.gameSize*i + j + 1
                if n == self.game.gameSize*self.game.gameSize: break
                this = Cubie(self.game, j, i, n)
                self.blocks.append(this)
                self.map[i][j] = this
                self.original[i][j] = this
        self.updateEmpty()

    def getEmpty(self):
        for i in range(self.game.gameSize):
            for j in range(self.game.gameSize):
                if not self.map[i][j]:
                    self.empty = (i, j)
                    return self.empty

    def move(self, x, y):
        ex, ey = self.getEmpty()
        moving = self.map[x][y]
        self.map[x][y], self.map[ex][ey] = self.map[ex][ey], self.map[x][y]
        moving.x, moving.y = ey, ex
        self.getEmpty()
        self.updateEmpty()
        self.game.cracker.saveState(self.map)

    def updateEmpty(self):
        for cubie in self.blocks:
            if dist(cubie.y, cubie.x, *self.empty) == 1:
                cubie.direction = (self.empty[1]-cubie.x, self.empty[0]-cubie.y)
            else:
                cubie.direction = (0, 0)


class Game():
    BACKGROUND = (0, 0, 0)
    def __init__(self, Wsize:int, Gsize:int):
        assert Wsize>=480 and Gsize>=2
        self.gameSize = Gsize
        self.border = Wsize//(Gsize*30)
        self.cubieSize = Wsize//Gsize
        self.windowSize = self.cubieSize*Gsize + self.border*(Gsize+1)
        self.window = pygame.display.set_mode((self.windowSize, self.windowSize))

        self.map = MAP(self)

        self.font = pygame.font.SysFont("arial", self.cubieSize//5)
        self.frameWait = pygame.time.Clock().tick

        self.dragging = None
        self.animating = False

        self.disturber = Disturber(self.gameSize)
        self.cracker = Cracker(self.map.map, self.gameSize)


    def animatePath(self, path, speedRate):
        for i in range(len(path)-1):
            (ex, ey), (ax, ay) = path[i:i+2]
            self.animating = self.map.map[ax][ay]
            direction = [ey-ay, ex-ax]
            while(
                (
                    direction[0]>0 and direction[1]==0 and self.animating.x<ey
                ) or (
                    direction[0]<0 and direction[1]==0 and self.animating.x>ey
                ) or (
                    direction[1]>0 and direction[0]==0 and self.animating.y<ex
                ) or (
                    direction[1]<0 and direction[0]==0 and self.animating.y>ex
                )
            ):
                self.window.fill(self.BACKGROUND)
                if self.handleQuit():
                    quit()

                self.drawCubies()

                self.animating.x += direction[0]*speedRate
                self.animating.y += direction[1]*speedRate

                self.frameWait(60)
                pygame.display.update()

            self.map.move(ax, ay)
            self.animating = None


    def handleQuit(self):
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                return True
        return False


    def handleDrag(self):
        if self.animating: return
        mouse_state = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        if mouse_state[0] and self.dragging is None:
            for cubie in self.map.blocks:
                if cubie.cover(*mouse_pos):
                    self.dragging = cubie
                    self.dragging.dragPos = self.dragging.vector(*mouse_pos)

        elif mouse_state[0] and self.dragging is not None:
            self.dragging.dragOffset = [0, 0]
            for i in range(2):
                if self.dragging.direction[i]:
                    self.dragging.dragOffset[i] = KeptRange(
                        mouse_pos[i]-self.dragging.displayInfo()[:2][i]-abs(self.dragging.dragPos[i]*self.dragging.direction[i]), 
                        0, 
                        self.dragging.size*self.dragging.direction[i]
                    )

        elif not mouse_state[0] and self.dragging is not None:
            for i in range(2):
                if self.dragging.direction[i]:
                    if abs( (self.dragging.size*self.dragging.direction[i])/2 ) < abs(self.dragging.dragOffset[i]):
                        self.map.move(self.dragging.y, self.dragging.x)
                        # x1, y1, x2, y2 = self.dragging.x, self.dragging.y, self.map.empty[0], self.map.empty[1]
                        # #swapping
                        # self.map.map[y1][x1], self.map.map[y2][x2] = self.map.map[y2][x2], self.map.map[y1][x1]
                        # self.dragging.x, self.dragging.y, self.map.empty[0], self.map.empty[1] = x2, y2, x1, y1
                    break
            self.dragging.reset()
            self.map.updateEmpty()
            self.dragging = None

        else:
            self.dragging = None


    def drawCubies(self, avoid=()):
        for cubie in self.map.blocks:
            if cubie in avoid: continue
            cubie.draw(self.window, (255, 255, 255))


    def mainloop(self):
        while(True):
            if self.handleQuit():
                quit()

            self.window.fill(self.BACKGROUND)

            self.drawCubies((self.dragging, ))
            if self.dragging:
                self.dragging.draw(self.window, (255, 255, 255))

            self.handleDrag()

            if pygame.key.get_pressed()[pygame.K_s]:
                steps = random.randint(20*self.gameSize, 30*self.gameSize)
                path = self.disturber.disturb(self.map.map, steps)
                # print(path, end="\n\n")
                self.animatePath(path, SHUFFLESPEED*self.gameSize)

            if pygame.key.get_pressed()[pygame.K_SPACE]:
                path = self.cracker.crack()
                # print(path, end="\n\n")
                self.animatePath(path, CRACKSPEED)
                self.cracker.reset(self.map.map, self.gameSize)

            self.frameWait(60)
            pygame.display.update()


G = Game(760, SIZE)
G.mainloop()