import pya
import math
from   enum import IntEnum
class Keys(IntEnum):
    shift  =  1
    ctrl   =  2
    alt    =  4
    
    left   =  8
    middle = 16
    right  = 32
    
    num_1  = 49
    num_2  = 50
    num_3  = 51
    num_4  = 52
    num_5  = 53
    num_6  = 54
    num_7  = 55
    num_8  = 56
    num_9  = 57
    num_0  = 48

def dPixelLength(view, pixels):
    vp_trans    = view.viewport_trans()
    canvasRes   = max([view.viewport_height(), view.viewport_width()])
    dlength  = 1 / vp_trans.mag * pixels
    return dlength
    
def vectorRotate(v, angle):
    rad = angle * 0.0174533 
    return pya.DVector(v.x * math.cos(rad) - v.y * math.sin(rad), v.x * math.sin(rad) + v.y * math.cos(rad))
    