import pygame
pygame.init()



SIZE = 3



import random
import shelve, os
from itertools import chain
CrackTable = shelve.open(os.path.join(os.path.dirname(__file__), f"{SIZE}x{SIZE}", f"{SIZE}x{SIZE}"))



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

def Ldist(x1, y1, x2, y2):
    return abs(x1-x2)+abs(y1-y2)

def dist(x1, y1, x2, y2):
    return round( ( (x2-x1)**2 + (y2-y1)**2 )**(1/2), 3 )



class CrackPath():
    def __init__(self, current, size, path):
        self.size = size
        self.current = [ [cubie.clone() if cubie else None for cubie in row] for row in current ]
        self.empty = self.findEmpty()
        self.path = path[:]

    def toString(self):
        result = ""
        for n in chain.from_iterable(self.current):
            if n:
                result += f"{n}|"
            else:
                result += "0|"
        return result[:-1]

    def sumH(self):
        H = 0
        for cubie in chain.from_iterable(self.current):
            if not cubie: continue
            cubie.updateH()
            H += cubie.H
        return H

    def partH(self, sx, sy):
        H = 0
        for cubie in chain.from_iterable(self.current):
            if not cubie: continue
            cubie.updateH()
            if cubie.y == sx or cubie.x == sy:
                H += cubie.H
            else:
                H += self.size+self.size
        return H


    def addPath(self, x1, y1, x2, y2):
        self.path.insert(0, (x1, y1))
        self.current[x2][y2].updatePos(x1, y1)
        self.current[x1][y1], self.current[x2][y2] = self.current[x2][y2], self.current[x1][y1]
        self.empty = (x2, y2)

    def findEmpty(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.current[i][j] is None: return (i, j)

    def clone(self):
        clone = CrackPath(self.current, self.size, self.path)
        return clone


class Cracker():
    def __init__(self, current, target, size):
        self.size = size
        self.original = CrackPath(current, self.size, [])
        self.target = target
        self.shrinkx = self.shrinky = 0
        self.priorityQueue = [[self.original, len(self.original.path), self.original.partH(self.shrinkx, self.shrinky), self.original.empty], ]

    def checkEqual(self, a, b):
        if a and b:
            return a.n == b.n
        else:
            return a == b

    def checkCracked(self, current):
        for i in range(self.size):
            for j in range(self.size):
                a = self.target[i][j]
                b = current[i][j]
                if not self.checkEqual(a, b):
                    return False
        return True

    def checkShrink(self, current):
        if self.shrinkx==self.size-1 or self.shrinky==self.size-1: return False
        nsx, nsy, Flag = self.shrinkx, self.shrinky, False
        for i in range(nsx, self.size-2):
            if not sum(
                [
                    not self.checkEqual(
                        self.target[i][j],
                        current[i][j]
                    ) for j in range(nsy, self.size)
                ]
            ): 
                self.shrinkx += 1
                Flag = True
            else: break
        for i in range(nsy, self.size-2):
            if not sum(
                [
                    not self.checkEqual(
                        self.target[j][i],
                        current[j][i]
                    ) for j in range(nsx, self.size)
                ]
            ): 
                self.shrinky += 1
                Flag = True
            else: break
        return Flag
                

    def findEmpty(self, current):
        for i in range(self.size):
            for j in range(self.size):
                if current[i][j] is None: return (i, j)

    def findSurrounding(self, x, y):
        result = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        return [ c for c in result if self.shrinkx<=c[0]<self.size and self.shrinky<=c[1]<self.size ]

    def crack(self):
        self.shrinkx, self.shrinky = 0, 0
        hash = set()
        while(self.priorityQueue):
            now = self.priorityQueue.pop(0)

            if self.checkCracked(now[0].current): return ([now[0].findEmpty(), ] + now[0].path)[::-1]

            if self.checkShrink(now[0].current):
                self.priorityQueue.clear()
                self.priorityQueue = [now, ]
                hash = set()
                ShowState(now[0].current)
                continue

            print(len(now[0].path)+1)
            flag = False
            for nx, ny in self.findSurrounding(*now[3]):
                new = now[0].clone()
                new.addPath(*now[3], nx, ny)
                mapped = new.toString()
                G, H = len(new.path), new.partH(self.shrinkx, self.shrinky)*7
                if mapped not in hash:
                    self.priorityQueue.append(
                        [new, G, H, new.empty]
                    )
                    hash.add(mapped)
                    flag = True

            if flag: self.priorityQueue.sort(key=lambda p:p[2]+p[1])
        return []



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

        #Crack Stuff
        self.resetCrack()

    def resetCrack(self):
        self.H = 0
        self.F = 0

    def updateH(self):
        self.H = Ldist(self.realX, self.realY, self.x, self.y)

    def updatePos(self, x, y):
        self.x = x
        self.y = y

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
        self.updateH()

    def updateH(self):
        for cubie in self.blocks:
            cubie.updateH()

    def setEmpty(self, x, y):
        self.empty = [x, y]

    def updateEmpty(self):
        for cubie in self.blocks:
            if dist(cubie.x, cubie.y, *self.empty) == 1:
                cubie.direction = (self.empty[0]-cubie.x, self.empty[1]-cubie.y)
            else:
                cubie.direction = (0, 0)

    def toString(self):
        result = ""
        for i in range(self.game.gameSize):
            for j in range(self.game.gameSize):
                result += f"{self.map[i][j].n}|" if self.map[i][j] else "0|"
        return result[:-1]


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
            
            self.animating.x = ey
            self.animating.y = ex
            self.map.map[ax][ay] = None
            self.map.map[ex][ey] = self.animating
            self.map.setEmpty(ay, ax)
            self.map.updateEmpty()

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
                        x1, y1, x2, y2 = self.dragging.x, self.dragging.y, self.map.empty[0], self.map.empty[1]
                        #swapping
                        self.map.map[y1][x1], self.map.map[y2][x2] = self.map.map[y2][x2], self.map.map[y1][x1]
                        self.dragging.x, self.dragging.y, self.map.empty[0], self.map.empty[1] = x2, y2, x1, y1
                    break
            self.dragging.reset()
            self.map.updateEmpty()
            self.map.updateH()
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
                print(path)
                self.animatePath(path, 0.8*self.gameSize)

            if pygame.key.get_pressed()[pygame.K_SPACE]:
                path = Cracker(self.map.map, self.map.original, self.gameSize).crack()
                # path = CrackTable[self.map.toString()]
                print(path, end="\n\n\n")
                self.animatePath(path, 0.05)

            self.frameWait(60)
            pygame.display.update()


G = Game(760, SIZE)
G.mainloop()