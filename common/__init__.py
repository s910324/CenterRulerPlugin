from importlib import reload
'''
marker handler : 
    draw/clear and store marker
    
marke manager :
    collect marker and do update, clear for all handlers
    
misc : 
    pixel to um converter
    vector rotate for marker drawing
    
object in range handler :
    check vertex, edge, shape in detection range
    
snap handler : 
    check object with minimum distance 
    provide snap point 
    draw corrosbonding hightlight marker

select handler : 
    check object with minimum distance 
    provide select object function
    draw corrosbonding hightlight marker


determine selection
make selection markers
turn to actual selection

Handlers : 
    Rulers Annotations : insert and delete Ruler annotation, lifetime and update is controlled by plugin
    Shape : for shape processing shape in --> shape out, does not involve operations that will modify layout

Plugin :
    interaction with view, control ruler / annotation update 
    process shape insert and modify


'''