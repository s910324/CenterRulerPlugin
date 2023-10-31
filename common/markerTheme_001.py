import pya
import math

import misc_001          as misc
import markerHandler_001 as mkHdl
    
def edgeToArrowPath(edge : pya.DEdge, arrowLength : float, direction : int = 1, supressArrowLen = 2.5):
    arrowWidthHalf  = arrowLength * 0.25882 
    arrowLengthVec  = (edge.p1 - edge.p2) / edge.length() * arrowLength
    arrowWidthVec   = misc.vectorRotate((edge.p1 - edge.p2) / edge.length() * arrowWidthHalf, 90)
    arrowPath       = pya.DPath ([edge.p2, edge.p1], 0)
    supressArrowLen = supressArrowLen if supressArrowLen > 1 else 1
    if arrowLength <= edge.length() / supressArrowLen:
        arrowPath = pya.DPath ([
            edge.p2,
            edge.p2 + arrowLengthVec * direction - arrowWidthVec,
            edge.p2 + arrowLengthVec * direction + arrowWidthVec,
            edge.p2,
            
            edge.p1,
            edge.p1 - arrowLengthVec * direction - arrowWidthVec,
            edge.p1 - arrowLengthVec * direction + arrowWidthVec,
            edge.p1,
            ], 0)
    return arrowPath

def edgeToFowardArrowPath(edge : pya.DEdge, arrowLength : float, direction : int = 1, supressArrowLen = 1.5):
    pts = [p for p in edgeToArrowPath(edge, arrowLength, direction, supressArrowLen).each_point()]
    return pya.DPath(pts[0:5] if len(pts) > 2 else pts, 0)
    
def edgeToBackwardArrowPath(edge : pya.DEdge, arrowLength : float, direction : int = 1, supressArrowLen = 1.5):
    pts = [p for p in edgeToArrowPath(edge, arrowLength, direction, supressArrowLen).each_point()]
    return pya.DPath(pts[3::] if len(pts) > 2 else pts, 0)

def edgeToArrowMark(edge : pya.DEdge, arrowLength : float, direction : int = 1):
    return [
        mkHdl.MarkerTemplate(data = edgeToArrowPath(edge, arrowLength, direction),
        line_width = 1, line_style = 0, vertex_size = 0)
    ]
     
def edgeToFowardArrowMark(edge : pya.DEdge, arrowLength : float, direction : int = 1):
    return [
        mkHdl.MarkerTemplate(data = edgeToFowardArrowPath(edge, arrowLength, direction),
        line_width = 1, line_style = 0, vertex_size = 0)
    ]
    
def edgeToBackwardArrowPath(edge : pya.DEdge, arrowLength : float, direction : int = 1):
    return [
        mkHdl.MarkerTemplate(data = edgeToBackwardArrowPath(edge, arrowLength, direction),
        line_width = 1, line_style = 0, vertex_size = 0)
    ]

def boxMark(p : pya.DPoint, length : float = 1):
    data = None
    if isinstance(p,pya.DPoint):
        vxy  = pya.DVector(length, length)
        data = pya.DBox(p - vxy, p + vxy)
        
    if isinstance(p, pya.DEdge):
        data = pya.DPath([p.p1, p.p2], length * 2) 
        
    if isinstance(p, pya.DPolygon):
        data = p.bbox
        
    if isinstance(p, pya.DBox):
        data = p

    return [
        mkHdl.MarkerTemplate(data = data, line_width = 1, line_style = 0, vertex_size = 0)
    ]
    
def crossMark(p : pya.DPoint, crossLength : float, angle : float):
    vx = misc.vectorRotate(pya.DVector(crossLength, 0), angle)
    vy = misc.vectorRotate(pya.DVector(0, crossLength), angle)
    return [
        mkHdl.MarkerTemplate(data = pya.DEdge(p + vy, p - vy), line_width = 1, line_style = 0, vertex_size = 0),
        mkHdl.MarkerTemplate(data = pya.DEdge(p + vx, p - vx), line_width = 1, line_style = 0, vertex_size = 0),
    ]

def circleMark(p : pya.DPoint, radius : float, points : int = 32):
    poly = pya.DPolygon([p + misc.vectorRotate(pya.DVector(radius, 0), 360/points * i) for i in range(points + 1)])
    return [ mkHdl.MarkerTemplate(data = poly, line_width = 1, line_style = 0, vertex_size = 0),]
    
def cursorMark(p : pya.DPoint, crossLength : float):
    radius = crossLength / 4
    return [   
        circleMark(p, radius, 32), 
        crossMark(p, crossLength, 0)
    ]
    

def detectRangeMark(p : pya.DPoint, detectRange : float):
    return boxMark(p, detectRange)


def centerMark(shape : pya.DPolygon, crossLength : float):
    c  = shape.bbox().center()
    return crossMark(c, crossLength, 0)
    
def edgeArrowMark(edge : pya.DEdge, arrowLength : float, direction : int = 1):
    return edgeToArrowMark(edge, arrowLength, direction)
    
def edgeCenterMark(edge : pya.DEdge, markLength : float):
    lengthVector = misc.vectorRotate((edge.d() / edge.length()) * markLength/2, 45)
    edgeCenter   = edge.p1 + edge.d()/2
    return [ 
        mkHdl.MarkerTemplate(
        data = pya.DEdge(edgeCenter + lengthVector, edgeCenter - lengthVector), 
        line_width = 1, line_style = 1, vertex_size = 0)
    ] 

def vertexMark(p : pya.DPoint, crossLength : float):
    radius2  = crossLength / 4 * 2
    radius1  = crossLength / 4
    
    return [
        circleMark(p, radius1, 32), 
        circleMark(p, radius2, 32), 
        crossMark(p, crossLength, 0)
    ]


def textMark(p : pya.DPoint, text : str, fontSize : float = 0):
    return [
        mkHdl.MarkerTemplate(
        data = pya.DText(text, pya.DTrans(p.x, p.y), fontSize, 0),
        line_width = 0, line_style = 0, vertex_size = 0),
    ]

def areaSelectionMark(areaDbox : pya.DBox):
    return [
        mkHdl.MarkerTemplate(data =areaDbox, line_width = 1, line_style = 1, vertex_size = 0)
    ]
    
def objHoverMark(o : pya.RecursiveShapeIterator):
    unit = o.layout().dbu
    data = None

    if o.shape().is_polygon():
        data = o.shape().polygon
    if o.shape().is_box():
        data = o.shape().box
    if o.shape().is_path():
        data = o.shape().path
    if o.shape().is_text():
        data = o.shape().text
                
    if data:
        return [
            mkHdl.MarkerTemplate(data =data.transformed(o.trans()).to_dtype(unit),
            line_width = 1, line_style = 0, vertex_size = 0)
        ]
    return []
    

def onScreenTextMK(view : pya.LayoutView, text : str):
    viewbox      = misc.viewPortBox(view)
    offset       = misc.dPixelLength(view, 10)
    dtext        = pya.DText(f"\n\n\n\n{text}", viewbox.center().x, viewbox.p2.y + offset)
    dtext.valign = pya.VAlign.VAlignTop
    dtext.halign = pya.HAlign.HAlignCenter
    textMK       = mkHdl.MarkerTemplate(
        data = dtext,
        line_width = 0, line_style = 0, vertex_size = 0
    )
    return [textMK]
    
