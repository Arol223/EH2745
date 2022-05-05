# -*- coding: utf-8 -*-
"""
Created on Thu May  5 16:03:45 2022

@author: arvidro
"""

import TopologyProcessing as tp
from xml.etree import ElementTree as ET
from HelpFunctions import *

class GeneratingUnit:
    def __init__(self, sync_ID, EQ_filename, SSH_filename):
        self.ID = sync_ID
        self.get_params(EQ_filename, SSH_filename)
    def get_params(self, EQ_filename, SSH_filename):
        EQ_tree = ET.parse(EQ_filename).getroot()
        SSH_tree = ET.parse(SSH_filename).getroot()
        gen_ID = find_gen_unit(EQ_tree, self.ID)
        sync_machine = find_element(EQ_tree, self.ID, 'SynchronousMachine')
        gen_unit = find_element(EQ_tree, gen_ID, 'GeneratingUnit')
        
        params = {}
        
        for param in SynchronousMachine_params['EQ']:
            value = sync_machine.find('cim:{}'.format(param), ns).text
            params[param.split('.')[-1]] = value
        for param in GeneratingUnit_params['EQ']:
            value = gen_unit.find('cim:{}'.format(param), ns).text
            params[param.split('.')[-1]] = value
        sync_machine = find_element(SSH_tree, self.ID, 'SynchronousMachine', file_type='SSH')
        for param in SynchronousMachine_params['SSH']:
            value = sync_machine.find('cim:{}'.format(param), ns).text
            params[param.split('.')[-1]] = value
        self.parameters = params    
    def get_connections(self, topology_list):
        top = find_connections(self.ID, topology_list)
        for node in top:
            if node.CE_type == 'BusbarSection':
                return node.ID
            
class Transformer:
    
    def __init__(self, ID, EQ_filename=EQ_filename, SSH_filename=SSH_filename):
        self.ID = ID
        self.get_ends(EQ_filename)
        self.get_tap_changer(EQ_filename, SSH_filename)
    
    def get_ends(self, EQ_filename):
        # get the transformer ends and rated voltages, rated S for the transformer 
        tree = ET.parse(EQ_filename).getroot()
        self.transformer_ends = get_transformer_ends(tree, self.ID)
        self.rated_S = self.transformer_ends[0]['Rated_S']
        self.rated_U = [(end['Terminal'], end['Rated_U']) for end in self.transformer_ends]
        self.rated_U.sort()
        
    def get_tap_changer(self, EQ_filename, SSH_filename):
        EQ_tree = ET.parse(EQ_filename).getroot()
        SSH_tree = ET.parse(SSH_filename).getroot()
        for end in self.transformer_ends:
            try:
                ID, TC_type = get_tap_changer(EQ_tree, end['ID'])
                break
            except:
                continue
            print("Transformer has no tap changer")
        TC = find_element(EQ_tree, ID, TC_type)
        tap_changer = {'ID':ID, 'TC_type':TC_type}
        for child in TC.iter():
            tag = child.tag.replace('{' + ns['cim'] + '}' + 'TapChanger.', '')
            RTC_tag = child.tag.replace('{' + ns['cim'] + '}' + 'RatioTapChanger', '')
            PTC_tag = child.tag.replace('{' + ns['cim'] + '}', '')
            if tag in tap_changer_EQ_parameters:
                tap_changer[tag] = child.text
            elif RTC_tag in ratio_tap_changer_EQ_parameters:
                tap_changer[RTC_tag] = child.text
            elif PTC_tag in phase_tap_changer_EQ_parameters:
                tap_changer[PTC_tag.replace('PhaseTapChangerNonLinear.', '')] = child.text
        res = get_resources(TC)
        if 'RatioTapChanger.TransformerEnd' in res.keys():
            tap_changer['trans_end'] = res['RatioTapChanger.TransformerEnd']
        elif 'PhaseTapChanger.TransformerEnd' in res.keys():
            tap_changer['trans_end'] = res['PhaseTapChanger.TransformerEnd']
        
        for TC in SSH_tree.findall('cim:{}'.format(TC_type), ns):
            if get_about_SSH(TC) == tap_changer['ID']:
                step = TC.find('cim:TapChanger.step', ns).text
                tap_changer['step'] = step
                break
        self.tap_changer = tap_changer
        
    def get_connections(self, topology_list):
        # Find busbars connected to transformer and sort the busbars by their nominal
        # voltage
            
        if len(self.transformer_ends) == 2:
            tops = [find_connections(self.ID, topology_list)]
        elif len(self.transformer_ends) == 3:
            tops = find_connections(self.ID, topology_list, mode='all')
        busbars = []
        for top in tops:
            for node in top:
                if node.CE_type == 'BusbarSection':
                    ID = node.ID
                    u = node.busbar_voltage
                    busbars.append((ID, float(u)))
        busbars.sort()
        return busbars

class BusBarSection:
    def __init__(self, ID, filename=EQ_filename):
        self.ID = ID
        self.get_voltage(filename)
        self.get_name(filename)
    def get_voltage(self, filename):
        tree = ET.parse(filename).getroot()
        bb = find_element(tree, self.ID, 'BusbarSection')
        self.NV = get_base_voltage(tree, bb)
            
    def get_name(self, filename):
        tree = ET.parse(filename).getroot()
        bb = find_element(tree, self.ID, 'BusbarSection')
        self.name = get_name(bb)
        
class ACLineSegment:
    def __init__(self, ID, EQ_filename=EQ_filename):
        self.ID = ID
        self.get_parameters(EQ_filename)
    def get_parameters(self, EQ_filename):
        tree = ET.parse(EQ_filename).getroot()
        line = find_element(tree, self.ID, 'ACLineSegment')
        parameters = {}
        
        for param in AC_line_segment_params:
            if param == 'length':
                parameters[param] = line.find('cim:Conductor.{}'.format(param), ns).text
            else:
                parameters[param] = line.find('cim:ACLineSegment.{}'.format(param), ns).text 
        self.parameters = parameters
    def get_connections(self, topology_list):
        top = find_connections(self.ID, topology_list)
        busbars = []
        for node in top:
            if node.CE_type == 'BusbarSection':
                busbars.append(node.ID)
        return busbars
    
class EnergyConsumer:
    def __init__(self, ID, EQ_filename=EQ_filename, SSH_filename=SSH_filename):
        self.ID = ID
        self.get_params(SSH_filename)
        
    def get_params(self, SSH_filename):
        tree = ET.parse(SSH_filename).getroot()
        EC = find_element(tree, self.ID, 'EnergyConsumer', file_type='SSH')
        parameters = {}
        for param in EnergyConsumer_params:
            parameters[param] = EC.find('cim:EnergyConsumer.{}'.format(param), ns).text
        self.parameters = parameters
        
    def get_connections(self, topology_list):
        top = find_connections(self.id, topology_list)
        for node in top:
            if node.CE_type == 'BusbarSection':
                return node.ID

class Shunt:
    def __init__(self, ID, EQ_filename=EQ_filename, SSH_filename=SSH_filename):
        self.ID = ID

    def get_params(self, EQ_filename):
        # To be implemented
        self.params = {'q':1.0}
    def get_connections(self, topology_list):
        top = find_connections(self.ID, topology_list)
        for node in top:
            if node.CE_type == 'BusbarSection':
                return node.ID

class Breaker:
    
    def __init__(self, ID):
        self.ID = ID
        self.open = False
    
    def set_open_status(self, open_):
        self.open = open_
        
    def get_status(self, filename=SSH_filename):
        # Get breaker status from SSH-file
        root = ET.parse(filename).getroot()
        for breaker in root.findall('cim:Breaker', ns):
            if get_about_SSH(breaker) == self.ID:
                stat = breaker.find('cim:Switch.open',ns).text
                if stat == 'false':
                    self.set_open_status(False)
                else:
                    self.set_open_status(True)
                break
    def get_connections(self, topology_list):
        top = find_connections(self.ID, topology_list)
        for ind, node in enumerate(top):
            if node.ID == self.ID:
                index = ind
                break
        connections = {}
        
        for i in [-1, 1]:
            node = top[index + i]
            key = node.CE_type
            ID = node.ID
            connections[key] = ID
        return connections