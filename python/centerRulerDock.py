import os 
import re
import sys
import pya

iconPath = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "icon"))
class CenterRulerSetupDock(pya.QDockWidget):
    def __init__(self):
        super(CenterRulerSetupDock, self).__init__()
        self.ctrSetup = CenterRulerSetupWidget()
        self.setWidget (self.ctrSetup)
        self.setWindowTitle("Center Ruler")
        self.visibilityChanged(lambda : self.host.deactive())

    def setHost(self, host):
        self.ctrSetup.setHost(host)
        
    def setRulerTempIndex(self, indexTitle):
        self.ctrSetup.setRulerTempIndex(indexTitle)
        
    def updateHostValue(self):
        self.ctrSetup.updateHostValue()
        
class CenterRulerSetupWidget(pya.QWidget):
    def __init__(self):
        super(CenterRulerSetupWidget, self).__init__()
        self.host         = None
        self.template     = []

        self.rulerTypeLt  = pya.QListWidget()
        self.reportBugPB  = pya.QPushButton()
        self.swapHotKeyPB = pya.QPushButton()
        self.layout       = pya.QGridLayout()
        self.container    = []
        
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.rulerTypeLt,   0, 0, 1, 4)
        self.layout.addWidget(self.swapHotKeyPB,  1, 2, 1, 1)
        self.layout.addWidget(self.reportBugPB,   1, 3, 1, 1)
        self.layout.setRowStretch(0, 1)
        
        self.setupButton(self.swapHotKeyPB, iconPath + '\\hotkey.png',     lambda : SwapHotKeyDialog().show())
        self.setupButton(self.reportBugPB,  iconPath + '\\bug-report.png', lambda : ReportBugDialog().show())

        self.rulerTypeLt.currentItemChanged  (lambda :self.updateHostValue())
        self.setFixedWidth(200)
        self.setLayout(self.layout)
        
    def setupButton(self, button, imgPath, func):
        button.setFlat(True)
        button.setIcon(pya.QIcon(imgPath))
        button.setIconSize(pya.QSize(25, 25))   
        button.setFixedSize(pya.QSize(35, 35))
        button.clicked(func)
        
    def setHost(self, host) : 
        self.host = host
        if self.host:
            currentRow = self.rulerTypeLt.currentRow if self.rulerTypeLt.currentRow >= 0 else 0
            hostTitle  = self.host.rulerTemplate["title"] 
            selfTitle  = self.template[currentRow]["title"] if self.template else ""
            rulerTitle = hostTitle if hostTitle else selfTitle
            
            self.updateRulerItem()
            self.setRulerTempIndex(rulerTitle)
            self.updateHostValue()

    def setRulerTempIndex(self, indexTitle):
        index      = 0
        itemCounts = len(self.template)
        
        if self.host and ( itemCounts > 0): 
            
            if isinstance(indexTitle, str):
                titleList = [t["title"] for t in self.template]
                if indexTitle in titleList:
                    index = titleList.index(indexTitle)
                    
            if isinstance(indexTitle, int):
                index = max([indexTitle , 0])
                
            index = min([index, itemCounts -1])
            self.rulerTypeLt.setCurrentRow(index)
            self.updateHostValue()

    def updateHostValue(self): 
        if self.host: 
            row = self.rulerTypeLt.currentRow
            if row in range(len(self.template)):
                self.host.rulerTemplate = self.template[row]
                
    def updateRulerItem(self):
        self.container = []
        self.template  = self.getRulerTemplates()
        self.rulerTypeLt.clear() 
        
        for i, tpl in enumerate(self.template):
            itemWidget     = RulerItemWidget()
            listItemIidget = pya.QListWidgetItem()              
            itemWidget.setValue(tpl["title"], f"Ctrl + {i+1}" if i < 9 else " N / A ")
            listItemIidget.setSizeHint(itemWidget.sizeHint())
            self.container.append(itemWidget)
            self.rulerTypeLt.addItem(listItemIidget)
            self.rulerTypeLt.setItemWidget(listItemIidget, itemWidget)
 
    def showEvent(self, event):
        self.updateRulerItem()
        event.accept()
    
    def hideEvent(self, event):
        if self.host:
            self.host.deactive()
        event.accept()
        
    def getRulerTemplates(self):
        mainWindow = pya.Application.instance().main_window()
        templates  = []
        
        for template in mainWindow.get_config("ruler-templates-v2").split(";"):
            templateStr = []
            title       = ""
            points      = 2
            
            for configs in template.split(","):
                if not(configs.split("=")[0] in ["mode", "title", "version"]):
                    templateStr.append(configs)
                    
                if (configs.split("=")[0]  == "title"): 
                    title = configs.split("=")[1]
                    
                if (configs.split("=")[0]  == "mode"): 
                    points, mode = {
                        "auto_metric"   : ( 1, pya.Annotation.RulerModeAutoMetric),
                        "single_click"  : ( 1, pya.Annotation.RulerModeSingleClick),
                        "normal"        : ( 2, pya.Annotation.RulerModeNormal),
                        "angle"         : ( 3, pya.Annotation.RulerThreeClicks),  
                        "multi_segment" : (-1, pya.Annotation.RulerMultiSegment),             
                    }[configs.split("=")[1]]

            
            ruler =  pya.Annotation.from_s(",".join(templateStr))
            templates.append({"title" : title, "template" : ruler, "points" : points, "mode" : mode})
            
        return templates
        
        
class RulerItemWidget(pya.QWidget):
    def __init__(self):
        super(RulerItemWidget, self).__init__()  

    
    def setValue(self, *args):
        height, wBase, wInc= 15, 5, 5
        title          = args[0]
        hotKeys        = re.split('(\+)', args[1])
        titleLB        = pya.QLabel(args[0])
        self.container = []
        self.layout    = pya.QHBoxLayout()
        styleSheetList = [
        "QLabel{",
            "color               : #909090;",
            "font                : 8pt 'Times';", 
            "qproperty-alignment : AlignCenter;",
            "background-color    : #e2e2e2;",
            "border-color        : #909090;",
            "border-style        : solid;",
            "border-width        : 1px;", 
            "border-radius       : 3px;",
            "",
        ]
        
        self.container.append(titleLB)
        for index, keyStr in enumerate(hotKeys):
            keyLabel = pya.QLabel(keyStr)
            keyLabel.setFixedSize(pya.QSize(wBase + len(keyStr) * wInc, height))
            keyLabel.setStyleSheet("".join(styleSheetList[0:4 if keyStr == "+" else -1] + ["}"]))
            self.container.append(keyLabel)

        for w in self.container : self.layout.addWidget(w)              
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(5, 2, 2, 5)
        self.setLayout(self.layout)

class ReportBugDialog(pya.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Report Bugs")
        self.container = []
        self.layout    = pya.QVBoxLayout()
        self.buttonBox = pya.QDialogButtonBox()
        self.msgLinks  = [
            ["Got any questions? Please check the Doc page:",
             "https://github.com/s910324/CenterRulerPlugin/"],
             
            ["Found any bug? Please give us feedback:",
             "https://github.com/s910324/CenterRulerPlugin/issues"]
        ]

        self.buttonBox.accepted(lambda : self.close())
        self.buttonBox.addButton("OK", pya.QDialogButtonBox.AcceptRole)
        self.layout.addLayout(self.addMsgLinks(self.msgLinks))
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        
    def urlToClipboard(self, url):  
        clipBoard = pya.Application.instance().clipboard()
        clipBoard.clear()
        clipBoard.setText(url)
        pya.QToolTip().showText( pya.QCursor.pos, f'link copy to clipboard : {url}')
        
    def addMsgLinks(self, msgLinks = []):
        self.mlLayout  = pya.QGridLayout()
        for i, msgLink in enumerate(msgLinks):
            pitch   = i * 2
            msg     = msgLink[0]
            url     = msgLink[1]
            msgLB   = pya.QLabel(msg)
            urlEdit = pya.QLineEdit(url)
            copyPB  = pya.QPushButton()
            openPB  = pya.QPushButton()
            self.container += [msgLB, urlEdit, copyPB, openPB]
            
            copyPB.setIcon(pya.QIcon(iconPath + '\link.png'))
            openPB.setIcon(pya.QIcon(iconPath + '\web.png'))
            copyPB.clicked(lambda _, link = url : self.urlToClipboard(link))
            openPB.clicked(lambda _, link = url : pya.QDesktopServices.openUrl(pya.QUrl(link)))
            
            self.mlLayout.addWidget(msgLB,   0 + pitch, 0, 1, 3)
            self.mlLayout.addWidget(urlEdit, 1 + pitch, 0, 1, 1)
            self.mlLayout.addWidget(copyPB,  1 + pitch, 1, 1, 1)
            self.mlLayout.addWidget(openPB,  1 + pitch, 2, 1, 1)
        self.mlLayout.setColumnMinimumWidth(0, 300)
        self.mlLayout.setColumnStretch(0, 1)
        return self.mlLayout
              
class SwapHotKeyDialog(pya.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Swap hotkey")
        
        dHotkey, cHotkey = self.getHotKey()
        self.messages    = "\n\n".join([
            f"Confirm Swap Hotkey?",
            f"Default Ruler hot key     [{dHotkey}]  ➜  [{cHotkey}].",
            f"Center  Ruler hot key     [{cHotkey}]  ➜  [{dHotkey}].",
            f"",
        ])
        
        self.layout    = pya.QVBoxLayout()
        self.messageLB = pya.QLabel(self.messages)
        self.buttonBox = pya.QDialogButtonBox()
        self.buttonBox.accepted(lambda : self.setHotKey(cHotkey, dHotkey))
        self.buttonBox.rejected(lambda : self.close())
        
        self.buttonBox.addButton("Cancel",  pya.QDialogButtonBox.RejectRole)
        self.buttonBox.addButton("Confirm", pya.QDialogButtonBox.AcceptRole)
        
        self.layout.addWidget(self.messageLB)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def getHotKey(self):
        mainWindow   = pya.Application.instance().main_window().instance()
        keyBindDict  = mainWindow.get_key_bindings()
        defaultRuler = "edit_menu.mode_menu.ruler"
        centerRuler  = "edit_menu.mode_menu.center_ruler_factory"
        defaultKey   = keyBindDict[defaultRuler] if (defaultRuler in keyBindDict) else ""
        centerKey    = keyBindDict[centerRuler]  if (centerRuler  in keyBindDict) else ""
        return [defaultKey, centerKey]
        
    def setHotKey(self, defaultKey, centerKey):
        mainWindow   = pya.Application.instance().main_window().instance()
        defaultRuler = "edit_menu.mode_menu.ruler"
        centerRuler  = "edit_menu.mode_menu.center_ruler_factory"
        mainWindow.set_key_bindings({ defaultRuler : defaultKey, centerRuler : centerKey })
        self.close()
        
if __name__ == "__main__":
    #'''
    crsw = CenterRulerSetupWidget()
    crsw.show()
    
    
    '''
    for tpl in crsw.getRulerTemplates():
        print (tpl)
    
    rbd = ReportBugDialog()
    rbd.show()
    '''
    