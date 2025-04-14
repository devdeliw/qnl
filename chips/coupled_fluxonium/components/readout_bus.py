from qiskit_metal.qlibrary.terminations.launchpad_wb import LaunchpadWirebond
from qiskit_metal.qlibrary.terminations.short_to_ground import ShortToGround
from qiskit_metal.qlibrary.terminations.open_to_ground import OpenToGround 
from qiskit_metal.qlibrary.tlines.straight_path import RouteStraight
from qiskit_metal.qlibrary.QNLMetal.inlineidc import InlineIDC 
from qiskit_metal.toolbox_metal.parsing import parse_value 
from qiskit_metal import Dict 
import numpy as np

def readout_bus(design, pos_x=0, pos_y=0, name='readout_bus'): 
    idc = InlineIDC(design, options=Dict(pos_x=pos_x, pos_y=pos_y)) 

    upper_node = idc.node('cpw0') 
    lower_node = idc.node('cpw1') 

    bus_start = ShortToGround(design, 'bus_start', options=Dict(
        pos_x=upper_node[0], 
        pos_y=upper_node[1], 
        orientation='270', 
    )) 

    bus_end = OpenToGround(design, 'bus_end', options=Dict(
        pos_x=upper_node[0], 
        pos_y=upper_node[1]+parse_value('6950um', Dict()), 
        orientation='90', 
        termination_gap='65um',
        width='65um', 
        gap='0um', 
    ))

    bus = RouteStraight(design, 'bus', 
        options=Dict(
            pin_inputs=Dict(
                start_pin=Dict(
                    component=bus_start.name, 
                    pin='short', 
                ), 
                end_pin=Dict(
                    component=bus_end.name, 
                    pin='open', 
                ), 
            ),
            trace_gap='17.5um', 
            trace_width='30um', 
        ), 
    ) 
    
    launch_options = {
        'pos_x': lower_node[0], 
        'orientation': '90', 
        'lead_length': '793.5um', 
        'pad_width'  : '375um', 
        'pad_height' : '125um', 
        'taper_height': '100um', 
        'trace_gap'  : '17.5um', 
        'trace_width': '30um', 
    }
    launch_options['pos_y'] = lower_node[1] - parse_value(launch_options['lead_length'], Dict())
        
    launch = LaunchpadWirebond(design, name='launch', options=launch_options) 

    nodes = Dict() 
    nodes.right = np.array([pos_x+parse_value('15um', Dict())+parse_value('17.5um', Dict()), pos_y]) 
    nodes.left  = np.array([pos_x-parse_value('15um', Dict())-parse_value('17.5um', Dict()), pos_y]) 
    return nodes

    