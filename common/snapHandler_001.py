import pya
import math
import time
import functools 
from   typing                import Union, Dict, List
from   enum                  import IntEnum

import misc_001              as misc
import markerTheme_001       as mkThm
import markerHandler_001     as mkHdl
import objInRangeHandler_001 as oirHdl

class SnapPolicy(IntEnum):
    showSearchRange = 0b000_000001
    snapCenter      = 0b000_000010
    snapVertex      = 0b000_000100
    snapEdge        = 0b000_001000
    snapEdgeCenter  = 0b000_010000
    snapDefault     = 0b000_001100
    snapAll         = 0b000_011110
    snapOctDir      = 0b111_000000
    snapQuadDir     = 0b011_000000
    
class SnapHandler(mkHdl.MarkerHandler):
    def __init__(self, view : pya.LayoutView, policy : SnapPolicy = SnapPolicy.snapDefault):
        super().__init__(view)
        self.objInRngHdl = oirHdl.ObjInRangeHandler(view)
        self.setPolicy(policy)
        
    def setPolicy(self, policy : SnapPolicy):
        self.policy          =  policy
        policySetter         = lambda p : ((policy & p) == p)
        self.showSearchRange = policySetter(SnapPolicy.showSearchRange)
        self.snapCenter      = policySetter(SnapPolicy.snapCenter)     
        self.snapVertex      = policySetter(SnapPolicy.snapVertex)      
        self.snapEdge        = policySetter(SnapPolicy.snapEdge)        
        self.snapEdgeCenter  = policySetter(SnapPolicy.snapEdgeCenter)  
        self.snapOctDir      = policySetter(SnapPolicy.snapOctDir)
        self.snapQuadDir     = policySetter(SnapPolicy.snapQuadDir)
        
    def addPolicies(self, policies : Union[SnapPolicy, List[SnapPolicy]]):
        p =  functools.reduce(lambda x, y: x | y, policies) if isinstance(policies, list) else policies
        self.setPolicy(self.policy | p)
            
    def removePolicies(self, policies : Union[SnapPolicy, List[SnapPolicy]]):
        p =  functools.reduce(lambda x, y: x | y, policies) if isinstance(policies, list) else policies
        self.setPolicy((self.policy | p) - p)

    def snapPolarTrack(self, startPoint : pya.DPoint, endPoint : pya.DPoint):
        result = endPoint
        if (self.snapOctDir or self.snapQuadDir):
            v1         = pya.DVector(1, 0)
            v2         = endPoint - startPoint
            angle      = misc.vectorAngle(v1, v2)
            pointSlant = (abs(v2.x) + abs(v2.y))/2.0
            snapARange = 22.5 if self.snapOctDir else 45.0

            range0     = abs( angle -   0) <= snapARange
            range90    = abs( angle -  90) <= snapARange
            range180   = abs( angle - 180) <= snapARange
            range270   = abs( angle - 270) <= snapARange
            range360   = abs( angle - 360) <= snapARange

            if  (range90 or range270):
                result = pya.DPoint(startPoint.x, endPoint.y)
                
            elif (range0 or range180 or range360):
                result = pya.DPoint(endPoint.x, startPoint.y)

            else: 
                result = startPoint + pya.DVector(
                    pointSlant * (-1.0 if v2.x < 0 else 1.0),
                    pointSlant * (-1.0 if v2.y < 0 else 1.0)
                )
        return result
        
    def snapPoint(self, *args, **argv):
        paramCount = len(args) + len(argv)
        
        if paramCount == 2:
            return self.snapPointStandard(*args, **argv)
            
        if paramCount == 3:   
            if (self.snapOctDir or self.snapQuadDir):
                return self.snapPointPolarConstrain(*args, **argv)
            else:
                return self.snapPointStandard(*args, **argv)
                
    def snapPointStandard(self, point : pya.DPoint, edge_point : Union[pya.DEdge, pya.DPoint]): 
        if isinstance(edge_point, pya.DEdge):
            edge = edge_point
            dx   = edge.p2.x - edge.p1.x 
            dy   = edge.p2.y - edge.p1.y 
            if dx == 0:
                return pya.DPoint(edge.p1.x, point.y)
            if dy == 0:
                return pya.DPoint(point.x, edge.p1.y)
            else:
                x = sorted([edge.p1.x, edge.p2.x, point.x])[1]
                return pya.DPoint(x,(x - edge.p1.x)/dx * dy + edge.p1.y)
        if isinstance(edge_point, pya.DPoint):
            return edge_point       
        return point
        
    def snapPointPolarConstrain(self, point1 : pya.DPoint, point2 : pya.DPoint, edge_point : Union[pya.DEdge, pya.DPoint]): 
        '''
            snap with polar track constrain
            point 1 : first cursor click point
            point 2 : current cursor real location
        '''
        point      = self.snapPolarTrack(point1, point2)
        cursorLine = pya.DEdge(point1, point)
        crossLine  = None
        if isinstance(edge_point, pya.DPoint):
            guideVec  = pya.DVector(0, 1) if (cursorLine.dx() > 0) else pya.DVector(1, 0)
            crossLine = pya.DEdge(edge_point, edge_point + guideVec)

                
        if isinstance(edge_point, pya.DEdge):            
            crossLine = edge_point
        
        return point if crossLine.is_parallel(cursorLine)else crossLine.cut_point(cursorLine)          	
    
    def snapToObject(self, *args, **argv):
        paramCount = len(args) + len(argv)
        if paramCount == 3:
            return self.snapToObject1Point(*args, **argv)
            
        if paramCount == 4:   
            if (self.snapOctDir or self.snapQuadDir):
                return self.snapToObject2Point(*args, **argv)
            else:
                return self.snapToObject1Point(*args[1::], **argv)

    def snapToObject1Point(self, p : pya.DPoint, detectRange : Union[int, float], hoverShapes : List[pya.DPolygon]):
        '''
            snap without polar track constrain
        '''
        return self.snapToObject2Point(point1 = None, point2 = p, detectRange = detectRange, hoverShapes = hoverShapes)

    def snapToObject2Point(self, point1 : pya.DPoint, point2 : pya.DPoint, detectRange : Union[int, float], hoverShapes : List[pya.DPolygon]):
        '''
            snap with polar track constrain
            point 1 : first cursor click point
            point 2 : current cursor real location
            snap to line centr and shape center abnormal
        '''
        p                = point2
        minDistance      = detectRange
        rangeDVector     = pya.DVector(detectRange, detectRange)
        rangeDBox        = pya.DBox(p - rangeDVector, p + rangeDVector)
        centerShapes     = sorted(hoverShapes, key = lambda hoveredShape: hoveredShape.bbox().center().distance(p))[0:10] if self.snapCenter else []
        hlVertex         = None
        hlEdge           = None
        hlCenter         = None
        snapPoint        = self.snapPolarTrack(point1, point2) if point1 else point2
        vtxSnapRatio     = 2
        
        for hoveredShape in hoverShapes:
            itemList = [] 
            center   = hoveredShape.bbox().center()  
            for e in hoveredShape.each_edge():
                if self.objInRngHdl.edgeInRange( p, e, detectRange, sideOnly = False):
                    ppc = pya.DPoint((e.p1.x + e.p2.x)/2, (e.p1.y + e.p2.y)/2)
                    if self.snapEdge       and self.objInRngHdl.edgeInRange(  p, e,      detectRange): itemList.append(e)
                    if self.snapVertex     and self.objInRngHdl.vertexInRange(p, e.p1,   detectRange): itemList.append(e.p1)
                    if self.snapVertex     and self.objInRngHdl.vertexInRange(p, e.p2  , detectRange): itemList.append(e.p2)
                    if self.snapEdgeCenter and self.objInRngHdl.vertexInRange(p, ppc,    detectRange): itemList.append(ppc)
            if self.snapCenter         and self.objInRngHdl.vertexInRange(p, center, detectRange): itemList.append(center)
            
            for i in itemList:
                dist = i.distance_abs(p) if isinstance(i, pya.DEdge) else i.distance(p)
                if (dist <= minDistance) if isinstance(i, pya.DEdge) else (dist <= detectRange * 2):
                    snapPoint   = self.snapPoint(point1, p, i) if point1 else self.snapPoint(p, i)
                    minDistance = dist
                    hlVertex    = None if isinstance(i, pya.DEdge) else i
                    hlEdge      = i    if isinstance(i, pya.DEdge) else None
            
        self.drawHighlight(snapPoint, detectRange, centerShapes, hlCenter, hlVertex, hlEdge)
        return snapPoint
        
    def drawHighlight(self, snapPoint, detectRange, centerShapes, hlCenter, hlVertex, hlEdge):
        cursorCrossLen   = misc.dPixelLength(self.view, 20)
        vertexCrossLen   = misc.dPixelLength(self.view, 20)
        centerCrossLen   = misc.dPixelLength(self.view,  5)
        edgeCrossLen     = misc.dPixelLength(self.view, 20)
        edgeArrowLen     = misc.dPixelLength(self.view, 20)
        self.markPropsAppend([mkThm.centerMark(centerShape, centerCrossLen) for centerShape in centerShapes])
        
        if hlCenter             : self.markPropsAppend(mkThm.cursorMark( snapPoint, cursorCrossLen))
        if hlVertex             : self.markPropsAppend(mkThm.vertexMark( hlVertex, vertexCrossLen))
        if self.showSearchRange : self.markPropsAppend(mkThm.detectRangeMark( p,  detectRange))  
        if not any([hlCenter, hlVertex]): self.markPropsAppend(mkThm.cursorMark(snapPoint, cursorCrossLen))
        
        if hlEdge               : 
            self.markPropsAppend(mkThm.edgeArrowMark( hlEdge, edgeArrowLen, 1))
            if self.snapEdgeCenter  : self.markPropsAppend(mkThm.edgeCenterMark(  hlEdge,    edgeCrossLen))  
             
if __name__ == "__main__":
    snHdl = SnapHandler(pya.LayoutView())
