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
import pandapower.plotting as plot

import pandapower.networks as nw 
import matplotlib.pyplot as plt
import os
import seaborn

colors = seaborn.color_palette()


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
    def __init__(self, EQ_filename='MicroGridEQ.xml', SSH_filename='MicroGridSSH.xml'):
        
        self.EQ_filename = EQ_filename
        self.SSH_filename = SSH_filename
        self.get_topology(EQ_filename)
        self.busbar_mapping(get_busbar_list(self.topology))
        self.get_component_IDs()
        self.make_components(EQ_filename, SSH_filename)
        
    def busbar_mapping(self, busbar_list):
        busbar_map = {}
        for i, bb in enumerate(busbar_list):
            busbar_map['{}'.format(bb)] = i
        self.busbar_map = busbar_map
    def get_topology(self, EQ_filename):
        self.topology, e_stack = tp.get_topology(EQ_filename)
    
    def get_component_IDs(self):
        components = {}
        n_components = 0
        for CE_type in conductive_equipment:
            components[CE_type] = []
        for top in self.topology:
            for node in top:
                CE_type = node.CE_type
                if node.ID not in components[CE_type]:
                    components[CE_type].append(node.ID)
                    n_components += 1
        self.component_IDs = components
        self.n_components = n_components
        
    def make_components(self, EQ_filename=EQ_filename, SSH_filename=SSH_filename):
        components = {key:[] for key in conductive_equipment}
        indices = (i for i in range(len(self.busbar_map), self.n_components))
        comp_ind_map = {key:{} for key in conductive_equipment}
        for key, IDs in self.component_IDs.items():
            
            
                # assign an index to every component that is not a busbar
            for ID in IDs:
                if key != 'BusbarSection':
                    index = next(indices, 'ran out of inds')
                    comp_ind_map[key][ID] = index 
            
                if key == 'ACLineSegment':
                    comp = pe.ACLineSegment(ID, EQ_filename)
                elif key == 'BusbarSection':
                    comp = pe.BusBarSection(ID, EQ_filename)
                elif key == 'Breaker':
                    comp = pe.Breaker(ID, EQ_filename, SSH_filename)
                elif key == 'EnergyConsumer':
                    comp = pe.EnergyConsumer(ID, EQ_filename, SSH_filename)
                elif key == 'SynchronousMachine':
                    #key = 'GeneratingUnit'
                    comp = pe.GeneratingUnit(ID, EQ_filename, SSH_filename)
                elif key == 'LinearShuntCompensator':
                    comp = pe.Shunt(ID, EQ_filename, SSH_filename)
                elif key == 'PowerTransformer':
                    comp = pe.Transformer(ID, EQ_filename, SSH_filename)
                if key != 'BusbarSection':
                    comp.get_connections(self.topology)
                components[key].append(comp)
        self.components = components
        self.comp_ind_map = comp_ind_map
    
    def create_net(self, name="My Network"):
        busbar_map = self.busbar_map
        comp_ind_map = self.comp_ind_map
        net = pp.create_empty_network(name=name)
        for bb in self.components['BusbarSection']:
            bb.to_pp(net, busbar_map, comp_ind_map)
        for key, val in self.components.items():
            if key == 'BusbarSection' or key == 'Breaker':
                continue
            else:
                for comp in val:
                    comp.to_pp(net, busbar_map, comp_ind_map)
        for breaker in self.components['Breaker']:
            breaker.to_pp(net, busbar_map, comp_ind_map)
        return net
    
EQ_names = ('Assignment_EQ_reduced.xml', 'MicroGridEQ.xml',
            "MicroGridTestConfiguration_T1_BE_EQ_V2.xml",
            "MicroGridTestConfiguration_T1_NL_EQ_V2.xml",
            "MicroGridTestConfiguration_T4_NL_EQ_V2.xml")
SSH_names = ('Assignment_SSH_reduced.xml', 'MicroGridSSH.xml',
            "MicroGridTestConfiguration_T1_BE_SSH_V2.xml",
             "MicroGridTestConfiguration_T1_NL_SSH_V2.xml",
             "MicroGridTestConfiguration_T4_NL_SSH_V2.xml")

GB = GridBuilder(EQ_names[1],SSH_names[1])


net = GB.create_net()

#lc = plot.create_line_collection(net, net.line.index, color="grey", zorder=1)
#bc = plot.create_bus_collection(net, net.bus.index, size=80, color=colors[0], zorder=2)
#plot.draw_collections([lc,bc], figsize=(8,6))
plot.simple_plot(net,respect_switches=True, plot_loads=True,
                 plot_line_switches=True, plot_sgens=True)   
            