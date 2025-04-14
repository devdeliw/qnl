from qiskit_metal.qlibrary.QNLMetal.claw import Claw
from qiskit_metal.qlibrary.QNLMetal.fluxline import FluxLine
from qiskit_metal.qlibrary.QNLMetal.fluxonium import Fluxonium
from qiskit_metal.qlibrary.terminations.short_to_ground import ShortToGround
from qiskit_metal.qlibrary.tlines.framed_path import RouteFramed
from qiskit_metal.qlibrary.tlines.straight_path import RouteStraight
from qiskit_metal.toolbox_metal.parsing import parse_value
from qiskit_metal import Dict 
import numpy as np 

def fluxonium(design, pos_x=0.0, pos_y=0.0, flip=False, name='lower'):
    # Initialize QNLDraw Fluxonium Design 
    flux = Fluxonium(design)
    flux.options.pos_x = pos_x
    flux.options.pos_y = pos_y
    flux.make()
    
    # One connects to a square pocket 
    # One connects to the side of the qubit
    claw_pocket = Claw(design)
    claw_qubit  = Claw(design)

    pocket_opts = {
        'finger_length': '60um',
        'base_length': '148um',
        'base_width': '20um',
        'finger_width': '20um',
        'cpw_length': '76um',
        'cpw_gap': '15um',
        'cpw_width': '15um'
    }
    for opt, val in pocket_opts.items():
        setattr(claw_pocket.options, opt, val)
    if flip:
        claw_pocket.options.orientation = '180'
        x, y = flux.node('r_pocket_top')
        claw_pocket.options.pos_x = x
        claw_pocket.options.pos_y = y + 0.004 + parse_value(claw_pocket.options.base_width, Dict())
    else:
        x, y = flux.node('r_pocket_bottom')
        claw_pocket.options.pos_x = x
        claw_pocket.options.pos_y = y - 0.004 - parse_value(claw_pocket.options.base_width, Dict())

    qubit_opts = {
        'orientation': '270',
        'base_length': '250um',
        'base_width': '40um',
        'finger_length': '0um',
        'cpw_length': '15um',
        'cpw_gap': '20um',
        'cpw_width': '10um'
    }
    for opt, val in qubit_opts.items():
        setattr(claw_qubit.options, opt, val)
    left_x, left_y = flux.node('left')
    claw_qubit.options.pos_x = left_x + parse_value(claw_qubit.options.cpw_length, Dict())
    claw_qubit.options.pos_y = left_y

    top_node = flux.node('top')
    bottom_node = flux.node('bottom')
    central_node = top_node if not flip else bottom_node
    central_orientation = '90' if not flip else '270'
    c_x, c_y = central_node

    otg_ops = {
        'central': {
            'pos_x': c_x, 
            'pos_y': c_y, 
            'orientation': central_orientation
        },
        'left': {
            'pos_x': c_x - parse_value('70um', Dict()), 
            'pos_y': c_y, 
            'orientation': central_orientation
        },
        'right': {
            'pos_x': c_x + parse_value('70um', Dict()), 
            'pos_y': c_y, 
            'orientation': central_orientation
        }
    }

    otg_cl = ShortToGround(design, f'{name}_doublet_cl', options=otg_ops['central'])
    otg_cr = ShortToGround(design, f'{name}_doublet_cr', options=otg_ops['central'])
    otg_l  = ShortToGround(design, f'{name}_doublet_l', options=otg_ops['left'])
    otg_r  = ShortToGround(design, f'{name}_doublet_r', options=otg_ops['right'])

    route_params = Dict(pin_inputs=Dict(
        start_pin=Dict(component=None, pin='short'),
        end_pin=Dict(component=None, pin='short'), 
    ))
    route_params.pin_inputs.start_pin.component = otg_cl.name
    route_params.pin_inputs.end_pin.component = otg_l.name
    route_left = RouteFramed(design, f'{name}_flux_line_doublet_l', route_params)

    route_params.pin_inputs.start_pin.component = otg_cr.name
    route_params.pin_inputs.end_pin.component = otg_r.name
    route_right = RouteFramed(design, f'{name}_flux_line_doublet_r', route_params)

    # Placing Fluxline 
    orientation = '180' if not flip else '0' 
    taper_length= '212um' 
    
    options = Dict(
        starting_width= '5um', 
        starting_gap  = '8um', 
        end_width= '1um', 
        end_gap  = '2um', 
        taper_length= taper_length,
        orientation = orientation, 
    ) 
 
    for route in (route_left, route_right):
        route.options.trace_width = '2um'
        route.options.trace_gap   = '1um' 
        route.options.total_length = '50um'
        route.options.lead.start_straight = '18um'
        route.options.lead.end_straight = '18um'
        route.options.fillet = '2.5um'

    # Adding fluxline 
    fluxline = FluxLine(design, name=f'{name}_flux_line_doublet_main', options=options) 
    fluxline.position('thin_gap_center', (c_x, c_y))

    if not flip: 
        pos_x = flux.node('r_pocket_bottom')[0]
        pos_y = flux.node('bottom')[1] 
        orientation = '90' 
        otg_name = 'lower_connector_otg'
    else: 
        pos_x = flux.node('r_pocket_top')[0] 
        pos_y = flux.node('top')[1] 
        orientation = '270' 
        otg_name = 'upper_connector_otg'
    
    otg = ShortToGround(design, otg_name, options=Dict(
        pos_x=pos_x, pos_y=pos_y, orientation=orientation))

    nodes = Dict() 
    nodes.right = flux.node('right') 
    nodes.upper_flux_line_end = flux.node('top') + [0, parse_value(taper_length, Dict())]
    nodes.lower_flux_line_end = flux.node('bottom') - [0, parse_value(taper_length, Dict())]
    nodes.qubit_claw = flux.node('left')
    nodes.flux_line  = flux.node('top') 
    return nodes 

def right_flux_doublet(design, pos_x, pos_y): 
    upper_nodes = fluxonium(design=design, pos_x=pos_x, pos_y=pos_y+0.1625, flip=False, name='upper') 
    lower_nodes = fluxonium(design=design, pos_x=pos_x, pos_y=pos_y-0.1625, flip=True, name='lower') 

    connector_ops = Dict(pin_inputs=Dict(
        start_pin=Dict(component='lower_connector_otg', pin='short'),
        end_pin=Dict(component='upper_connector_otg', pin='short'), 
    )) 
    connector = RouteStraight(design, 'right_fluxonium_connector', options=connector_ops)
    connector.options.trace_width = '15um' 
    connector.options.trace_gap   = '15um'

    nodes = Dict() 
    nodes.upper_right = upper_nodes.right 
    nodes.lower_right = lower_nodes.right
    nodes.upper_flux_line_end = upper_nodes.upper_flux_line_end 
    nodes.lower_flux_line_end = lower_nodes.lower_flux_line_end 
    nodes.upper_flux_line = upper_nodes.flux_line 
    nodes.upper_qubit_claw= upper_nodes.qubit_claw 
    nodes.lower_flux_line = lower_nodes.flux_line 
    nodes.lower_qubit_claw= lower_nodes.qubit_claw
    return nodes 

