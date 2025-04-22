# doesn't work in .py file. 
# MetalGUI requires ipykernel.

from qiskit_metal import designs, MetalGUI, draw, Dict
from qiskit_metal.toolbox_metal.parsing import parse_value
from qiskit_metal.qlibrary.terminations.launchpad_wb import LaunchpadWirebond
from qiskit_metal.qlibrary.terminations.short_to_ground import ShortToGround
from qiskit_metal.qlibrary.terminations.open_to_ground import OpenToGround
from qiskit_metal.qlibrary.tlines.pathfinder import RoutePathfinder
from qiskit_metal.qlibrary.QNLMetal.alignmentmarker import AlignmentMarker 

# custom components
from components.right_flux_singlet import right_flux_singlet
from components.right_flux_doublet import right_flux_doublet
from components.coupling_resonator_ import resonator 
from components.readout_bus import readout_bus 
from components.left_transmon import left_transmon_resonator
from components.left_flux_doublet import left_flux_doublet
from collections import OrderedDict
import numpy as np


class CoupledFluxonium(): 
    def __init__(self, design, right_flux_x=0, right_flux_y=0): 
        self.design = design 
        self.gui = MetalGUI(design)
        self.right_flux_x = right_flux_x 
        self.right_flux_y = right_flux_y

        self.options = Dict(
            singlet_y_offset = parse_value('-2575um', Dict()), 
            idc_x_offset = parse_value('-32.5um', Dict())+parse_value('-20.5um', Dict()),
            idc_y_offset = parse_value('-4242um', Dict()), 
            tsmn_x_offset= parse_value('-3405um', Dict()) + parse_value('280um', Dict()), 
            tsmn_y_offset= parse_value('1687um', Dict()), 
            left_doublet_y_offset = parse_value('-649.5um', Dict()), 
            r_align_marker_xoffset= parse_value('2500um', Dict()), 
            r_align_marker_yoffset= parse_value('3388um', Dict()),
            align_marker_gap = parse_value('8400um', Dict()),
        )

        self.launch_options =  {
            'lead_length': '0um',
            'pad_width': '375um',
            'pad_height': '125um',
            'taper_height': '100um',
            'trace_gap': '5um',
            'trace_width': '8um',
            'fluxline_launches': {
                'top_right': (
                    right_flux_x + parse_value('2300.0um', Dict()), 
                    right_flux_y + parse_value('3706.5um', Dict())),
                'offsets': {
                    'top_right': (0, 0), 
                    'top_left' : (parse_value('-8000um', Dict()), 0), 
                    'bottom_right': (parse_value('518.5um', Dict()), parse_value('-8518.0um', Dict())), 
                    'bottom_left' : (parse_value('-8518.5um', Dict()), parse_value('-9037um', Dict())), 
                    'left_center' : (parse_value('-8518.5um', Dict()), parse_value('-4518.5um', Dict())),
                },
            }, 
            'cpw_launches': { 
                'top_right': (
                    right_flux_x + parse_value('2818.5um', Dict()),
                    right_flux_y + parse_value('3188um', Dict())), 
                'offsets': { 
                    'top_right': (0, 0), 
                    'top_left' : (parse_value('-9037um', Dict()), 0) ,
                    'bottom_right': (parse_value('-518.5um', Dict()), parse_value('-8518um', Dict())),
                    'bottom_left' : (parse_value('-9037um', Dict()), parse_value('-8000um', Dict())),
                    'right_center': (0, parse_value('-4000um', Dict())),
                },
            },  
        }       
        
      
    def right_doublet(self): 
        self.right_doublet_nodes = right_flux_doublet(
            self.design, 
            pos_x=self.right_flux_x, 
            pos_y=self.right_flux_y
        ) 
        self.gui.rebuild()

    def right_doublet_resonators(self): 
        upper_x, upper_y = self.right_doublet_nodes['upper_qubit_claw'] 
        lower_x, lower_y = self.right_doublet_nodes['lower_qubit_claw'] 
        
        self.nodes_doublet_upper_res = resonator(self.design, upper_x, upper_y, key='upper_doublet', name='upper_doublet_resonator')
        self.nodes_doublet_lower_res = resonator(self.design, lower_x, lower_y, key='lower_doublet', name='lower_doublet_resonator')
        self.gui.rebuild()

    def right_singlet(self):
        right_flux_sing_x = self.right_flux_x 
        right_flux_sing_y = self.right_flux_y + self.options.singlet_y_offset

        self.right_singlet_nodes = right_flux_singlet(
            self.design, 
            pos_x=right_flux_sing_x, 
            pos_y=right_flux_sing_y, 
            name='flux_singlet'
        )
        self.gui.rebuild()

    def singlet_resonator(self): 
        sing_res_x, sing_res_y = self.right_singlet_nodes['qubit_claw'] 

        self.singlet_resonator_nodes = resonator(
            self.design, 
            pos_x=sing_res_x, 
            pos_y=sing_res_y, 
            key='singlet', 
            name='singlet_resonator'
        )
        self.gui.rebuild()
        
    def readout_bus(self): 
        idc_pos_x = self.nodes_doublet_upper_res.closest_to_bus[0] + self.options.idc_x_offset
        idc_pos_y = self.right_flux_y + self.options.idc_y_offset
        
        self.readout_bus_nodes = readout_bus(
            self.design, 
            pos_x=idc_pos_x, 
            pos_y=idc_pos_y,
            name='readout_bus',
        ) 
        self.gui.rebuild() 

    def left_transmon(self): 
        tsmn_x = self.right_flux_x + self.options.tsmn_x_offset
        tsmn_y = self.right_flux_y + self.options.tsmn_y_offset
        
        self.left_tsmn_nodes = left_transmon_resonator(
            self.design, 
            pos_x=tsmn_x, 
            pos_y=tsmn_y, 
            name='left_transmon_resonator'
        )
        self.gui.rebuild()

    def left_doublet(self): 
        left_flux_x = self.right_flux_x + self.options.tsmn_x_offset
        left_flux_y = self.right_flux_y + self.options.left_doublet_y_offset 
        
        self.left_doublet_nodes = left_flux_doublet(
            self.design, 
            pos_x=left_flux_x, 
            pos_y=left_flux_y,
        ) 
        self.gui.rebuild()
     
    def left_doublet_resonators(self): 
        pos_upper_x, pos_upper_y = self.left_doublet_nodes['upper_qubit_claw'] 
        pos_lower_x, pos_lower_y = self.left_doublet_nodes['lower_qubit_claw'] 
        
        self.nodes_left_doublet_upper_res = resonator(design, pos_upper_x, pos_upper_y, key='upper_left_doublet', name='upper_left_doublet_resonator')
        self.nodes_left_doublet_lower_res = resonator(design, pos_lower_x, pos_lower_y, key='lower_left_doublet', name='lower_left_doublet_resonator')
        self.gui.rebuild() 

    def place_launchpad_cpw_fluxline(self, key):
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
        elif key == 'left_center' : launch_pad_ops['orientation'] = '0'
        else: raise ValueError(f"Unknown key: {key}")

        launch_pad_ops.update({
            'pos_x': top_right[0] + offsets[key][0],
            'pos_y': top_right[1] + offsets[key][1], 
        })
        launch_pad = LaunchpadWirebond(design, name=f'{key}_launch_fluxline', options=launch_pad_ops)
        
        anchors = OrderedDict()
        if key == 'top_right':
            end_pos = self.right_doublet_nodes.upper_flux_line_end
            end_orientation = '270'
            anchors[0] = np.array([
                launch_pad_ops['pos_x'] - parse_value(fillet, Dict()) - parse_value('600um', Dict()),
                launch_pad_ops['pos_y'] - parse_value(fillet, Dict())
            ])
            anchors[1] = anchors[0] + np.array([-parse_value(fillet, Dict()), -parse_value('2200um', Dict())])
            anchors[2] = anchors[1] + np.array([-parse_value(fillet, Dict()) - parse_value('900um', Dict()),
                                                -parse_value(fillet, Dict())])
        elif key == 'top_left':
            end_pos = self.left_doublet_nodes.upper_flux_line_end
            end_orientation = '270'
            anchors[0] = np.array([
                launch_pad_ops['pos_x'] + parse_value(fillet, Dict()) + parse_value('400um', Dict()),
                launch_pad_ops['pos_y'] - parse_value(fillet, Dict())
            ])
            anchors[1] = anchors[0] + np.array([parse_value(fillet, Dict()), -parse_value('2500um', Dict())])
            anchors[2] = anchors[1] + np.array([parse_value(fillet, Dict()) + parse_value('1100um', Dict()),
                                                -parse_value(fillet, Dict())])
        elif key == 'bottom_right':
            end_pos = self.right_doublet_nodes.lower_flux_line_end
            end_orientation = '90'
            anchors[0] = np.array([
                launch_pad_ops['pos_x'] - parse_value(fillet, Dict()) - parse_value('500um', Dict()),
                launch_pad_ops['pos_y'] + parse_value(fillet, Dict())
            ])
            anchors[1] = anchors[0] + np.array([-parse_value(fillet, Dict()), parse_value('3000um', Dict())])
            anchors[2] = anchors[1] + np.array([-parse_value(fillet, Dict()) - parse_value('1718.5um', Dict()),
                                                parse_value(fillet, Dict())])
        elif key == 'bottom_left':
            end_pos = self.left_doublet_nodes.lower_flux_line_end
            end_orientation = '90'
            anchors[0] = np.array([
                launch_pad_ops['pos_x'] + parse_value(fillet, Dict()) + parse_value('500um', Dict()),
                launch_pad_ops['pos_y'] + parse_value(fillet, Dict())
            ])
            anchors[1] = anchors[0] + np.array([parse_value(fillet, Dict()), parse_value('3256.5um', Dict())])
            anchors[2] = anchors[1] + np.array([parse_value(fillet, Dict()) + parse_value('1000um', Dict()),
                                                parse_value(fillet, Dict())])
        elif key == 'left_center':
            fillet = '81um'
            end_pos = self.left_doublet_nodes.central_flux_line_end
            end_orientation = '0'
            anchors[0] = np.array([
                launch_pad_ops['pos_x'] + parse_value('100um', Dict()),
                launch_pad_ops['pos_y']
            ])
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

    def place_launchpad_cpw_qubit(self, key): 
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
            end_pos_ = self.right_doublet_nodes.upper_right
            end_pos_ = end_pos_ + [parse_value('80um', Dict()), 0] 
            end_orientation = '180'
            anchors[0] = np.array([
                launch_pad_ops['pos_x'] - parse_value(fillet, Dict()) - parse_value('188.5um', Dict()),
                launch_pad_ops['pos_y'] - parse_value(fillet, Dict())
            ])
            anchors[1] = anchors[0] + np.array([0, -parse_value('2665um', Dict())])
    
        elif key == 'top_left':
            end_pos_ = self.left_doublet_nodes.upper_left 
            end_pos_ = end_pos_ - [parse_value('80um', Dict()), 0]
            end_orientation = '0'
            anchors[0] = np.array([
                launch_pad_ops['pos_x'] + parse_value(fillet, Dict()) + parse_value('188.5um', Dict()),
                launch_pad_ops['pos_y'] - parse_value(fillet, Dict())
            ])
            anchors[1] = anchors[0] + np.array([0, -parse_value('3215um', Dict())])
            
        elif key == 'bottom_right':
            end_pos_ = self.right_singlet_nodes.right 
            end_pos_ = end_pos_ + [parse_value('75um', Dict()), 0]
            end_orientation= '180'
            anchors[0] = np.array([
                launch_pad_ops['pos_x'] - 1.01*parse_value(fillet, Dict()),
                launch_pad_ops['pos_y'] + 1.01*parse_value(fillet, Dict())
            ])
    
            anchors[1] = anchors[0] - [parse_value('500um', Dict()), 0]
            anchors[2] = anchors[1] + np.array([0, parse_value('2053.5um', Dict())])
           
        elif key == 'bottom_left':
            end_pos_ = self.left_doublet_nodes.lower_left 
            end_pos_ = end_pos_ - [parse_value('80um', Dict()), 0]
            end_orientation = '0'
            anchors[0] = np.array([
                launch_pad_ops['pos_x'] + parse_value(fillet, Dict()) + parse_value('188.5um', Dict()),
                launch_pad_ops['pos_y'] + parse_value(fillet, Dict())
            ])
            anchors[1] = anchors[0] + np.array([0, parse_value('3540um', Dict())])
            
        elif key == 'right_center':
            end_pos_ = self.right_doublet_nodes.lower_right 
            end_pos_ = end_pos_ + [parse_value('80um', Dict()), 0]
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
    
    def fluxline_cpws(self): 
        self.place_launchpad_cpw_fluxline('top_right')  
        self.place_launchpad_cpw_fluxline('top_left') 
        self.place_launchpad_cpw_fluxline('bottom_right')  
        self.place_launchpad_cpw_fluxline('bottom_left') 
        self.place_launchpad_cpw_fluxline('left_center')
        self.gui.rebuild()

    def qubit_cpws(self): 
        self.place_launchpad_cpw_qubit('top_right')  
        self.place_launchpad_cpw_qubit('top_left')
        self.place_launchpad_cpw_qubit('bottom_left')
        self.place_launchpad_cpw_qubit('bottom_right')
        self.place_launchpad_cpw_qubit('right_center')
        self.gui.rebuild()

    def alignment_marker(self, key): 

        pos_x = self.right_flux_x+self.options.r_align_marker_xoffset
        pos_y = self.right_flux_y+self.options.r_align_marker_yoffset
        
        if key == 'upper_right' : 
            pos_x, pos_y = pos_x, pos_y
        elif key == 'upper_left': 
            pos_x -= self.options.align_marker_gap
        elif key == 'lower_right':
            pos_y -= self.options.align_marker_gap
        elif key == 'lower_left': 
            pos_x -= self.options.align_marker_gap
            pos_y -= self.options.align_marker_gap
        else: raise ValueError(f"Invalid Key: {key}") 
    
        AlignmentMarker(self.design, name=f'{key}_marker', options=Dict(
            pos_x=pos_x, 
            pos_y=pos_y, 
            size='20um', 
        ))

    def place_markers(self): 
        self.alignment_marker('upper_right') 
        self.alignment_marker('lower_right') 
        self.alignment_marker('upper_left') 
        self.alignment_marker('lower_left')
        self.gui.rebuild()

    def rebuild(self): 
        self.gui.rebuild() 
        self.gui.autoscale() 

    def export(self, filename='couplet_resonator'): 
        self.design.chips.main.size.center_x='-1700um'
        self.design.chips.main.size.center_y='-811um'
        self.design.chips.main.size.size_x = '10mm' 
        self.design.chips.main.size.size_y = '10mm'
        
        a_gds = self.design.renderers.gds
        a_gds.options.cheese.cheese_0_x = '2um' 
        a_gds.options.cheese.cheese_0_y = '2um' 
        a_gds.options.cheese.delta_x = '10um' 
        a_gds.options.cheese.delta_y = '10um'
        a_gds.options.no_cheese.join_style = '1'
        a_gds.options.no_cheese.buffer = '30um'
        a_gds.options.cheese.edge_nocheese= '80um'
        a_gds.options.cheese.view_in_file = {'main': {1: True}}
        a_gds.options.no_cheese.view_in_file = {'main': {1: True}}
        a_gds.options.negative_mask = Dict(main=[1])
        
        a_gds.export_to_gds(filename)

    def close(self): 
        self.gui.main_window.close()

    def render(self, export=False):
        self.right_doublet() 
        self.right_doublet_resonators() 
        self.right_singlet() 
        self.singlet_resonator() 
        self.readout_bus()
        self.left_transmon() 
        self.left_doublet() 
        self.left_doublet_resonators() 
        self.fluxline_cpws() 
        self.qubit_cpws() 
        self.place_markers() 
        self.rebuild() 
        
        if export: 
            self.export(filename='coupled_fluxonium.gds')
