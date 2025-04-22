import numpy as np 
from shapely import box, difference, unary_union 

def boundary(
    design, 
    pos_x=0, pos_y=0, 
    length='10mm', height='10mm', thick='50um',
    buffer='30um', corner_size='250um'
): 
    pos_x, pos_y    = design.parse_value([pos_x, pos_y])
    lx, ly          = design.parse_value([length, height]) 
    thick, corner_size = design.parse_value([thick, corner_size])

    outer_edge = np.array([pos_x-lx/2, pos_y-ly/2, pos_x+lx/2, pos_y+ly/2]) 
    inner_edge = np.add(outer_edge, [+thick, +thick, -thick, -thick])

    outer_box = box(outer_edge[0], outer_edge[1], outer_edge[2], outer_edge[3]) 
    inner_box = box(inner_edge[0], inner_edge[1], inner_edge[2], inner_edge[3]) 
    boundary = difference(outer_box, inner_box)

    tl_corner = box(
        pos_x-lx/2, 
        pos_y+ly/2-corner_size,
        pos_x-lx/2+corner_size,
        pos_y+ly/2, 
    ) 

    tr_corner = box(
        pos_x+lx/2-corner_size, 
        pos_y+ly/2-corner_size, 
        pos_x+lx/2,
        pos_y+ly/2
    )

    bl_corner = box( 
        pos_x-lx/2, 
        pos_y-ly/2,
        pos_x-lx/2+corner_size,
        pos_y-ly/2+corner_size, 
    )

    br_corner = box(
        pos_x+lx/2-corner_size, 
        pos_y-lx/2, 
        pos_x+lx/2, 
        pos_y-lx/2+corner_size, 
    ) 

    boundary = unary_union([tl_corner, tr_corner, bl_corner, br_corner, boundary]) 
    no_cheese= boundary.buffer(distance=design.parse_value(buffer), quad_segs=30) 

    design.qgeometry.add_qgeometry( 
        'poly', 
        geometry        = {'chip_buffer': no_cheese}, 
        component_name  = 'chip_buffer', 
        subtract        = True, 
        layer           = 2, 
    )

    design.qgeometry.add_qgeometry(
        'poly', 
        geometry        = {'chip_boundary': boundary}, 
        component_name  = 'chip_boundary', 
        subtract        = True, 
        layer           = 0, 
    )





