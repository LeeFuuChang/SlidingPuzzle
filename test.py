p = [
    (2, 2), (2, 1), (2, 0), (1, 0), (0, 0), (0, 1), (0, 2), (1, 2), 
    (2, 2), (2, 1), (2, 0), (1, 0), (0, 0), (0, 1), (0, 2), (1, 2)
]
p = [
    (2, 1), (2, 0), (1, 0), (0, 0), (0, 1), (0, 2), (1, 2), (2, 2),
    (2, 1), (2, 0), (1, 0), (0, 0), (0, 1), (0, 2), (1, 2), (2, 2),
    (2, 1), (2, 0), (1, 0), (0, 0), (0, 1), (0, 2), (1, 2), (2, 2),
    (2, 1), (2, 0), (1, 0), (0, 0), (0, 1), (0, 2), (1, 2), (2, 2),
    (2, 1), (2, 0), (1, 0), (0, 0), (0, 1), (0, 2), (1, 2), (2, 2),
]



workingPath = [(1, 0), (0, 0), (0, 1), (1, 1), (1, 0), (0, 0), (0, 1), (1, 1), (1, 0), (0, 0), (0, 1), (1, 1), (2, 1), (2, 2)]

def shortenPath(singleCycle, workingPath):
    singleCycleLength = len(singleCycle)
    workingPathLength = len(workingPath)
    closeLoopLength = singleCycleLength*(singleCycleLength-1)
    reversePathLength = closeLoopLength - workingPathLength
    if reversePathLength >= workingPathLength: return False
    print(f"singleCycleLength: {singleCycleLength}")
    print(f"workingPathLength: {workingPathLength}")
    print(f"closeLoopLength: {closeLoopLength}")
    print(f"reversePathLength: {reversePathLength}")
    templateCycle = singleCycle*(singleCycleLength)
    return templateCycle[::-1][workingPathLength-1:workingPathLength+reversePathLength+1]

def optPath(path):
    for singleLoopLength in range(4, 17):
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
            optPath = shortenPath(singleLoopPath, toBeOptPath)
            if optPath:
                print("toBe:", toBeOptPath)
                print("optmized:", optPath)
                path = path[:startIdx] + optPath + path[startIdx+LoopIdx+1:]
    return path

print(optPath(workingPath))