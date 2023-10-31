import pya
from typing      import Union, List
from dataclasses import dataclass

@dataclass
class MarkerTemplate:
    def __init__(self, data = None, color = None, dither_pattern = None, frame_color = None, 
    halo = None, line_style = None, line_width = None, vertex_size = None): 
        self.data           = data 
        self.color          = color
        self.dither_pattern = dither_pattern
        self.frame_color    = frame_color
        self.halo           = halo
        self.line_style     = line_style
        self.line_width     = line_width
        self.vertex_size    = vertex_size  

class MarkerHandler:
    def __init__(self, view : pya.LayoutView):
        self.view            = view
        self.defaultMkThm    = pya.Marker(view)
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
        for marker in self.activeMarkers:
            marker._destroy()
        self.activeMarkers = []
        
        for i, markProp in enumerate(self.markPropList):
            if isinstance(markProp, MarkerTemplate):
                dataSet = [markProp.data] if not isinstance(markProp.data, list) else markProp.data
                for data in dataSet:
                    marker = pya.Marker(self.view)
                    marker.set(data)
                    if markProp.color          is not None : marker.color          = markProp.color           
                    if markProp.dither_pattern is not None : marker.dither_pattern = markProp.dither_pattern  
                    if markProp.frame_color    is not None : marker.frame_color    = markProp.frame_color     
                    if markProp.halo           is not None : marker.halo           = markProp.halo            
                    if markProp.line_style     is not None : marker.line_style     = markProp.line_style      
                    if markProp.line_width     is not None : marker.line_width     = markProp.line_width      
                    if markProp.vertex_size    is not None : marker.vertex_size    = markProp.vertex_size  
                    self.activeMarkers.append(marker)  
                
        self.markPropList = []

    def markPropsAppend(self, markProps):
        if   isinstance(markProps, dict):
            if markProps["data"] : self.markPropList.append(markProps)
            
        elif isinstance(markProps, MarkerTemplate):
            if markProps.data : self.markPropList.append(markProps)
            
        elif isinstance(markProps, list):
            for markProp in markProps : self.markPropsAppend(markProp)
                
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
        
        
