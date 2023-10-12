import pya
import time
import misc
from typing import Union, Dict, List


class ObjInRangeHandler:
    def __init__(self, view : pya.LayoutView):
        self.view = view
        
    def vertexInRange(self, point : pya.DPoint, vertex : pya.DPoint, detectRange : Union[int, float]):
        inXRange   = (vertex.x - detectRange) <= point.x <= (vertex.x + detectRange)
        inYRange   = (vertex.y - detectRange) <= point.y <= (vertex.y + detectRange)
        detected   = all([inXRange, inYRange])
        return detected
        
    def edgeInRange(self, point : pya.DPoint, edge : pya.DEdge, detectRange : Union[int, float], sideOnly : bool = True):
        endLength  = detectRange if not(sideOnly) else 0
        detectArea = pya.DPath([edge.p1, edge.p2], detectRange * 2, endLength, endLength).simple_polygon()
        detected   = detectArea.inside(point)
        return detected
        
    def visibleCellViewLayers(self):
        result = {}
        itr = self.view.begin_layers()
        while not itr.at_end():
            lyp = itr.current()
            lid = lyp.layer_index()
            cvIndex = lyp.source_cellview
             
            if not(cvIndex in result):
                result[cvIndex] = []
                
            if lyp.visible and (lid >= 0): result[cvIndex].append(lid)
            itr.next()
        
        return result
    
    #performance killer
    def shapeRecInCVRange(self, rangeDBox : pya.DBox, cvLayerIDDict : Dict[int, List[int]], limitSize : float = -1):
        result          = []
        maxHier         = self.view.max_hier_levels
        minHier         = self.view.min_hier_levels
        
        for cvIndex in cvLayerIDDict:

            cellView    = self.view.cellview(cvIndex)
            layout      = cellView.layout()
            unit        = layout.dbu
            cell        = cellView.cell
            layerIDList = cvLayerIDDict[cvIndex]
            hiddenCells = [index for index in layout.each_cell_bottom_up() if cellView.is_cell_hidden(cellView.layout().cell(index))]

            rsiList     = []
            for li in layerIDList:
                rsiList += [rsi.dup() for rsi in cell.begin_shapes_rec_overlapping(li, rangeDBox) if (rsi.shape().darea() > limitSize * limitSize)]

            for i, rsi in enumerate(rsiList):
                treeNotHidden = True
                shapeTouched  = True
                hier          = 0
                
                for index, ie in enumerate(rsi.path()):
                    hier = index + 1
                    if ie.inst().cell_index in hiddenCells:
                        treeNotHidden = False
                        break
                
                if minHier > hier or hier >= maxHier : 
                    treeNotHidden = False
                    
                if treeNotHidden:
                    if rsi.shape().polygon:
                        if not(rsi.shape().polygon.transformed(rsi.trans()).to_dtype(unit).touches(rangeDBox)): 
                            shapeTouched = False
                           
                if False in [treeNotHidden, shapeTouched]:
                    rsiList[i] = None

                        
            result += rsiList
        return list(filter(None, result))
        
    def visibleShapeRecInCVRange(self, rangeDBox : pya.DBox, limitSize : float = -1):
        return self.shapeRecInCVRange(rangeDBox, self.visibleCellViewLayers(), limitSize)
                    
    def shapeInCVRange(self, rangeDBox : pya.DBox, cvLayerIDDict : Dict[int, List[int]], limitSize : float = -1):
        result = []
        for rsi in self.shapeRecInCVRange(rangeDBox, cvLayerIDDict, limitSize):
            if rsi.shape().polygon:
                unit = rsi.layout().dbu
                result.append(rsi.shape().polygon.transformed(rsi.trans()).to_dtype(unit))
        return result
        
    def visibleShapeInCVRange(self, rangeDBox : pya.DBox, limitSize : float = -1):
        return self.shapeInCVRange(rangeDBox, self.visibleCellViewLayers(), limitSize)


    def shapeRecInSideCVRange(self, rangeDBox : pya.DBox, cvLayerIDDict : Dict[int, List[int]], limitSize : float = -1):
        result = []
        
        for rsi in self.shapeRecInCVRange(rangeDBox, cvLayerIDDict, limitSize):
            if rsi.shape().polygon:
                unit = rsi.layout().dbu
                if rsi.shape().polygon.transformed(rsi.trans()).bbox().to_dtype(unit).inside(rangeDBox): 
                    result.append(rsi)
            else:
                result.append(rsi)
                
        return result
                            
    def visibleShapeRecInSideCVRange(self, rangeDBox : pya.DBox, limitSize : float = -1):
        return self.shapeRecInSideCVRange(rangeDBox, self.visibleCellViewLayers(), limitSize)