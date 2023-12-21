import pya
import math
from   enum import IntEnum, Enum
class Keys(IntEnum):
    shift      =  1
    ctrl       =  2
    alt        =  4
    
    back_space = 16777219
    delete     = 16777223
    
    left       =  8
    middle     = 16
    right      = 32
    
    dot        = 46
    num_1      = 49
    num_2      = 50
    num_3      = 51
    num_4      = 52
    num_5      = 53
    num_6      = 54
    num_7      = 55
    num_8      = 56
    num_9      = 57
    num_0      = 48
    
    def number():
        return [46, 49, 59, 50, 51, 52, 53, 54, 55, 56, 57, 48]

def isFloat(string : str):
  if string is None:
      return False
  try:
      float(string)
      return True
  except:
      return False
    
def toAngle(arc : float):
    return(arc/(2 * math.pi)*360)
    
def toArc(angle : float):
    return (angle/360) * 2 * math.pi

def viewPortBox(view : pya.LayoutView):
    vp_trans = view.viewport_trans()
    offsetXY = vp_trans.disp          / vp_trans.mag * -1
    offsetW  = view.viewport_width()  / vp_trans.mag
    offsetH  = view.viewport_height() / vp_trans.mag
    return pya.DBox(offsetXY + pya.DPoint(0, 0), offsetXY + pya.DPoint(offsetW, offsetH))
    
def viewPortCenter(view : pya.LayoutView):
    return viewPortBox(view).center()
    
def dPixelLength(view : pya.LayoutView, pixels : float):
    vp_trans = view.viewport_trans()
    dlength  = 1 / vp_trans.mag * pixels
    return dlength
            
def centerDBox(p : pya.DPoint, w : float, h : float):
    dx, dy = w / 2, h / 2
    return pya.DBox( p.x - dx, p.x - dy, p.x + dx, p.x + dy )
    
def centerBox(p : pya.Point, w : int, h : int):
    dx, dy = int(w / 2), int(h / 2)
    return pya.Box( p.x - dx, p.x - dy, p.x + dx, p.x + dy )

def vectorRotate(v : pya.DVector, angle : float):
    rad = angle * 0.0174533 
    return pya.DVector(v.x * math.cos(rad) - v.y * math.sin(rad), v.x * math.sin(rad) + v.y * math.cos(rad))
    
def vectorAngle(v1 : pya.DVector, v2 : pya.DVector):
    vp    = v1.vprod(v2)
    sp    = v1.sprod(v2)
    angle = (math.atan2(vp, sp) * 180.0 / math.pi)
    angle = angle + (360  if angle < 0 else 0)
    return angle

def vertorLengthen(v : pya.DVector, length : float):
    return(v / v.length()) * length

def mirrorPointByEdge(p : pya.DPoint, edge : pya.DEdge):
    vx, vy = (edge.x2 - edge.x1, edge.y2 - edge.y1)
    x,  y  = (edge.x1 - p.x,     edge.y1 -     p.y)
    r      = 0 if 0 in [vx, vy] else (1 / (vx * vx + vy * vy))

    return pya.DPoint(
        p.x + 2 * (x - x * vx * vx * r - y * vx * vy * r), 
        p.y + 2 *( y - y * vy * vy * r - x * vx * vy * r)
    )
