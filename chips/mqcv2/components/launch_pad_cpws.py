from qiskit_metal.qlibrary.terminations.launchpad_wb import LaunchpadWirebond 
from qiskit_metal.qlibrary.terminations.short_to_ground import ShortToGround
from qiskit_metal.qlibrary.terminations.open_to_ground import OpenToGround
from qiskit_metal.qlibrary.tlines.pathfinder import RoutePathfinder 
from qiskit_metal.toolbox_metal.parsing import parse_value
from qiskit_metal import Dict 
from collections import OrderedDict 
import numpy as np 

class LaunchCPWs():
    def __init__(self, design, main_x=0, main_y=0): 
        self.design = design 
        self.main_x = main_x 
        self.main_y = main_y 

        self.launch_options =  {
            'lead_length': '0um',
            'pad_width': '375um',
            'pad_height': '125um',
            'taper_height': '100um',
            'trace_gap': '5um',
            'trace_width': '8um',
            'fluxline_launches': {
                'top_right': (
                    main_x + design.parse_value('2300.0um'), 
                    main_y + design.parse_value('3706.5um')),
                'offsets': {
                    'top_right': (0, 0), 
                    'top_left' : (design.parse_value('-8000um'), 0), 
                    'bottom_right': (design.parse_value('518.5um'), design.parse_value('-8518.0um')), 
                    'bottom_left' : (design.parse_value('-8000um'), design.parse_value('-9037um')), 
                    'left_center' : (design.parse_value('-8518.5um'), design.parse_value('-4518.5um')),
                },
            }, 
            'cpw_launches': { 
                'top_right': (
                    main_x + design.parse_value('2818.5um'),
                    main_y + design.parse_value('3188um')), 
                'offsets': { 
                    'top_right': (0, 0), 
                    'top_left' : (design.parse_value('-9037um'), 0) ,
                    'bottom_right': (design.parse_value('-518.5um'), design.parse_value('-8518um')),
                    'bottom_left' : (design.parse_value('-9037um'), design.parse_value('-8000um')),
                    'right_center': (0, design.parse_value('-4000um')),
                },
            },  
        }

    def place_launchpad_cpw_fluxline(self, key, end_pos): 
        fillet = '200um'
        launch_pad_params = self.launch_options
        params = launch_pad_params['fluxline_launches']
        top_right = params['top_right']
        offsets   = params['offsets'] 

        launch_pad_ops = {
            key: launch_pad_params[key] 
            for key in [
                'lead_length', 
                'pad_width', 
                'pad_height', 
                'taper_height', 
                'trace_gap', 
                'trace_width'
            ]
        }

        if key   == 'top_right'   : launch_pad_ops['orientation'] = '270'
        elif key == 'top_left'    : launch_pad_ops['orientation'] = '270'
        elif key == 'bottom_right': launch_pad_ops['orientation'] = '180'
        elif key == 'bottom_left' : launch_pad_ops['orientation'] = '90'
        else: raise ValueError(f"Unknown key: {key}")

        launch_pad_ops.update({
            'pos_x': top_right[0] + offsets[key][0],
            'pos_y': top_right[1] + offsets[key][1], 
        })
        launch_pad = LaunchpadWirebond(self.design, name=f'{key}_launch_fluxline', options=launch_pad_ops)
        
        anchors = OrderedDict()
        if key == 'top_right':
            end_orientation = '270'
            anchors[0] = np.array([
                launch_pad_ops['pos_x'] - parse_value(fillet, Dict()) - parse_value('600um', Dict()),
                launch_pad_ops['pos_y'] - parse_value(fillet, Dict())
            ])
            anchors[1] = anchors[0] + np.array([-parse_value(fillet, Dict()), -parse_value('2200um', Dict())])
            anchors[2] = anchors[1] + np.array([-parse_value(fillet, Dict()) - parse_value('900um', Dict()),
                                                -parse_value(fillet, Dict())])
        elif key == 'top_left':
            end_orientation = '270'
            anchors[0] = np.array([
                launch_pad_ops['pos_x'] + parse_value(fillet, Dict()) + parse_value('400um', Dict()),
                launch_pad_ops['pos_y'] - parse_value(fillet, Dict())
            ])
            anchors[1] = anchors[0] + np.array([parse_value(fillet, Dict()), -parse_value('2500um', Dict())])
            anchors[2] = anchors[1] + np.array([parse_value(fillet, Dict()) + parse_value('1100um', Dict()),
                                                -parse_value(fillet, Dict())])
        elif key == 'bottom_right':
            end_orientation = '90'
            anchors[0] = np.array([
                launch_pad_ops['pos_x'] - parse_value(fillet, Dict()) - parse_value('500um', Dict()),
                launch_pad_ops['pos_y'] + parse_value(fillet, Dict())
            ])
            anchors[1] = anchors[0] + np.array([-parse_value(fillet, Dict()), parse_value('3000um', Dict())])
            anchors[2] = anchors[1] + np.array([-parse_value(fillet, Dict()) - parse_value('1718.5um', Dict()),
                                                parse_value(fillet, Dict())])
        elif key == 'bottom_left':
            end_orientation = '90'
            anchors[0] = np.array([
                launch_pad_ops['pos_x'] + parse_value(fillet, Dict()) + parse_value('500um', Dict()),
                launch_pad_ops['pos_y'] + parse_value(fillet, Dict())
            ])
            anchors[1] = anchors[0] + np.array([parse_value(fillet, Dict()), parse_value('3256.5um', Dict())])
            anchors[2] = anchors[1] + np.array([parse_value(fillet, Dict()) + parse_value('1000um', Dict()),
                                                parse_value(fillet, Dict())])
        else:
            raise ValueError(f"Invalid key: {key}")
        
        end_stg = ShortToGround(self.design, f'{key}_fl_cpw_end', options=Dict(
            pos_x=end_pos[0], pos_y=end_pos[1], orientation=end_orientation))
        
        cpw_ops = Dict(pin_inputs=Dict(
            start_pin=Dict(component=launch_pad.name, pin='tie'),
            end_pin=Dict(component=end_stg.name, pin='short')
        ))
        cpw_ops.trace_width = '8um'
        cpw_ops.trace_gap   = '5um'
        cpw_ops.fillet      = fillet
        cpw_ops.anchors     = anchors
        
        RoutePathfinder(self.design, f'{key}_fl_cpw', cpw_ops)

    def place_launchpad_cpw_qubit(self, key, end_pos): 
        fillet = '200um'
        launch_pad_params = self.launch_options
        params = launch_pad_params['cpw_launches']
        top_right = params['top_right']
        offsets   = params['offsets'] 

        launch_pad_ops = {
            key: launch_pad_params[key] 
            for key in [
                'lead_length', 
                'pad_width', 
                'pad_height', 
                'taper_height', 
                'trace_gap', 
                'trace_width'
            ]
        }

        if key   == 'top_right'   : launch_pad_ops['orientation'] = '180'
        elif key == 'top_left'    : launch_pad_ops['orientation'] = '0'
        elif key == 'bottom_right': launch_pad_ops['orientation'] = '90'
        elif key == 'bottom_left' : launch_pad_ops['orientation'] = '0'
        elif key == 'right_center': launch_pad_ops['orientation'] = '180'
        else: raise ValueError(f"Unknown key: {key}")

        launch_pad_ops.update({
            'pos_x': top_right[0] + offsets[key][0],
            'pos_y': top_right[1] + offsets[key][1], 
        })
        launch_pad_qubit = LaunchpadWirebond(self.design, name=f'{key}_launch_qubit', options=launch_pad_ops)
    
        anchors = OrderedDict()
        if key == 'top_right':
            end_pos_ = end_pos + [parse_value('80um', Dict()), 0] 
            end_orientation = '180'
            anchors[0] = np.array([
                launch_pad_ops['pos_x'] - parse_value(fillet, Dict()) - parse_value('188.5um', Dict()),
                launch_pad_ops['pos_y'] - parse_value(fillet, Dict())
            ])
            anchors[1] = anchors[0] + np.array([0, -parse_value('2665um', Dict())])
    
        elif key == 'top_left':
            end_pos_ = end_pos - [parse_value('80um', Dict()), 0]
            end_orientation = '0'
            anchors[0] = np.array([
                launch_pad_ops['pos_x'] + parse_value(fillet, Dict()) + parse_value('188.5um', Dict()),
                launch_pad_ops['pos_y'] - parse_value(fillet, Dict())
            ])
            anchors[1] = anchors[0] + np.array([0, -parse_value('3215um', Dict())])
            
        elif key == 'bottom_right':
            end_pos_ = end_pos + [parse_value('75um', Dict()), 0]
            end_orientation= '180'
            anchors[0] = np.array([
                launch_pad_ops['pos_x'] - 1.01*parse_value(fillet, Dict()),
                launch_pad_ops['pos_y'] + 1.01*parse_value(fillet, Dict())
            ])
    
            anchors[1] = anchors[0] - [parse_value('500um', Dict()), 0]
            anchors[2] = anchors[1] + np.array([0, parse_value('2053.5um', Dict())])
           
        elif key == 'bottom_left':
            end_pos_ = end_pos - [parse_value('80um', Dict()), 0]
            end_orientation = '0'
            anchors[0] = np.array([
                launch_pad_ops['pos_x'] + parse_value(fillet, Dict()) + parse_value('188.5um', Dict()),
                launch_pad_ops['pos_y'] + parse_value(fillet, Dict())
            ])
            anchors[1] = anchors[0] + np.array([0, parse_value('3540um', Dict())])
            
        elif key == 'right_center':
            end_pos_ = end_pos + [parse_value('80um', Dict()), 0]
            end_orientation = '180'

            anchors[0] = end_pos_ + np.array([parse_value('2132um', Dict()), 0])
        else:
            raise ValueError(f"Invalid key: {key}")
            
        end_otg_qubit = OpenToGround(self.design, f'{key}_qubit_cpw_end', options=Dict(
            pos_x=end_pos_[0], pos_y=end_pos_[1], orientation=end_orientation, 
            gap='0um', termination_gap='5um', width='18um'))
    
        cpw_ops_qubit = Dict(pin_inputs=Dict(
            start_pin=Dict(component=launch_pad_qubit.name, pin='tie'),
            end_pin=Dict(component=end_otg_qubit.name, pin='open')
        ))
        cpw_ops_qubit.trace_width = '8um'
        cpw_ops_qubit.trace_gap   = '5um'
        cpw_ops_qubit.fillet      = fillet
        cpw_ops_qubit.anchors     = anchors
        
        RoutePathfinder(self.design, f'{key}_qubit_cpw', cpw_ops_qubit)
