from qiskit_metal.qlibrary.tlines.pathfinder import RoutePathfinder
from qiskit_metal.qlibrary.tlines.straight_path import RouteStraight
from qiskit_metal.qlibrary.tlines.mixed_path import RouteMixed
from qiskit_metal.qlibrary.terminations.short_to_ground import ShortToGround
from qiskit_metal import Dict

def resonator(
        design, 
        start_x, start_y, end_x_offset,
        anchors, fillet=0.08, name='resonator', length=4.463,
):
    """ 
    Renders a resonator to the chip based on given parameters. 

    Args: 
        * design (qiskit_metal.designs.DesignPlanar): 
            Chip design. 
        * start_x/y (float or string); 
            x, y position for start of resonator. 
            (part connected to the qubit). 
        * end_x/y (float or string): 
            x, y position for end of resonator. 
            (part that is open-to-ground). 
        * anchors (collections.OrderedDict): 
            anchors used to direct the resonator Route. 
        * fillet (float or string): 
            Fillet for Route curves. 

    """
    start_x, start_y = design.parse_value([start_x, start_y])
    end_x_offset, fillet = design.parse_value([end_x_offset, fillet])

    first_anchor = next(iter(anchors.values()))
    last_anchor  = next(reversed(anchors.values())) #O(1) 

    # orientation for resonator terminations 
    orientation = '0' if first_anchor[0] > last_anchor[0] else '180'

    stg_in = ShortToGround(
        design, 
        f'{name}_stgin', 
        options=Dict(
            pos_x=start_x, 
            pos_y=start_y, 
            orientation=orientation, 
        )
    )
    stg_out = ShortToGround( 
        design,
        f'{name}_stgout', 
        options=Dict( 
            pos_x=start_x+end_x_offset, 
            pos_y=last_anchor[1], 
            orientation=orientation, 
        )
    )

    resonator_opts = Dict(
        pin_inputs=Dict(
            start_pin=Dict(component=stg_in.name, pin='short'), 
            end_pin=Dict(component=stg_out.name, pin='short'),
        ), 
        anchors=anchors, 
        trace_width='20um', 
        trace_gap='10um', 
        fillet=fillet,
        step_size='0.05mm', 
        total_length=length,
    )

    rp = RouteMixed(
        design, 
        f'{name}', 
        options=resonator_opts, 
    )

    print(f'{name} slack: {design.parse_value(length) - design.parse_value(rp.options._actual_length)}')
