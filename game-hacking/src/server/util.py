import math

def distance(a, b):
    return math.sqrt((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2)

def lerp(a, b, t):
    return a + (b - a) * t
