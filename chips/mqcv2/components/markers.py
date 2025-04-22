from qiskit_metal.qlibrary.QNLMetal.alignmentmarker import AlignmentMarker 
from qiskit_metal import Dict 

def markers(design, main_x, main_y, key): 

    r_align_marker_xoffset= design.parse_value('2500um')
    r_align_marker_yoffset= design.parse_value('3388um')
    align_marker_gap = design.parse_value('8400um')

    pos_x = main_x + r_align_marker_xoffset
    pos_y = main_y + r_align_marker_yoffset
    
    if key == 'upper_right' : 
        pos_x, pos_y = pos_x, pos_y
    elif key == 'upper_left': 
        pos_x -= align_marker_gap
    elif key == 'lower_right':
        pos_y -= align_marker_gap
    elif key == 'lower_left': 
        pos_x -= align_marker_gap
        pos_y -= align_marker_gap
    else: raise ValueError(f"Invalid Key: {key}") 

    AlignmentMarker(design, name=f'{key}_marker', options=Dict(
        pos_x=pos_x, 
        pos_y=pos_y, 
        size='20um', 
    ))
