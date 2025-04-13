from qiskit_metal.qlibrary.terminations.open_to_ground import OpenToGround 
from qiskit_metal.qlibrary.terminations.short_to_ground import ShortToGround
from qiskit_metal.qlibrary.tlines.framed_path import RouteFramed
from qiskit_metal.qlibrary.tlines.straight_path import RouteStraight
from qiskit_metal.qlibrary.tlines.mixed_path import RouteMixed
from qiskit_metal.qlibrary.tlines.meandered import RouteMeander
from qiskit_metal.qlibrary.tlines.pathfinder import RoutePathfinder
from qiskit_metal.toolbox_metal.parsing import parse_value 
from qiskit_metal import Dict 
from collections import OrderedDict 
import numpy as np 

import numpy as np
from collections import OrderedDict

def coupling_resonator(design, pos_x, pos_y, flip_x=False, flip_y=False, name='coup_resonator_1'):
    fillets = [0.09, 0.09, 0.095, 0.09]

    anchors = OrderedDict()
    anchors[0]  = np.array([pos_x - 0.560, pos_y])
    anchors[1]  = np.array([anchors[0][0] - fillets[0], anchors[0][1] + fillets[0]])
    anchors[2]  = np.array([anchors[1][0], anchors[1][1] + 0.01])
    anchors[3]  = np.array([anchors[2][0] - fillets[0], anchors[2][1] + fillets[0]])
    anchors[4]  = np.array([anchors[3][0] - 0.5595, anchors[3][1]])
    anchors[5]  = np.array([anchors[4][0] - fillets[1], anchors[4][1] + fillets[1]])
    anchors[6]  = np.array([anchors[5][0], anchors[5][1] + 0.2])
    anchors[7]  = np.array([anchors[6][0] + fillets[1], anchors[6][1] + fillets[1]])
    anchors[8]  = np.array([anchors[7][0] + 0.63, anchors[7][1]])
    anchors[9]  = np.array([anchors[8][0] + fillets[2], anchors[8][1] + fillets[2]])
    anchors[10] = np.array([anchors[9][0] - fillets[2], anchors[9][1] + fillets[2]])
    anchors[11] = np.array([anchors[10][0] - 0.510224, anchors[10][1]])
    anchors[12] = np.array([anchors[11][0] - fillets[3], anchors[11][1] + fillets[3]])
    anchors[13] = np.array([anchors[12][0] + fillets[3], anchors[12][1] + fillets[3]])
    #anchors[14] = np.array([anchors[13][0] + 0.510224, anchors[13][1]])

    # inverts about x or y depending on flip_x/y
    for key in anchors:
        rel = anchors[key] - np.array([pos_x, pos_y])
        rel[0] = (-rel[0]) if flip_x else rel[0]
        rel[1] = (-rel[1]) if flip_y else rel[1]
        anchors[key] = np.array([pos_x, pos_y]) + rel

    orientation = '0' if not flip_x else '180'
    otgi = ShortToGround(design, f'{name}_otg_i', options=dict(
        pos_x=pos_x, 
        pos_y=pos_y, 
        orientation=orientation
    ))
    stgo = ShortToGround(design, f'{name}_stg_o', options=dict(
        pos_x=anchors[13][0]+0.510224, 
        pos_y=anchors[13][1], 
        orientation=orientation
    ))
    
    between_anchors = OrderedDict()
    for idx in range(len(anchors) + 1):
        between_anchors[idx] = "S"

    opts = Dict(
        pin_inputs=Dict(
            start_pin=Dict(
                component=otgi.name,
                pin='short',
            ),
            end_pin=Dict(
                component=stgo.name,
                pin='short',
            ),
        ),
        step_size='1um',
        #total_length='4.5mm', 
        trace_width='20um',
        trace_gap='10um', 
        anchors=anchors,
        between_anchors=anchors,
        fillet=fillets[0],
    )
    route = RoutePathfinder(design, name, options=opts)


