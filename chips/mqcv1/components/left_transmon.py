from qiskit_metal.qlibrary.QNLMetal.claw import Claw
from qiskit_metal.qlibrary.QNLMetal.transmon import Transmon
from qiskit_metal.toolbox_metal.parsing import parse_value
from qiskit_metal import Dict 
import numpy as np 

from components.coupling_resonator_ import resonator 

def left_transmon_resonator(design, pos_x=0.0, pos_y=0.0, name='left_transmon'):
    # Initialize QNLDraw Transmon Design 
    tsmn = Transmon(design)
    tsmn.options.pos_x = pos_x
    tsmn.options.pos_y = pos_y
    tsmn.options.name = name
    tsmn.make()

    # Claw connects to the side of the qubit
    claw_qubit  = Claw(design)

    qubit_opts = {
        'orientation': '90',
        'base_length': '650.5um',
        'base_width': '40um',
        'finger_length': '0um',
        'cpw_length': '15um',
        'cpw_gap': '20um',
        'cpw_width': '10um'
    }
    
    for opt, val in qubit_opts.items():
        setattr(claw_qubit.options, opt, val)
    right_x, right_y = tsmn.node('right')

    claw_x = right_x + parse_value('65.4um', Dict())
    claw_qubit.options.pos_x = claw_x
    claw_qubit.options.pos_y = right_y

    nodes = Dict()
    nodes.qubit_claw = np.array([claw_x + 0.015, tsmn.node('right')[1]])

    resonator_x = nodes.qubit_claw[0] 
    resonator_y = nodes.qubit_claw[1]
    resonator_nodes = resonator(design, resonator_x, resonator_y, key='transmon', name='transmon_resonator')  

    nodes.resonator_end = resonator_nodes.end
    return nodes