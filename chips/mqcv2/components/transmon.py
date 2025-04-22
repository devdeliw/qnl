from qiskit_metal.qlibrary.QNLMetal.transmon import Transmon 
from qiskit_metal.qlibrary.QNLMetal.claw import Claw 
from qiskit_metal import Dict 
import numpy as np 

def transmon(design, options=None, name='transmon'): 
    """
    Renders a single transmon to the design.

    Args:
        * design (qiskit_metal.designs.DesignPlanar): 
            Chip design.
        * opts (qiskit_metal.Dict): 
            Options for the Transmon object.

    Returns: 
        nodes (Dict): Significant locations of geometry. 
    """

    template_options = Transmon.get_template_options(design) 
    options = template_options | options if options else template_options 
    options = design.parse_value(options) 

    tsmn = Transmon(design, f'{name}', options=options) 
    tsmn.make() # properly positions nodes 

    nodes = tsmn.nodes 
    return nodes 

def add_claw(design, nodes, side='right', options=None, name='tsmn_claw'): 
    """ 
    Renders resonator claws on edge of transmon. 

    Args: 
        * design (qiskit_metal.designs.DesignPlanar): 
            Chip design. 
        * nodes (Dict): 
            Returned nodes from `transmon()`. 
        * side ('left' or 'right'): 
            Places claws on left or right edge of the transmon. 
        * options (Dict) 
            Some extra options for the claws. See Claw.get_template_options(design).
            Defaults to claw_opts below. 
    """

    claw_opts = {
        'orientation': '90',
        'base_length': '650.5um',
        'base_width': '40um',
        'finger_length': '0um',
        'cpw_length': '15um',
        'cpw_gap': '20um',
        'cpw_width': '10um'
    } 

    claw_opts = claw_opts if not options else claw_opts | options 
    claw = Claw(design, f'{name}', options=claw_opts)

    nodes_ = Dict() 
    if side == 'right': 
        x, y = nodes.right  
        x += design.parse_value('65.4um') 
        orientation = '90'
        nodes_.claw = np.array([x + 0.015, nodes.right[1]])
    else: 
        x, y = nodes.left 
        x -= design.parse_value('65.4um') 
        orientation = '270' 
        nodes_.claw = np.array([x - 0.015, nodes.left[1]])
    claw.options.pos_x = x 
    claw.options.pos_y = y 
    claw.options.orientation = orientation

    nodes = nodes | nodes_ 
    return nodes


