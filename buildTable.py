from copy import deepcopy
import shelve
import os

SIZE = 3

class Node:
    def __init__(self, state, path):
        self.path = deepcopy(path)
        self.map = deepcopy(state)

    def swap(self, x1, y1, x2, y2):
        self.path.insert(0, (x2, y2))
        self.map[x1][y1], self.map[x2][y2] = self.map[x2][y2], self.map[x1][y1]

    def getEmpty(self):
        for i in range(SIZE):
            for j in range(SIZE):
                if not self.map[i][j]: 
                    return (i, j)

    def getAva(self):
        empty = self.getEmpty()

        directions = [
            [empty[0]+1, empty[1]],
            [empty[0]-1, empty[1]],
            [empty[0], empty[1]+1],
            [empty[0], empty[1]-1]
        ]
        result = [ (nx, ny) for nx, ny in directions if 0<=nx<SIZE and 0<=ny<SIZE ]
        return [empty, result]

    def toString(self):
        result = ""
        for i in range(SIZE):
            for j in range(SIZE):
                result += f"{self.map[i][j]}|"
        return result[:-1]

    def display(self):
        print(len(self.path))
        for row in self.map:
            print(row)

    def clone(self):
        return Node(self.map, self.path)


def main(s):
    global SIZE

    SIZE = int(s)

    Map = []
    for i in range(SIZE):
        Map.append([])
        for j in range(SIZE):
            Map[-1].append(i*SIZE+j+1)
    Map[SIZE-1][SIZE-1] = 0

    hash = set()

    location = os.path.join(os.path.dirname(__file__), f"{s}x{s}")
    if not os.path.exists(location): os.mkdir(location)
    result = shelve.open(os.path.join(location, f"{s}x{s}"))

    queue = [Node(Map, [])]
    while(queue):
        now = queue.pop(0)
        name = now.toString()
        hash.add(name)
        result[name] = [now.getEmpty(), ] + now.path
        empty, directions = now.getAva()
        for direction in directions:
            new = now.clone()
            new.swap(direction[0], direction[1], empty[0], empty[1])
            new_name = new.toString()
            if new_name in hash: continue
            queue.append(new)
            new.display()
            print([new.getEmpty(), ] + new.path)
            print()

    result.close()


import sys
if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])