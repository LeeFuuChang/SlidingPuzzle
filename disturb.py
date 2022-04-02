import pygame
pygame.init()



SIZE = 4

import random



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

            if pygame.key.get_pressed()[pygame.K_SPACE]:
                # self.animatePath(Cracker(self.map.map, self.map.original, self.gameSize).crack(), 0.05)
                steps = random.randint(20*self.gameSize, 30*self.gameSize)
                path = self.disturber.disturb(self.map.map, steps)
                print(path)
                self.animatePath(path, 0.08*self.gameSize)

            self.frameWait(60)
            pygame.display.update()


G = Game(760, SIZE)
G.mainloop()