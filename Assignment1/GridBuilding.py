# -*- coding: utf-8 -*-
"""
Created on Thu May  5 16:15:55 2022

@author: arvidro
"""

from HelpFunctions import *
import ParameterExtraction as pe
import TopologyProcessing as tp
import pandapower as pp
from Definitions import*

topology_list = tp.get_topology(EQ_filename)

def get_busbar_list(topology_list):
    busbars = []
    for top in topology_list:
        for node in top:
            if node.CE_type == 'BusbarSection':
                if node.ID not in busbars: 
                    busbars.append(node.ID)
    return busbars

class GridBuilder:
    def __init__(self, EQ_filename=EQ_filename, SSH_filename=SSH_filename):
        
        self.EQ_filename = EQ_filename
        self.SSH_filename = SSH_filename
        self.topology = self.get_topology(EQ_filename)
        self.busbar_mapping(get_busbar_list(self.topology))
        self.get_component_IDs()
        
    def busbar_mapping(self, busbar_list):
        busbar_map = {}
        for i, bb in enumerate(busbar_list):
            busbar_map['{}'.format(bb)] = i
        self.busbar_map = busbar_map
    def get_topology(self, EQ_filename):
        self.topology = tp.get_topology(EQ_filename)
    
    def get_component_IDs(self):
        components = {}
        for CE_type in CE_types:
            components[CE_type] = []
        for top in self.topology:
            for node in top:
                CE_type = node.CE_type
                if node.ID not in components[CE_type]:
                    components[CE_type].append(node.ID)
        self.component_IDs = components
    
    def make_components(self, EQ_filename=EQ_filename, SSH_filename=SSH_filename):
        components = {}
        indices = (i for i in range(len(self.busbar_map), len(self.component_IDs)))
        comp_ind_map = {{} for key in conductive_equipment}
        for key, ID in self.component_IDs.items():
            index = next(indices, 'ran out of inds')
            if key != 'BusbarSection':
                # assign an index to every component that is not a busbar
                comp_ind_map[key][ID] = index 
            if key == 'ACLineSegment':
                components[key].append(pe.ACLineSegment(ID, EQ_filename))
            elif key == 'BusbarSection':
                components[key].append(pe.BusBarSection(ID, EQ_filename))
            elif key == 'Breaker':
                components[key].append(pe.Breaker(ID, EQ_filename, SSH_filename))
            elif key == 'EnergyConsumer':
                components[key].append(pe.EnergyConsumer(ID, EQ_filename, SSH_filename))
            elif key == 'SynchronousMachine':
                components['GeneratingUnit'].append(pe.GeneratingUnit(ID, EQ_filename, SSH_filename))
            elif key == 'LinearShuntCompensator':
                components(key).append(pe.Shunt(ID, EQ_filename, SSH_filename))
            elif key == 'PowerTransformer':
                components(key).append(pe.Transformer(ID, EQ_filename, SSH_filename))
            
        self.components = components
        
    
    
            