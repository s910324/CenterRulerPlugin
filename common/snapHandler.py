import pya
import math
import time
from typing import Union, Dict, List

from   enum import IntEnum

import misc
import markerTheme       as mkThm
import markerHandler     as mkHdl
import objInRangeHandler as oirHdl

# V20230925

class SnapPolicy(IntEnum):
    showSearchRange = 0b000_000001
    snapCenter      = 0b000_000010
    snapVertex      = 0b000_000100
    snapEdge        = 0b000_001000
    snapEdgeCenter  = 0b000_010000
    snapDefault     = 0b000_001110

    snapOctDir      = 0b111_000000
    snapQuadDir     = 0b011_000000
    
class SnapHandler(mkHdl.MarkerHandler):
    def __init__(self, view : pya.LayoutView, snapPolicy : SnapPolicy = SnapPolicy.snapDefault):
        super().__init__(view)
        self.objInRngHdl = oirHdl.ObjInRangeHandler(view)
        self.setSnapPolicy(snapPolicy)
        
    def setSnapPolicy(self, snapPolicy : SnapPolicy):
        self.snapPolicy      =  snapPolicy
        policySetter         = lambda policy : ((snapPolicy & policy) == policy)
        self.showSearchRange = policySetter(SnapPolicy.showSearchRange)
        self.snapCenter      = policySetter(SnapPolicy.snapCenter)     
        self.snapVertex      = policySetter(SnapPolicy.snapVertex)      
        self.snapEdge        = policySetter(SnapPolicy.snapEdge)        
        self.snapEdgeCenter  = policySetter(SnapPolicy.snapEdgeCenter)  
          
        self.snapOctDir      = policySetter(SnapPolicy.snapOctDir)
        self.snapQuadDir     = policySetter(SnapPolicy.snapQuadDir)
        
    def addSnapPolicies(self, policies : Union[SnapPolicy, List[SnapPolicy]]):
        result = self.snapPolicy
        if isinstance(policies, list):
            for policy in policies:
                result = result | policy
        else:
            result = result | policies
        
        self.setSnapPolicy(result)
            
    def removeSnapPolicies(self, policies : Union[SnapPolicy, List[SnapPolicy]]):
        result = self.snapPolicy
        if isinstance(policies, list):
            for policy in policies:
                result = (result | policy) - policy
        else:
            result = (result | policies) - policies
        
        self.setSnapPolicy(result)
                    
    def cursorMark(self, p : pya.DPoint):
        crossLength = misc.dPixelLength(self.view, 20)
        return mkThm.cursorMark(p, crossLength)

        
    def detectRangeMark(self, p : pya.DPoint, detectRange : Union[int, float]):
        return mkThm.detectRangeMark(p, detectRange)
             
    def centerMark(self, shape : pya.DPolygon):
        crossLength = misc.dPixelLength(self.view, 5)
        return mkThm.centerMark(shape, crossLength)
        
    def edgeMark(self, edge : pya.DEdge):
        arrowLength = misc.dPixelLength(self.view, 20)
        direction   = 1
        return mkThm.edgeArrowMark(edge, arrowLength, direction)
        
    def edgeCenterMark(self, edge : pya.DEdge):
        markLength  = misc.dPixelLength(self.view, 20)
        return mkThm.edgeCenterMark(edge, markLength)
                
    def vertexMark(self, p : pya.DPoint):
        crossLength = misc.dPixelLength(self.view, 20)
        return mkThm.vertexMark(p, crossLength)
    
    def snapPolarTrack(self, startPoint : pya.DPoint, endPoint : pya.DPoint):
        result = endPoint
        if (self.snapOctDir or self.snapQuadDir):
            v1         = pya.Vector(1, 0)
            v2         = endPoint - startPoint
            vp         = v1.vprod(v2)
            sp         = v1.sprod(v2)
            angle      = math.atan2(vp, sp) * 180.0 / math.pi
            pointSlant = (abs(v2.x) + abs(v2.y))/2.0
            snapARange = 22.5 if self.snapOctDir else 45.0

            if  (  90-snapARange <= abs(angle) <= 90 + snapARange):
                result = pya.DPoint(startPoint.x, endPoint.y)
                
            elif (  0+snapARange >= abs(angle)) or (180-snapARange <= abs(angle)):
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
                return pya.DPoint(point.x,(point.x - edge.p1.x)/dx * dy + edge.p1.y)
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
            return self.snapToObjectStandard(*args, **argv)
            
        if paramCount == 4:   
            if (self.snapOctDir or self.snapQuadDir):
                return self.snapToObjectPolarConstrain(*args, **argv)
            else:
                return self.snapToObjectStandard(*args[1::], **argv)


        
    def snapToObjectStandard(self, p : pya.DPoint, detectRange : Union[int, float], hoverShapes : List[pya.DPolygon]):
        '''
            snap without polar track constrain
        '''
        minDistance      = detectRange
        ranegDVector     = pya.DVector(detectRange, detectRange)
        rangeDBox        = pya.DBox(p - ranegDVector, p + ranegDVector)
        centerShapes     = sorted(hoverShapes, key = lambda hoveredShape: hoveredShape.bbox().center().distance(p))[0:10] if self.snapCenter else []
        hlVertex         = None
        hlEdge           = None
        hlCenter         = None
        snapPoint        = p
        
        self.markPropsAppend([self.centerMark(centerShape) for centerShape in centerShapes])
        
        for hoveredShape in hoverShapes:
            '''
                edge in box range
                check vertex/center points if vc, snap vc
            '''
            for e in hoveredShape.each_edge():
                if self.objInRngHdl.edgeInRange(p, e, detectRange):
                    epDistance  = e.distance_abs(p)

                    if epDistance <= minDistance:
                        minDistance = epDistance
                        snapPoint   = self.snapPoint(p, e) if self.snapEdge else p
                        hlEdge      = e                    if self.snapEdge else hlEdge
                        
                        ppc         = pya.DPoint((e.p1.x + e.p2.x)/2, (e.p1.y + e.p2.y)/2)
                        pointDists  = [
                            {"point" : e.p1, "distance" : e.p1.distance(p)},
                            {"point" : e.p2, "distance" : e.p2.distance(p)},
                            {"point" : ppc,  "distance" : ppc.distance(p)},
                        ]
                        pointDists = pointDists if self.snapEdgeCenter else pointDists[0:2]
                        pointDist  = sorted(pointDists, key = lambda pd : pd["distance"])[0]
                        ppDistance = pointDist["distance"]
                        hlVertex   = None
                        
                        if (ppDistance < (minDistance * 2)):
                            v = pointDist["point"]
                            if self.objInRngHdl.vertexInRange(p, v, detectRange):
                                snapPoint   = self.snapPoint(p, v) if self.snapVertex else p
                                hlVertex    = v                    if self.snapVertex else hlVertex

            center = hoveredShape.bbox().center()
            if self.objInRngHdl.vertexInRange(p, center, detectRange):
                cpDistance = center.distance(p)
                if (cpDistance < (minDistance * 2)):
                    snapPoint = self.snapPoint(p, center) if self.snapCenter else p
                    hlCenter  = center                    if self.snapVertex else hlCenter

        if hlCenter:
            self.markPropsAppend(self.cursorMark(snapPoint))
            
        else:
            
            if hlVertex:
                self.markPropsAppend(self.vertexMark(hlVertex))
                
            else:
                if hlEdge: 
                    self.markPropsAppend(self.edgeMark(hlEdge))
                
                    if self.snapEdgeCenter:
                        self.markPropsAppend(self.edgeCenterMark(hlEdge))
                    
                self.markPropsAppend(self.cursorMark(snapPoint))
                             
        if self.showSearchRange:
            self.markPropsAppend(self.detectRangeMark(p, detectRange))                                                    
        
        return snapPoint
    
    def snapToObjectPolarConstrain(self, point1 : pya.DPoint, point2 : pya.DPoint, detectRange : Union[int, float], hoverShapes : List[pya.DPolygon]):
        '''
            snap with polar track constrain
            point 1 : first cursor click point
            point 2 : current cursor real location
            snap to line centr and shape center abnormal
        '''
        
        minDistance      = detectRange
        ranegDVector     = pya.DVector(detectRange, detectRange)
        rangeDBox        = pya.DBox(point2 - ranegDVector, point2 + ranegDVector)       
        centerShapes     = sorted(hoverShapes, key = lambda hoveredShape: hoveredShape.bbox().center().distance(point2))[0:10] if self.snapCenter else []
        hlVertex         = None
        hlEdge           = None
        hlCenter         = None
        snapPoint        = self.snapPolarTrack(point1, point2)
        
        self.markPropsAppend([self.centerMark(centerShape) for centerShape in centerShapes])
        
        for hoveredShape in hoverShapes:
            '''
                edge in box range
                check vertex/center points if vc, snap vc
            '''
            for e in hoveredShape.each_edge():
                if self.objInRngHdl.edgeInRange(point2, e, detectRange):
                    epDistance  = e.distance_abs(point2)

                    if epDistance <= minDistance:
                        minDistance = epDistance
                        #point2      = self.snapPolarTrack(point1, point2)
                        snapPoint   = self.snapPoint(point1, point2, e) 
                        snapPoint   = snapPoint if self.snapEdge else point2
                        hlEdge      = e         if self.snapEdge else hlEdge
                        
                        ppc         = pya.DPoint((e.p1.x + e.p2.x)/2, (e.p1.y + e.p2.y)/2)
                        pointDists  = [
                            {"point" : e.p1, "distance" : e.p1.distance(point2)},
                            {"point" : e.p2, "distance" : e.p2.distance(point2)},
                            {"point" : ppc,  "distance" : ppc.distance(point2)},
                        ]
                        pointDists = pointDists if self.snapEdgeCenter else pointDists[0:2]
                        pointDist  = sorted(pointDists, key = lambda pd : pd["distance"])[0]
                        ppDistance = pointDist["distance"]
                        hlVertex   = None
                        
                        if (ppDistance < (minDistance * 2)):
                            v = pointDist["point"]
                            if self.objInRngHdl.vertexInRange(point2, v, detectRange):
                                snapPoint   = self.snapPoint(point1, point2, v) 
                                snapPoint   = snapPoint if self.snapVertex else point2
                                hlVertex    = v         if self.snapVertex else hlVertex

            center = hoveredShape.bbox().center()
            if self.objInRngHdl.vertexInRange(point2, center, detectRange):
                cpDistance = center.distance(point2)
                if (cpDistance < (minDistance * 2)):
                    snapPoint = self.snapPoint(point1, point2, center) 
                    snapPoint = snapPoint if self.snapCenter else point2
                    hlCenter  = center    if self.snapVertex else hlCenter

        if hlCenter:
            self.markPropsAppend(self.cursorMark(snapPoint))
            
        else:
            
            if hlVertex:
                self.markPropsAppend(self.vertexMark(hlVertex))
                
            else:
                if hlEdge: 
                    self.markPropsAppend(self.edgeMark(hlEdge))
                
                    if self.snapEdgeCenter:
                        self.markPropsAppend(self.edgeCenterMark(hlEdge))
                    
                self.markPropsAppend(self.cursorMark(snapPoint))
                             
        if self.showSearchRange:
            self.markPropsAppend(self.detectRangeMark(point2, detectRange))                                                    

        return snapPoint