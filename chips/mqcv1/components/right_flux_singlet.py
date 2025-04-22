from qiskit_metal.qlibrary.QNLMetal.claw import Claw
from qiskit_metal.qlibrary.QNLMetal.fluxonium import Fluxonium
from qiskit_metal.toolbox_metal.parsing import parse_value
from qiskit_metal import Dict 

def right_flux_singlet(design, pos_x=0.0, pos_y=0.0, name='right_singlet'):
    # Initialize QNLDraw Fluxonium Design 
    flux = Fluxonium(design)
    flux.options.pos_x = pos_x
    flux.options.pos_y = pos_y
    flux.options.name = name
    flux.make()

    # Claw connects to the side of the qubit
    claw_qubit  = Claw(design)

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

    nodes = Dict()
    nodes.right = flux.node('right')
    nodes.qubit_claw = flux.node('left') 
    return nodes