import os 
import pya
import math
import time
import functools

import misc
import snapHandler       as snHdl
import markerHandler     as mkHdl
import markerTheme       as mkThm 
import objInRangeHandler as oirHdl
import centerRulerDock   as crd


class CenterRulerPlugin(pya.Plugin):
    dock = None
    def __init__(self, view):
        super(CenterRulerPlugin, self).__init__()
        self.ctrlDock        = None
        self.initiallize(view)
        
    def initiallize(self, view):        
        self.view            = view
        self.cellView        = None
        self.cell            = None
        self.cursor          = pya.Cursor.Arrow
        self.snappedPoint    = None
        self.rulerPoints     = []
        self.rulerTemplate   = {"title" : "", "template" : pya.Annotation(), "points" : 2, "mode" : pya.Annotation.RulerModeNormal}
        self.withSelected    = False
        self.selectedObjs    = []
        self.selectedAnts    = []
        self.selectedObjBox  = None
        
        self.snapHandler     = snHdl.SnapHandler(self.view)        
        self.stdRulerHandler = mkHdl.RulerHandler(self.view)
        self.objInRngHdl     = oirHdl.ObjInRangeHandler(self.view)
        self.markerManager   = mkHdl.MarkerManager([self.stdRulerHandler, self.snapHandler])
        
        self.snapHandler.setSnapPolicy(snHdl.SnapPolicy.snapDefault | snHdl.SnapPolicy.snapEdgeCenter)


    def validselect(self):
        self.cellView     = self.view.active_cellview()
        self.cell         = self.cellView.cell

        self.selectedObjs = [o for o in self.view.each_object_selected() if (not(o.is_cell_inst()) and (o.shape.polygon))]
        self.selectedAnts = [o for o in self.view.each_annotation_selected()]
        
        self.withSelected = False
        
        if self.selectedObjs or self.selectedAnts:
            boxList      = [o.box() for o in self.selectedAnts]
            
            for o in self.selectedObjs:
                cellView = self.view.cellview(o.cv_index)
                cell     = cellView.cell
                unit     = cellView.layout().dbu
                boxList.append(o.shape.polygon.transformed(o.trans()).to_dtype(unit).bbox())
                
            self.selectedObjBox = functools.reduce(lambda a, b: a+b, boxList)
            self.rulerPoints = [self.selectedObjBox.center(), self.selectedObjBox.center()]
        self.withSelected = True

              
    def activated(self):
        self.initiallize(self.view)
        self.validselect()
        self.showDock()

    def deactivated(self):
        self.markerManager.clearAll()
        self.markerManager.updateAll()
        self.initiallize(self.view)
        if (self.ctrlDock) : self.ctrlDock.hide()
        self.ungrab_mouse()
            
    def deactive(self):
        esc_key  = 16777216 
        keyPress = pya.QKeyEvent(pya.QKeyEvent.KeyPress, esc_key, pya.Qt.NoModifier)
        pya.QApplication.sendEvent(self.view.widget(), keyPress)
    
    def exitOnViewChangd(self):  
        # might not be required, implement this will 
        # deactive by this does not clear markers correctly
        cellViewChanged = not(self.cellView == self.view.active_cellview())
        cellChanged     = not(self.cell     == self.cellView.cell)
        
        if any([cellViewChanged, cellChanged]):
            tip = "Cell view changed, cancel operation"
            tooltip = pya.QToolTip()
            tooltip.showText( pya.QCursor.pos, f'\n\t{tip}\t\t\n')
            self.deactive()
            
    def showDock(self):
        if not(CenterRulerPlugin.dock):
            mw   = pya.Application.instance().main_window()
            dock = crd.CenterRulerSetupDock()
            CenterRulerPlugin.dock = dock
            mw.addDockWidget(pya.Qt_DockWidgetArea.RightDockWidgetArea, dock)
            
        if not(self.ctrlDock):
            self.ctrlDock = CenterRulerPlugin.dock
            
        self.ctrlDock.setHost(self)
        self.ctrlDock.show()
        
    def key_event	(self, key, buttons):
        if (buttons == misc.Keys.ctrl) and (misc.Keys.num_1 <= key <= misc.Keys.num_9):
            self.ctrlDock.setRulerTempIndex(key - misc.Keys.num_1)
           
    def enter_event(self, prio):
        if prio:
            self.showDock()
            return True
        return False
    
    def mouse_double_click_event(self, p, buttons, prio):
        if prio:
            if (buttons & misc.Keys.left):
                self.cursor = pya.Cursor.Arrow
                self.markerManager.unbindRulers()
                self.rulerPoints = []
                self.markerManager.updateAll()
                
            return True
        return False
            
    def mouse_click_event(self, p, buttons, prio):
        if prio:

            if (buttons & misc.Keys.left):
            
                rulerProps = {
                    "data"     : self.rulerPoints, 
                    "template" : self.rulerTemplate["template"]
                }
                
                self.cursor = pya.Cursor.Cross
                clickPts    = self.rulerTemplate["points"]
                rulerMode   = self.rulerTemplate["mode"]
                rulerPts    = len(self.rulerPoints)
                rulerAtv    = True in [clickPts == 1, clickPts == -1, clickPts > rulerPts]
                
                if rulerAtv:
                    if rulerMode == pya.Annotation.RulerModeAutoMetric:
                        autoRuler = self.view.create_measure_ruler(self.snappedPoint)
                        self.rulerPoints += [autoRuler.p1, autoRuler.p2]
                        autoRuler.delete()
                        autoRuler._destroy()
                    else:
                        self.rulerPoints += [self.snappedPoint] * (2 if rulerPts == 0 else 1 )
                else:
                    self.rulerPoints[-1] = self.snappedPoint

                self.stdRulerHandler.rulerPropsAppend(rulerProps)
                self.markerManager.updateRulers()       
                
                if clickPts == 1 or not(rulerAtv):
                    self.cursor = pya.Cursor.Arrow
                    self.markerManager.unbindRulers()
                    self.rulerPoints = []     

            
            return True
        return False
    

    
    def mouse_moved_event(self, p, buttons, prio):
        if prio:
            
            self.set_cursor(self.cursor)
            
            if (buttons & misc.Keys.ctrl):
                self.snapHandler.addSnapPolicies(snHdl.SnapPolicy.snapOctDir)

            elif (buttons & misc.Keys.shift):
                self.snapHandler.addSnapPolicies(snHdl.SnapPolicy.snapQuadDir)

            else : 
                self.snapHandler.removeSnapPolicies(snHdl.SnapPolicy.snapOctDir)

            
            searchRange       = min([misc.dPixelLength(self.view, 25), 50])
            sizeLimit         = misc.dPixelLength(self.view, 5)
            rangeDBox         = pya.DBox(pya.DPoint(p.x - searchRange, p.y - searchRange),pya.DPoint(p.x + searchRange, p.y + searchRange))
            hoverShapes       = self.objInRngHdl.visibleShapeInCVRange(rangeDBox, sizeLimit) ## performance killer
            self.snappedPoint = p
 
            if   len(self.rulerPoints) == 0 :
                self.snappedPoint = self.snapHandler.snapToObject(p, searchRange, hoverShapes)  ## performance killer
   
            elif len(self.rulerPoints) >= 2 :
                point1 = self.rulerPoints[-2]
                point2 = p
                self.snappedPoint = self.snapHandler.snapToObject(point1, point2, searchRange, hoverShapes)
                
                self.rulerPoints[-1] = self.snappedPoint
                self.stdRulerHandler.rulerPropsAppend([
                    {
                        "data"     : self.rulerPoints, 
                        "template" : self.rulerTemplate["template"]
                    }
                ])


            self.markerManager.updateAll()

            return True
        return False
        
if __name__ == "__main__":
    mainWindow = pya.Application.instance().main_window()
    layoutView = mainWindow.current_view()  
    CenterRulerPlugin(layoutView)