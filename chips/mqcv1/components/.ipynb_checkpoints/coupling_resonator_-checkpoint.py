from qiskit_metal.qlibrary.tlines.pathfinder import RoutePathfinder
from qiskit_metal.qlibrary.terminations.open_to_ground import OpenToGround 
from qiskit_metal.qlibrary.terminations.short_to_ground import ShortToGround
from qiskit_metal.qlibrary.tlines.mixed_path import RouteMixed
from qiskit_metal.toolbox_metal.parsing import parse_value
from qiskit_metal import draw, Dict, MetalGUI, designs
from collections import OrderedDict
import numpy as np

def resonator(design, pos_x, pos_y, key='upper_left', name='resonator'): 
    if key == 'upper_doublet': 
        nodes = resonator_upper_left(design, pos_x, pos_y, name) 
    if key == 'lower_doublet': 
        nodes = resonator_lower_left(design, pos_x, pos_y, name) 
    if key == 'singlet': 
        nodes = resonator_singlet(design, pos_x, pos_y, name)
    if key == 'transmon': 
        nodes = resonator_transmon(design, pos_x, pos_y, name)
    if key == 'upper_left_doublet': 
        nodes= resonator_upper_doublet(design, pos_x, pos_y, name)
    if key == 'lower_left_doublet': 
        nodes= resonator_lower_doublet(design, pos_x, pos_y, name)

    return nodes

def resonator_upper_left(design, pos_x, pos_y, name='resonator'): 
    fillet = 0.075
    
    stg_in = ShortToGround( 
        design, 
        f'{name}_stgin', 
        options=Dict( 
            pos_x=pos_x, 
            pos_y=pos_y, 
            orientation='0', 
        ) 
    )

    anchors = OrderedDict() 
    anchors[0] = np.array([pos_x - 0.560, pos_y]) 
    anchors[1] = np.array([anchors[0][0] - 2*fillet, anchors[0][1] + 2*fillet])
    anchors[2] = np.array([anchors[1][0] - 0.5595, anchors[1][1]])
    anchors[3] = np.array([anchors[2][0], anchors[2][1] + 0.2+2*fillet])
    anchors[4] = np.array([anchors[3][0] + 0.630, anchors[3][1]])
    anchors[5] = np.array([anchors[4][0] - 0.5110, anchors[4][1]+2*fillet]) 
    anchors[6] = np.array([anchors[5][0], anchors[5][1]+2*fillet]) 

    stg_out = ShortToGround(
        design,
        f'{name}_stgout', 
        options=Dict(
            pos_x=pos_x-parse_value('670um', Dict()), 
            pos_y=anchors[6][1],
            orientation='0', 
        )
    )
    
    res_options = Dict(
        pin_inputs=Dict(
            start_pin=Dict(component=stg_in.name, pin='short'), 
            end_pin=Dict(component=stg_out.name, pin='short'),
        ), 
        anchors=anchors, 
        trace_width='20um', 
        trace_gap='10um', 
        fillet=fillet, 
    )
    resonator = RoutePathfinder(
        design, 
        f'{name}_resonator', 
        options=res_options, 
    )

    nodes = Dict() 
    nodes.closest_to_bus = np.array([anchors[3][0]- parse_value('20um', Dict()) , anchors[3][1]]) 
    return nodes 

def resonator_lower_left(design, pos_x, pos_y, name='resonator'): 
    fillet = 0.075
    
    stg_in = ShortToGround( 
        design, 
        f'{name}_stgin', 
        options=Dict( 
            pos_x=pos_x, 
            pos_y=pos_y, 
            orientation='0', 
        ) 
    )

    anchors = OrderedDict() 
    anchors[0] = np.array([pos_x - 0.558, pos_y]) 
    anchors[1] = np.array([anchors[0][0] - 2*fillet, anchors[0][1] - 2*fillet])
    anchors[2] = np.array([anchors[1][0] - 0.564, anchors[1][1]])
    anchors[3] = np.array([anchors[2][0], anchors[2][1] - (0.2+2*fillet)])
    anchors[4] = np.array([anchors[3][0] + 0.630, anchors[3][1]])
    anchors[5] = np.array([anchors[4][0] - 0.528, anchors[4][1] - 2*fillet]) 
    anchors[6] = np.array([anchors[5][0], anchors[5][1] - 2*fillet]) 

    stg_out = ShortToGround(
        design,
        f'{name}_stgout', 
        options=Dict(
            pos_x=pos_x-parse_value('670um', Dict()), 
            pos_y=anchors[6][1],
            orientation='0', 
        )
    )
    
    res_options = Dict(
        pin_inputs=Dict(
            start_pin=Dict(component=stg_in.name, pin='short'), 
            end_pin=Dict(component=stg_out.name, pin='short'),
        ), 
        anchors=anchors, 
        trace_width='20um', 
        trace_gap='10um', 
        fillet=fillet, 
    )
    resonator = RoutePathfinder(
        design, 
        f'{name}_resonator', 
        options=res_options, 
    )

    nodes = Dict() 
    nodes.closest_to_bus = np.array([anchors[3][0] - parse_value('20um', Dict()), anchors[3][1]])
    return nodes 

def resonator_singlet(design, pos_x, pos_y, name='resonator'): 
    fillet = 0.075
    
    stg_in = ShortToGround( 
        design, 
        f'{name}_stgin', 
        options=Dict( 
            pos_x=pos_x, 
            pos_y=pos_y, 
            orientation='0', 
        ) 
    )

    anchors = OrderedDict() 
    anchors[0] = np.array([pos_x - 0.565, pos_y]) 
    anchors[1] = np.array([anchors[0][0] - 2*fillet-0.01, anchors[0][1] - 2*fillet-0.01])
    anchors[2] = np.array([anchors[1][0] - 0.551, anchors[1][1]])
    anchors[3] = np.array([anchors[2][0], anchors[2][1] + 0.2+2*fillet+0.01])
    anchors[4] = np.array([anchors[3][0] + 0.630, anchors[3][1]])
    anchors[5] = np.array([anchors[4][0] - 0.555, anchors[4][1]+2*fillet+0.01]) 
    #anchors[6] = np.array([anchors[5][0] - 0.5110, anchors[5][1]]) 
    anchors[6] = np.array([anchors[5][0], anchors[5][1]+2*fillet+0.01]) 

    stg_out = ShortToGround(
        design,
        f'{name}_stgout', 
        options=Dict(
            pos_x=pos_x-parse_value('670um', Dict()), 
            pos_y=anchors[6][1],
            orientation='0', 
        )
    )
    
    res_options = Dict(
        pin_inputs=Dict(
            start_pin=Dict(component=stg_in.name, pin='short'), 
            end_pin=Dict(component=stg_out.name, pin='short'),
        ), 
        anchors=anchors, 
        trace_width='20um', 
        trace_gap='10um', 
        fillet=fillet, 
    )
    resonator = RoutePathfinder(
        design, 
        f'{name}_resonator', 
        options=res_options, 
    )

    nodes = Dict() 
    nodes.closest_to_bus = np.array([anchors[3][0]- parse_value('20um', Dict()) , anchors[3][1]]) 
    return nodes 

def resonator_transmon(design, pos_x, pos_y, name='resonator'): 
    fillet = 0.075
    
    stg_in = ShortToGround( 
        design, 
        f'{name}_stgin', 
        options=Dict( 
            pos_x=pos_x, 
            pos_y=pos_y, 
            orientation='180', 
        ) 
    )

    anchors = OrderedDict() 
    anchors[0] = np.array([pos_x + 0.625, pos_y]) 
    anchors[1] = np.array([anchors[0][0] + 2*fillet-0.01, anchors[0][1] - 2*fillet-0.01])
    anchors[2] = np.array([anchors[1][0] + 0.3586, anchors[1][1]])
    anchors[3] = np.array([anchors[2][0], anchors[2][1] + 0.2+2*fillet+0.01])
    anchors[4] = np.array([anchors[3][0] - 0.630, anchors[3][1]])
    anchors[5] = np.array([anchors[4][0] + 0.587, anchors[4][1]+2*fillet+0.01]) 
    anchors[6] = np.array([anchors[5][0], anchors[5][1]+2*fillet+0.01]) 

    stg_out = ShortToGround(
        design,
        f'{name}_stgout', 
        options=Dict(
            pos_x=pos_x+parse_value('670um', Dict()), 
            pos_y=anchors[6][1],
            orientation='180', 
        )
    )
    
    res_options = Dict(
        pin_inputs=Dict(
            start_pin=Dict(component=stg_in.name, pin='short'), 
            end_pin=Dict(component=stg_out.name, pin='short'),
        ), 
        anchors=anchors, 
        trace_width='20um', 
        trace_gap='10um', 
        fillet=fillet, 
    )
    resonator = RoutePathfinder(
        design, 
        f'{name}_resonator', 
        options=res_options, 
    )

    nodes = Dict() 
    nodes.closest_to_bus = np.array([anchors[3][0]+ parse_value('20um', Dict()) , anchors[3][1]]) 
    nodes.end = np.array([pos_x+parse_value('670um', Dict()), anchors[6][1]])
    return nodes 

def resonator_upper_doublet(design, pos_x, pos_y, name='resonator'): 
    fillet = 0.08
    
    stg_in = ShortToGround( 
        design, 
        f'{name}_stgin', 
        options=Dict( 
            pos_x=pos_x, 
            pos_y=pos_y, 
            orientation='180', 
        ) 
    )

    anchors = OrderedDict() 
    anchors[0] = np.array([pos_x + 0.635, pos_y]) 
    anchors[1] = np.array([anchors[0][0] + fillet, anchors[0][1] + fillet]) 
    anchors[2] = np.array([anchors[1][0], anchors[1][1] + 0.13])
    anchors[3] = np.array([anchors[2][0] + fillet, anchors[2][1] + fillet]) 
    anchors[4] = np.array([anchors[3][0] + 0.439, anchors[3][1]])
    anchors[5] = np.array([anchors[4][0], anchors[4][1] + 0.2+2*fillet+0.01])
    anchors[6] = np.array([anchors[5][0] - 0.630, anchors[5][1]])
    anchors[7] = np.array([anchors[6][0] + 0.587, anchors[6][1]+2*fillet+0.01]) 
    anchors[8] = np.array([anchors[7][0], anchors[7][1]+2*fillet+0.01]) 

    stg_out = ShortToGround(
        design,
        f'{name}_stgout', 
        options=Dict(
            pos_x=pos_x+parse_value('670um', Dict()), 
            pos_y=anchors[8][1],
            orientation='180', 
        )
    )
    
    res_options = Dict(
        pin_inputs=Dict(
            start_pin=Dict(component=stg_in.name, pin='short'), 
            end_pin=Dict(component=stg_out.name, pin='short'),
        ), 
        anchors=anchors, 
        trace_width='20um', 
        trace_gap='10um', 
        fillet=fillet, 
    )
    resonator = RoutePathfinder(
        design, 
        f'{name}_resonator', 
        options=res_options, 
    )

    nodes = Dict() 
    nodes.closest_to_bus = np.array([anchors[3][0]+ parse_value('20um', Dict()) , anchors[3][1]]) 
    nodes.end = np.array([pos_x+parse_value('670um', Dict()), anchors[6][1]])
    return nodes 

def resonator_lower_doublet(design, pos_x, pos_y, name='resonator'): 
    fillet = 0.08
    
    stg_in = ShortToGround( 
        design, 
        f'{name}_stgin', 
        options=Dict( 
            pos_x=pos_x, 
            pos_y=pos_y, 
            orientation='180', 
        ) 
    )

    anchors = OrderedDict() 
    anchors[0] = np.array([pos_x + 0.638, pos_y]) 
    anchors[1] = np.array([anchors[0][0] + fillet, anchors[0][1]])
    anchors[2] = np.array([anchors[1][0], anchors[1][1] - fillet])
    anchors[3] = np.array([anchors[2][0], anchors[2][1] - 0.13])
    anchors[4] = np.array([anchors[3][0] + fillet, anchors[3][1] - fillet])
    anchors[5] = np.array([anchors[4][0] + 0.439, anchors[4][1]])
    anchors[6] = np.array([anchors[5][0], anchors[5][1] - 0.2-(2*fillet+0.01)])
    anchors[7] = np.array([anchors[6][0] - 0.630, anchors[6][1]])
    anchors[8] = np.array([anchors[7][0] + 0.587, anchors[7][1]-(2*fillet+0.01)]) 
    anchors[9] = np.array([anchors[8][0], anchors[8][1]-(2*fillet+0.01)]) 

    stg_out = ShortToGround(
        design,
        f'{name}_stgout', 
        options=Dict(
            pos_x=pos_x+parse_value('670um', Dict()), 
            pos_y=anchors[9][1],
            orientation='180', 
        )
    )
    
    res_options = Dict(
        pin_inputs=Dict(
            start_pin=Dict(component=stg_in.name, pin='short'), 
            end_pin=Dict(component=stg_out.name, pin='short'),
        ), 
        anchors=anchors, 
        trace_width='20um', 
        trace_gap='10um', 
        fillet=fillet, 
    )
    resonator = RoutePathfinder(
        design, 
        f'{name}_resonator', 
        options=res_options, 
    )

    nodes = Dict() 
    nodes.closest_to_bus = np.array([anchors[4][0]+ parse_value('20um', Dict()) , anchors[4][1]]) 
    nodes.end = np.array([pos_x+parse_value('670um', Dict()), anchors[6][1]])
    return nodes 


