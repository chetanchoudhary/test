import random


def randomGen(minRange, maxRange, frequency):
    step = (maxRange - minRange)//frequency
    numList = []
    numList.append(minRange)
    numList.append(minRange + step)
    i = 0
    if step == 0:
        step = 1
    while i < (frequency - 2):
        a = numList[len(numList)-1]
        newNum = random.randint(a, a + step)
        numList.append(newNum)
        i = i + 1

    return numList
