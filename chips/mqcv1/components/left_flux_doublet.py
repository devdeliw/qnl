from qiskit_metal.qlibrary.QNLMetal.claw import Claw
from qiskit_metal.qlibrary.QNLMetal.fluxline import FluxLine
from qiskit_metal.qlibrary.QNLMetal.fluxonium import Fluxonium
from qiskit_metal.qlibrary.QNLMetal.bandage import Bandage
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
    claw_qubit  = Claw(design)

    qubit_opts = {
        'orientation': '90',
        'base_length': '250um',
        'base_width': '40um',
        'finger_length': '0um',
        'cpw_length': '15um',
        'cpw_gap': '20um',
        'cpw_width': '10um'
    }
    for opt, val in qubit_opts.items():
        setattr(claw_qubit.options, opt, val)
    right_x, right_y = flux.node('right')
    claw_qubit.options.pos_x = right_x - parse_value(claw_qubit.options.cpw_length, Dict())
    claw_qubit.options.pos_y = right_y

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

    otg_cl = ShortToGround(design, f'{name}_cl', options=otg_ops['central'])
    otg_cr = ShortToGround(design, f'{name}_cr', options=otg_ops['central'])
    otg_l  = ShortToGround(design, f'{name}_l', options=otg_ops['left'])
    otg_r  = ShortToGround(design, f'{name}_r', options=otg_ops['right'])

    route_params = Dict(pin_inputs=Dict(
        start_pin=Dict(component=None, pin='short'),
        end_pin=Dict(component=None, pin='short'), 
    ))
    route_params.pin_inputs.start_pin.component = otg_cl.name
    route_params.pin_inputs.end_pin.component = otg_l.name
    route_left = RouteFramed(design, f'{name}_flux_line_l', route_params)

    route_params.pin_inputs.start_pin.component = otg_cr.name
    route_params.pin_inputs.end_pin.component = otg_r.name
    route_right = RouteFramed(design, f'{name}_flux_line_r', route_params)

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

    # Adding fluxline 
    fluxline = FluxLine(design, name=f'{name}_flux_line_main', options=options) 
    fluxline.position('thin_gap_center', (c_x, c_y))

    for route in (route_left, route_right):
        route.options.trace_width = '2um'
        route.options.trace_gap   = '1um' 
        route.options.total_length = '50um'
        route.options.lead.start_straight = '18um'
        route.options.lead.end_straight = '18um'
        route.options.fillet = '2.5um'


    options = Dict(
        starting_width='10um', 
        starting_gap='15um', 
        end_width='10um', 
        end_gap='5um', 
        taper_length='60um', 
        start_length='40um', 
        orientation=orientation,
    )
    fl = FluxLine(design, name=f'{name}_fl_connector', options=options) 
    if not flip: 
        fl.position('origin', tuple(flux.node('l_pocket_bottom')))
    else: 
        fl.position('origin', tuple(flux.node('l_pocket_top')))
    

    nodes = Dict() 
    nodes.upper_flux_line_end = flux.node('top') + [0, parse_value(taper_length, Dict())]
    nodes.lower_flux_line_end = flux.node('bottom') - [0, parse_value(taper_length, Dict())]
    nodes.qubit_claw = flux.node('left')
    nodes.flux_line  = flux.node('top') 
    nodes.top        = flux.node('top')
    nodes.bottom     = flux.node('bottom') 
    nodes.left       = flux.node('left') 
    nodes.right      = flux.node('right')
    nodes.left_qubit_claw = flux.node('right')
    return nodes 

def central_pad(design, pos_x, pos_y):
    pad = Bandage(design, options=Dict(
        pos_x=pos_x, pos_y=pos_y, width='300um', height='225um'))

    central_node = pad.node('left') 
    central_orientation = '180' 
    c_x, c_y = central_node 

    otg_ops = {
        'central': {'pos_x': c_x, 'pos_y': c_y, 'orientation': central_orientation},
        'top': {'pos_x': c_x, 'pos_y': c_y + parse_value('70um', Dict()), 'orientation': central_orientation},
        'bot': {'pos_x': c_x, 'pos_y': c_y - parse_value('70um', Dict()), 'orientation': central_orientation}
    }

    otg_cl = ShortToGround(design, f'left_cl', options=otg_ops['central'])
    otg_cr = ShortToGround(design, f'left_cr', options=otg_ops['central'])
    otg_l  = ShortToGround(design, f'left_l', options=otg_ops['top'])
    otg_r  = ShortToGround(design, f'left_r', options=otg_ops['bot'])

    route_params = Dict(pin_inputs=Dict(
        start_pin=Dict(component=None, pin='short'),
        end_pin=Dict(component=None, pin='short'), 
    ))
    route_params.pin_inputs.start_pin.component = otg_cl.name
    route_params.pin_inputs.end_pin.component = otg_l.name
    route_left = RouteFramed(design, f'left_flux_line_l', route_params)

    route_params.pin_inputs.start_pin.component = otg_cr.name
    route_params.pin_inputs.end_pin.component = otg_r.name
    route_right = RouteFramed(design, f'left_flux_line_r', route_params)

    for route in (route_left, route_right):
        route.options.trace_width = '2um'
        route.options.trace_gap   = '1um' 
        route.options.total_length = '50um'
        route.options.lead.start_straight = '18um'
        route.options.lead.end_straight = '18um'
        route.options.fillet = '2.5um'

    taper_length= '212um' 
    options = Dict(
        starting_width= '5um', 
        starting_gap  = '8um', 
        end_width= '1um', 
        end_gap  = '2um', 
        taper_length= taper_length,
        orientation = '270', 
    ) 

    # Adding fluxline 
    fluxline = FluxLine(design, name=f'left_flux_line_main', options=options) 
    fluxline.position('thin_gap_center', (c_x, c_y))

    nodes = Dict() 
    nodes.flux_line_end = pad.node('left') - [parse_value(taper_length, Dict()), 0]
    return nodes

def left_flux_doublet(design, pos_x, pos_y): 
    upper_nodes = fluxonium(design=design, pos_x=pos_x, pos_y=pos_y+0.2625, flip=False, name='upper') 
    lower_nodes = fluxonium(design=design, pos_x=pos_x, pos_y=pos_y-0.2625, flip=True, name='lower') 
    center_nodes= central_pad(design, upper_nodes.left[0]+0.15, pos_y)
    
    nodes = Dict() 
    nodes.upper_left = upper_nodes.left 
    nodes.lower_left = lower_nodes.left
    nodes.upper_flux_line_end = upper_nodes.upper_flux_line_end 
    nodes.lower_flux_line_end = lower_nodes.lower_flux_line_end 
    nodes.central_flux_line_end = center_nodes.flux_line_end 
    nodes.upper_flux_line = upper_nodes.flux_line 
    nodes.upper_qubit_claw= upper_nodes.left_qubit_claw 
    nodes.lower_flux_line = lower_nodes.flux_line 
    nodes.lower_qubit_claw= lower_nodes.left_qubit_claw
    return nodes 

