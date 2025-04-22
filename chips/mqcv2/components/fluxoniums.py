# Requires >=Python 3.9.0 

from qiskit_metal import Dict
from qiskit_metal.qlibrary.QNLMetal.fluxonium import Fluxonium 
from qiskit_metal.qlibrary.QNLMetal.claw import Claw 
from qiskit_metal.qlibrary.QNLMetal.fluxline import FluxLine
from qiskit_metal.qlibrary.terminations.short_to_ground import ShortToGround 
from qiskit_metal.qlibrary.tlines.straight_path import RouteStraight 
from qiskit_metal.qlibrary.tlines.framed_path import RouteFramed
import numpy as np 

def coupled_fluxonium(design, gap='25um', options=None, name='coupled_fluxonium'):
    """
    Renders a capacitively-coupled fluxonium to the design.

    Args:
        * design (qiskit_metal.designs.DesignPlanar): 
            Chip design.
        * gap (float or str): 
            Vertical spacing between fluxoniums.
        * opts (qiskit_metal.Dict): 
            Options for the Fluxonium object.

    Returns: 
        nodes (Dict): Significant locations of geometry. 
    """

    gap = design.parse_value(gap)

    template_options = Fluxonium.get_template_options(design) 
    options = template_options | options if options else template_options 
    options = design.parse_value(options) 

    upper_fluxonium = Fluxonium(design, f'{name}_upper', options=options) 
    upper_fluxonium.options.pos_y = options.pos_y + gap/2 + options.height/2
    lower_fluxonium = Fluxonium(design, f'{name}_lower', options=options)
    lower_fluxonium.options.pos_y = options.pos_y - gap/2 - options.height/2
    upper_fluxonium.make() # properly positions nodes 
    lower_fluxonium.make() # properly positions nodes 

    nodes = Dict() 
    nodes.top       = upper_fluxonium.node('top') 
    nodes.bottom    = lower_fluxonium.node('bottom') 
    nodes.top_left  = upper_fluxonium.node('left') 
    nodes.top_right = upper_fluxonium.node('right') 
    nodes.bottom_left  = lower_fluxonium.node('left') 
    nodes.bottom_right = lower_fluxonium.node('right')
    nodes.upper_bottom = upper_fluxonium.node('bottom') 
    nodes.lower_top    = lower_fluxonium.node('top')
    nodes.top_left_pocket_bottom = upper_fluxonium.node('l_pocket_bottom') 
    nodes.top_right_pocket_bottom= upper_fluxonium.node('r_pocket_bottom') 
    nodes.bottom_left_pocket_top = lower_fluxonium.node('l_pocket_top') 
    nodes.bottom_right_pocket_top= lower_fluxonium.node('r_pocket_top') 
    return nodes

def add_capacitive_claws(design, nodes, pair='right', options=None, name='capaclaws'):
    """
    Adds capacitive claws between fluxoniums.

    Args: 
        * design (qiskit_metal.designs.DesignPlanar): 
            Chip design. 
        * nodes (Dict): 
            Returned nodes from `coupled_fluxonium()`.  
        * pair ('left' or 'right'): 
            Either place capacitive coupler between left or right pockets.
    """

    claw_opts = Dict({
        'finger_length': '60um',
        'base_length': '148um',
        'base_width': '20um',
        'finger_width': '20um',
        'cpw_length': '76um',
        'cpw_gap': '15um',
        'cpw_width': '15um'
    }) 
    claw_opts = claw_opts if not options else claw_opts | options 

    upper_claw = Claw(design, f'{name}_upper', options=claw_opts)
    upper_claw.options.orientation = '0'
    lower_claw = Claw(design, f'{name}_lower', options=claw_opts)
    lower_claw.options.orientation = '180'

    if pair == 'left': 
        upper_claw.options.pos_x = nodes.top_left_pocket_bottom[0] 
        lower_claw.options.pos_x = nodes.bottom_left_pocket_top[0] 
        upper_claw.options.pos_y = nodes.top_left_pocket_bottom[1] 
        lower_claw.options.pos_y = nodes.bottom_left_pocket_top[1] 

        # For straight path connector 
        stg_in_opts = Dict( 
            pos_x = nodes.top_left_pocket_bottom[0], 
            pos_y = nodes.upper_bottom[1], 
            orientation='90'
        )
        stg_out_opts= Dict(
            pos_x = nodes.top_left_pocket_bottom[0], 
            pos_y = nodes.lower_top[1], 
            orientation='270'
        )
    else: 
        upper_claw.options.pos_x = nodes.top_right_pocket_bottom[0] 
        lower_claw.options.pos_x = nodes.bottom_right_pocket_top[0] 
        upper_claw.options.pos_y = nodes.top_right_pocket_bottom[1] 
        lower_claw.options.pos_y = nodes.bottom_right_pocket_top[1]

        # For straight path connector
        stg_in_opts = Dict( 
            pos_x = nodes.top_right_pocket_bottom[0], 
            pos_y = nodes.upper_bottom[1], 
            orientation='90'
        ) 
        stg_out_opts = Dict(
            pos_x = nodes.top_right_pocket_bottom[0], 
            pos_y = nodes.lower_top[1], 
            orientation='270'
        )

    y_offset = (
            design.parse_value('4um') + 
            design.parse_value(claw_opts.base_width)
    )
    upper_claw.options.pos_y -= y_offset 
    lower_claw.options.pos_y += y_offset

    # Building straight path in between claws 
    stg_in = ShortToGround(design, options=stg_in_opts) 
    stg_out= ShortToGround(design, options=stg_out_opts) 

    cpw_opts = Dict( 
        pin_inputs=Dict(
            start_pin=Dict(
                component=stg_in.name, 
                pin='short' 
            ), 
            end_pin=Dict(
                component=stg_out.name, 
                pin='short' 
            ) 
        ), 
        trace_width = claw_opts.cpw_gap, 
        trace_gap   = claw_opts.cpw_width, 
    )

    RouteStraight(design, options=cpw_opts)
    return nodes 

def add_resonator_claws(design, nodes, side='left', options=None, name='resclaws'): 
    """ 
    Renders resonator claws on edge of fluxoniums. 
    *Only for coupled fluxoniums (two fluxoniums).*

    Args: 
        * design (qiskit_metal.designs.DesignPlanar): 
            Chip design. 
        * nodes (Dict): 
            Returned nodes from `coupled_fluxonium()`. 
        * side ('left' or 'right'): 
            Places claws on left or right edge of fluxonium qubits. 
        * options (Dict) 
            Some extra options for the claws. See Claw.get_template_options(design).
            Defaults to claw_opts below. 
    """

    claw_opts = {
        'base_length': '250um',
        'base_width': '40um',
        'finger_length': '0um',
        'cpw_length': '15um',
        'cpw_gap': '20um',
        'cpw_width': '10um'
    } 
    claw_opts = claw_opts if not options else claw_opts | options

    upper_claw = Claw(design, f'{name}_upper', options=claw_opts) 
    lower_claw = Claw(design, f'{name}_lower', options=claw_opts)

    if side == 'left': 
        upper_x, upper_y = nodes.top_left 
        lower_x, lower_y = nodes.bottom_left  
        upper_claw.options.orientation = '270' 
        lower_claw.options.orientation = '270' 
        x_offset = +design.parse_value(claw_opts['cpw_length'])
    else: 
        upper_x, upper_y = nodes.top_right 
        lower_x, lower_y = nodes.bottom_right
        upper_claw.options.orientation = '90' 
        lower_claw.options.orientation = '90'
        x_offset = -design.parse_value(claw_opts['cpw_length'])

    upper_claw.options.pos_x = upper_x + x_offset 
    upper_claw.options.pos_y = upper_y 
    lower_claw.options.pos_x = lower_x + x_offset
    lower_claw.options.pos_y = lower_y  

    nodes.upper_claw = np.array([upper_x, upper_y])
    nodes.lower_claw = np.array([lower_x, lower_y])
    return nodes 

def add_fluxlines(design, nodes, name='fluxlines'):
    """ 
    Renders fluxline tapers above the top and below the bottom fluxoniums. 

    Args: 
        * design (qiskit_metal.designs.DesignPlanar):
            Chip design. 
        * nodes (Dict): 
            Returned nodes from `coupled_fluxonium`. 
    """

    top_node    = nodes.top 
    bottom_node = nodes.bottom

    names                = ['upper', 'lower']
    central_nodes        = [top_node, bottom_node] 
    central_orientations = ['90', '270'] 
    fluxline_orientations= ['180', '0'] 
    taper_length = '212um' 
    for idx in range(len(central_nodes)): 
        c_x, c_y = central_nodes[idx]    

        stg_ops = {
            'central': {
                'pos_x': c_x, 
                'pos_y': c_y, 
                'orientation': central_orientations[idx]
            },
            'left': {
                'pos_x': c_x - design.parse_value('70um'), 
                'pos_y': c_y, 
                'orientation': central_orientations[idx]
            },
            'right': {
                'pos_x': c_x + design.parse_value('70um'), 
                'pos_y': c_y, 
                'orientation': central_orientations[idx]
            }
        }

        stg_cl = ShortToGround(design, f'{names[idx]}_{name}_cl', options=stg_ops['central'])
        stg_cr = ShortToGround(design, f'{names[idx]}_{name}_cr', options=stg_ops['central'])
        stg_l  = ShortToGround(design, f'{names[idx]}_{name}_l',  options=stg_ops['left'])
        stg_r  = ShortToGround(design, f'{names[idx]}_{name}_r',  options=stg_ops['right'])

        route_opts = Dict(
            pin_inputs=Dict( 
                start_pin=Dict(
                    component=None, 
                    pin='short', 
                ), 
                end_pin=Dict( 
                    component=None, 
                    pin='short', 
                ), 
            ), 
            trace_width = '2um', 
            trace_gap   = '1um', 
            total_length= '50um', 
            lead=Dict(
                start_straight='18um', 
                end_straight='18um', 
            ), 
            fillet='2.5um'
        )

        route_opts.pin_inputs.start_pin.component = stg_cl.name 
        route_opts.pin_inputs.end_pin.component   = stg_l.name 
        RouteFramed(design, f'{names[idx]}_{name}_routeleft', options=route_opts) 

        route_opts.pin_inputs.start_pin.component = stg_cr.name
        route_opts.pin_inputs.end_pin.component = stg_r.name
        RouteFramed(design, f'{names[idx]}_{name}_routeright', options=route_opts)

        # Placing fluxline 
        fl_opts = Dict(
            starting_width  = '5um', 
            starting_gap    = '8um', 
            end_width       = '1um', 
            end_gap         = '2um', 
            taper_length    = taper_length, 
            orientation     = fluxline_orientations[idx]
        )
        fluxline = FluxLine(design, f'{names[idx]}_{name}', options=fl_opts) 
        fluxline.position('thin_gap_center', (c_x, c_y))

    nodes.upper_flux_line_end = nodes.top + [0, design.parse_value(taper_length)] 
    nodes.lower_flux_line_end = nodes.bottom - [0, design.parse_value(taper_length)]
    return nodes

def single_fluxonium(design, options=None, name='single_fluxonium'): 
    """
    Renders a single fluxonium to the design.

    Args:
        * design (qiskit_metal.designs.DesignPlanar): 
            Chip design.
        * opts (qiskit_metal.Dict): 
            Options for the Fluxonium object.

    Returns: 
        nodes (Dict): Significant locations of geometry. 
    """

    flux_opts = Fluxonium.get_template_options(design) 
    flux_opts = flux_opts if not options else flux_opts | options 

    fluxonium = Fluxonium(design, f'{name}', options=flux_opts)

    nodes = Dict() 
    nodes.top       = fluxonium.node('top') 
    nodes.bottom    = fluxonium.node('bottom') 
    nodes.right     = fluxonium.node('right') 
    nodes.left      = fluxonium.node('left') 
    return nodes

def add_resonator_claw(design, nodes, side='left', options=None, name='single_claw'): 
    """ 
    Renders resonator claws on edge of fluxonium. 
    *Only for a single fluxonium.*

    Args: 
        * design (qiskit_metal.designs.DesignPlanar): 
            Chip design. 
        * nodes (Dict): 
            Returned nodes from `coupled_fluxonium()`. 
        * side ('left' or 'right'): 
            Places claws on left or right edge of the fluxonium. 
        * options (Dict) 
            Some extra options for the claws. See Claw.get_template_options(design).
            Defaults to claw_opts below. 
    """

    claw_opts = {
        'base_length': '250um',
        'base_width': '40um',
        'finger_length': '0um',
        'cpw_length': '15um',
        'cpw_gap': '20um',
        'cpw_width': '10um'
    }
    claw_opts = claw_opts if not options else claw_opts | options 
    claw = Claw(design, f'{name}', options=claw_opts) 

    nodes_ = Dict() 
    if side == 'left': 
        x, y = nodes.left 
        x += design.parse_value(claw_opts['cpw_length']) 
        orientation = '270'
        nodes_.claw = nodes.left 
    else: 
        x, y = nodes.right 
        x -= design.parse_value(claw_opts['cpw_length'])
        orientation = '90'
        nodes_.claw = nodes.right 

    claw.options.pos_x = x 
    claw.options.pos_y = y 
    claw.options.orientation = orientation 
    nodes_.right = nodes.right 
    nodes_.left  = nodes.left 
    nodes = nodes | nodes_ 
    return nodes


























            



        






