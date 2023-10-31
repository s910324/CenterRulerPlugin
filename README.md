# CenterRulerPlugin
<p align="center">
<img align="middle" src="https://github.com/s910324/CenterRulerPlugin/assets/1561043/bed73a21-20e7-44ee-b8a4-dba87046cc4f" alt="installation" width="800"/>
</p>


# Installation and setup
This app can be installed through KLayout package manager
After installation the app can be accessed through toolbar, center ruler icon


# Functions 

<p align="center">
<img align="middle" src="https://github.com/s910324/CenterRulerPlugin/assets/1561043/09147b94-7963-4bc1-b680-532ba795210a" alt="installation" width="800"/>
</p>

<p align="center">
<img align="middle" src="https://github.com/s910324/CenterRulerPlugin/assets/1561043/0a89f692-60e2-485d-b4c9-a840f49614a8" alt="installation" width="800"/>
</p>

* Privide ruler measured from Shape/Object center
* Privide ruler measured from Ruler center (useful for measure from spacing center)
* Snape to Edges, midpoint of a Edge, Verties and Object Center
* Center point hightlighted when object being hovered
* Ruler style switch hotkey `ctrl + 1~9`to select preset Rulers



# Changelog
### 0.01
* bug fix : Snap object error caused by unused layers
* bug fix : Snap object error caused by Text objects
* improve : Ruler now support another Ruler as target object

### 0.02
* improve : Snap object performance improve by update search algorithm
* improve : Snap object performance improve by Limit center mark count to 10 
* improve : Snap object policy update to improve user experience
* improve : Snap object vertex size increased for better visibility

### 0.03
* bug fix : Ruler `undo` not working properly.
* bug fix : Snap object error caused by empty layers        
* bug fix : Snap object snap to shapes in hidden cells.
* bug fix : Snap object snap to shapes in hidden hierarchy levels                         
* bug fix : Snap object incorrect when mutiple different dbu cellview is loaded           
* bug fix : Hover hightlight when cursor enters shape bound box instead of actual shape.
* bug fix : Plugin create multiple dock when more then one layout is loaded.

* improve : Ruler support user pre-set templates.
* improve : Ruler templates can be switched by Ctrl + Num hotkey.
* improve : Ruler support arc, ellipse and auto measure.   
* improve : Ruler can perform continuous measurement without pre-selecting target.
* improve : Ruler angle can be locked to horizontal / vertical by Ctrl/Shift Key.         
* improve : Ruler hotkey swap for quick shortcut binding.
* improve : Snap object support snap to edge center.
* improve : Snap object hightlight looks and feels more generic.
* improve : Snap object support auto range, use screen px instead of um.
* improve : Snap object performance improve by drop shapes smaller than 4px.
* improve : Snap object performance improve by limit max search range.
* improve : In-app Bug report link

### 0.04 
* bug fix : Snap object vertex becomes much sensitive
* bug fix : Snap object snap to vertex during not working properly while using `ctrl` or `shift` to lock the angle
* bug fix : Snap object unable to snap to small distance under `ctrl` or `shift` mode is activated


