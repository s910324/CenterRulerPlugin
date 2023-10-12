import pya
from typing import Union, List


class MarkerHandler:
    def __init__(self, view : pya.LayoutView):
        self.view            = view
        self.markPropList    = []
        self.activeMarkers   = []
        
    def handleType(self):
        return MarkerHandler
        
    def clearMarkers(self):
        for marker in self.activeMarkers:
            marker._destroy()
            
        self.markPropList  = []
        self.activeMarkers = []

    def updateMarkers(self):
        for marker in self.activeMarkers[len(self.markPropList) : -1]:
            marker._destroy()
        self.activeMarkers = self.activeMarkers[0 : len(self.markPropList)]

        for i, markProp in enumerate(self.markPropList):
            marker = None
            if i < len(self.activeMarkers):
                marker = self.activeMarkers[i] 
            else:
                marker = pya.Marker(self.view)
                self.activeMarkers.append(marker)
                
            marker.set(markProp["data"])
            marker.line_width  = markProp["theme"]["line_width"]
            marker.line_style  = markProp["theme"]["line_style"] 
            marker.vertex_size = markProp["theme"]["vertex_size"] 
            
        self.markPropList = []

    def markPropsAppend(self, markProps):
        if isinstance(markProps, dict):
            self.markPropList.append(markProps)
        elif isinstance(markProps, list):
            for markProp in markProps:
                self.markPropsAppend(markProp)
                
class RulerHandler:
    def __init__(self, view : pya.LayoutView):
        self.view          = view
        self.rulerPropList = []
        self.activeRulers  = []
    
    def handleType(self):
        return RulerHandler

    def clearRulers(self):
        for ruler in self.activeRulers:
            if ruler is not None:
                ruler.delete()
            ruler._destroy()
        self.activeRulers = []
    
    def unbindRulers(self):
        rulerBackup = [ruler.dup() for ruler in self.activeRulers]
        self.clearRulers()
        for ruler in rulerBackup: 
            self.view.transaction("add ruler")
            ruler.detach()
            try     : self.view.insert_annotation(ruler)
            finally : self.view.commit()

    def updateRulers(self):
        self.clearRulers()
        
        for rulerProp in self.rulerPropList:
            ruler         = rulerProp["template"].dup()
            ruler.points  = rulerProp["data"]

            self.view.insert_annotation(ruler)
            self.activeRulers.append(ruler)
            
        self.rulerPropList = []

             
    def rulerPropsAppend(self, rulerProps):
        if isinstance(rulerProps, dict):
            self.rulerPropList.append(rulerProps)
        elif isinstance(rulerProps, list):
            for rulerProp in rulerProps:
                self.rulerPropsAppend(rulerProp)
                               
class MarkerManager:
    def __init__(self, handlers : List[Union[MarkerHandler, RulerHandler]] = []):
        self.markerHdls = []
        self.rulerHdls  = []
        self.addHandlers(handlers)
        
    def addHandlers(self, handlers : List[Union[MarkerHandler, RulerHandler]]):
        for handler in handlers:
            if (handler.handleType() is MarkerHandler) : self.markerHdls.append(handler)
            if (handler.handleType() is RulerHandler)  : self.rulerHdls.append(handler)
                
    def unbindRulers(self):
        for handler in self.rulerHdls : handler.unbindRulers()
        
    def deleteAll(self):
        self.deleteMarkers() 
        self.deleteRulers()
              
    def deleteMarkers(self):
        self.clearMarkers()
        self.markerHdls = []
        
    def deleteRulers(self):
        self.clearRulers()
        self.rulerHdls = []
          
    def clearAll(self):
        self.clearMarkers() 
        self.clearRulers() 
        
    def clearMarkers(self):
        for handler in self.markerHdls : handler.clearMarkers()
        
    def clearRulers(self):
        for handler in self.rulerHdls : handler.clearRulers()
        
    def updateAll(self):
        self.updateMarkers() 
        self.updateRulers()
        
    def updateMarkers(self):
        for handler in self.markerHdls : handler.updateMarkers()

    def updateRulers(self):
        for handler in self.rulerHdls : handler.updateRulers()
        
        
