import pya
import math
from typing import Union, Dict, List
from   enum import IntEnum

import misc_001              as misc
import markerTheme_001       as mkThm
import markerHandler_001     as mkHdl
import objInRangeHandler_001 as oirHdl

class SelectPolicy(IntEnum):
    #selectVertex    = 0b00_00_00_000_01
    #selectEdge      = 0b00_00_00_000_10
    
    selectBox       = 0b00_00_00_001_00
    selectPath      = 0b00_00_00_010_00
    selectPolygon   = 0b00_00_00_100_00
    selectShape     = 0b00_00_00_111_00
    
    selectText      = 0b00_00_01_000_00
    #selectInstance  = 0b00_00_10_000_00
    
    #selectRuler     = 0b00_01_00_000_00
    #selectImage     = 0b00_10_00_000_00
    
    selectMultiple  = 0b01_00_00_000_00
    #selectPartial   = 0b00_00_00_000_11
    selectDefault   = 0b01_00_01_111_00
    
class SelectHandler(mkHdl.MarkerHandler):
    def __init__(self, view : pya.LayoutView, selectPolicy : SelectPolicy = SelectPolicy.selectDefault):
        super().__init__(view)
        self.objInRngHdl  = oirHdl.ObjInRangeHandler(view)   
        self.defaultPxRng = 4
        self.setSelectPolicy(selectPolicy)
        
    def setSelectPolicy(self, selectPolicy : SelectPolicy):
        self.selectPolicy    = selectPolicy
        #self.selectVertex    = (selectPolicy & SelectPolicy.selectVertex    ) > 0
        #self.selectEdge      = (selectPolicy & SelectPolicy.selectEdge      ) > 0
        self.selectBox       = (selectPolicy & SelectPolicy.selectBox       ) > 0
        self.selectPath      = (selectPolicy & SelectPolicy.selectPath      ) > 0
        self.selectPolygon   = (selectPolicy & SelectPolicy.selectPolygon   ) > 0
        self.selectShape     = (selectPolicy & SelectPolicy.selectShape     ) > 0
        #self.selectInstance  = (selectPolicy & SelectPolicy.selectInstance  ) > 0
        self.selectText      = (selectPolicy & SelectPolicy.selectText      ) > 0
        #self.selectRuler     = (selectPolicy & SelectPolicy.selectRuler     ) > 0
        #self.selectImage     = (selectPolicy & SelectPolicy.selectImage     ) > 0
        self.selectMultiple  = (selectPolicy & SelectPolicy.selectMultiple  ) > 0
        #self.selectPartial   = (selectPolicy & SelectPolicy.selectPartial   ) > 0
        self.selectDefault   = (selectPolicy & SelectPolicy.selectDefault   ) > 0
        
    def rsiPolicyCheck(self, rsi : pya.RecursiveShapeIterator):
        return any([
            self.selectPolicy & rsi.shape().is_box()     *  4,
            self.selectPolicy & rsi.shape().is_path()    *  8,
            self.selectPolicy & rsi.shape().is_polygon() * 16,
            self.selectPolicy & rsi.shape().is_text()    * 32,])
            
    def rsiToPolygonType(self, rsi : pya.RecursiveShapeIterator):
        if rsi.shape().is_box()     : return rsi.shape().polygon
        if rsi.shape().is_path()    : return rsi.shape().polygon
        if rsi.shape().is_polygon() : return rsi.shape().polygon
        if rsi.shape().is_text()    : return pya.Polygon(rsi.shape().bbox())
        
    
    def defaultHoveredObject(self, p  : pya.DPoint):
        searchRange = misc.dPixelLength(self.view, self.defaultPxRng)
        
        rangeDBox   = pya.DBox(
            pya.DPoint(p.x - searchRange, p.y - searchRange),
            pya.DPoint(p.x + searchRange, p.y + searchRange)
        )
        
        hoverRsi   = self.objInRngHdl.visibleShapeRecInCVRange(rangeDBox)
        return self.hoveredObject(p, searchRange, hoverRsi)
    
    def hoveredObject(self, p : pya.DPoint, detectRange : Union[int, float], hoverRsis : List[pya.RecursiveShapeIterator]):
        minDistance = math.inf
        hlShapeRsi  = []
     
        for rsi in hoverRsis:
            unit = rsi.layout().dbu

            if self.rsiPolicyCheck(rsi):
                                
                hoveredShape = self.rsiToPolygonType(rsi).transformed(rsi.trans()).to_dtype(unit)
                for e in hoveredShape.each_edge(): 
                    epDistance = e.distance_abs(p)
                    if  epDistance <= minDistance:
                        minDistance = epDistance
                        hlShapeRsi  = [rsi]
                         
        return hlShapeRsi
        
    def areaSelectedObject(self, rangeDBox : pya.DBox):
        result = []
        if self.selectPolicy & SelectPolicy.selectMultiple :
            for rsi in self.objInRngHdl.visibleShapeRecInSideCVRange( rangeDBox ):
                if self.rsiPolicyCheck(rsi):
                    result.append(rsi)
                    
        return result
            

if __name__ == "__main__":
    mainWindow = pya.Application.instance().main_window()
    layoutView = mainWindow.current_view()  
    SelectHandler(layoutView)