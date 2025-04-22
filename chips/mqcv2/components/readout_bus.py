from qiskit_metal.qlibrary.QNLMetal.inlineidc import InlineIDC 
from qiskit_metal.qlibrary.terminations.short_to_ground import ShortToGround 
from qiskit_metal.qlibrary.terminations.open_to_ground import OpenToGround 
from qiskit_metal.qlibrary.tlines.straight_path import RouteStraight 
from qiskit_metal.qlibrary.terminations.launchpad_wb import LaunchpadWirebond 
from qiskit_metal import Dict 
import numpy as np 


def readout_bus(design, idc_pos_x=0, idc_pos_y=0, length='6950um', name='readout_bus'): 
    """
    Renders a readout-bus to the design. 

    Args: 
        * design (qiskit_metal.designs.DesignPlanar): 
            Chip design. 
        * idc_pos_x/y (float or string): 
            x, y position of the InlineIDC origin.
        * length (float or string): 
            Length of the readout bus.
        * name (string): 
            Starting name of readout bus sub_components in design. 

    """


    idc = InlineIDC(design, options=Dict(pos_x=idc_pos_x, pos_y=idc_pos_y)) 
    idc.make()
    idc_upper_node = idc.node('cpw0')
    idc_lower_node = idc.node('cpw1')

    bus_start = ShortToGround(
        design, 
        f'{name}_start', 
        options=Dict(
            pos_x=idc_upper_node[0], 
            pos_y=idc_upper_node[1], 
            orientation='270', 
        )
    ) 

    bus_end = OpenToGround(
        design, 
        f'{name}_end', 
        options=Dict(
            pos_x=idc_upper_node[0], 
            pos_y=idc_upper_node[1] + design.parse_value(length),
            orientation='90', 
            termination_gap='65um', 
            width='65um', 
            gap='0um', 
        )
    )

    RouteStraight(
        design, 
        name, 
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
        'pos_x': idc_lower_node[0], 
        'orientation'   : '90', 
        'lead_length'   : '793.5um', 
        'pad_width'     : '375um', 
        'pad_height'    : '125um', 
        'taper_height'  : '100um', 
        'trace_gap'     : '17.5um', 
        'trace_width'   : '30um', 
    }
    launch_options['pos_y'] = idc_lower_node[1] - design.parse_value(launch_options['lead_length'])
    LaunchpadWirebond(design, name=f'{name}_launch', options=launch_options) 

    nodes = Dict() 
    nodes.right = np.array([idc_pos_x+design.parse_value('15um')+design.parse_value('17.5um'), idc_pos_y]) 
    nodes.left  = np.array([idc_pos_x-design.parse_value('15um')-design.parse_value('17.5um'), idc_pos_y]) 
    return nodes


