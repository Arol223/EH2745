# -*- coding: utf-8 -*-
"""
Created on Thu May  5 16:05:58 2022

@author: arvidro
"""

from Definitions import *

def find_gen_unit(EQ_tree, sync_ID):
    sync_mach = find_element(EQ_tree, sync_ID, 'SynchronousMahine')
    res = get_resources(sync_mach)
    gen_ID = res['RotatingMachine.GeneratingUnit']
    generator = find_element(EQ_tree, gen_ID, 'GeneratingUnit')
    return generator

def find_connections(ID, topology, mode='first'):
    # Given an object ID and a topology list output from the get_topology function, 
    # find the list element in the topology list containing this piece of equipment
    if mode == 'first':
        for top in topology:
            for node in top:
                if node.ID == ID:
                    return top
    elif mode == 'all':
        connections = []
        for top in topology:        
            for node in top:
                if node.ID == ID:
                    connections.append(top)
                    break
        return connections
    
def find_element(tree, ID, element_type, file_type='EQ'):
    # Find a particular element in the tree by matching ID and type
    # Implemented because this is used a __lot__
    for element in tree.findall('cim:{}'.format(element_type), ns):
        if file_type == 'EQ':
            if get_ID(element) == ID:
                return element
        elif file_type == 'SSH':
            if get_about_SSH(element) == ID:
                return element
            
def get_about_SSH(element):        
    about = element.attrib[ns['rdf'] + 'about'].replace('#', '')
    return about

def get_terminals(tree, element_id, CE):
    """
    

    Parameters
    ----------
    tree : etree.ElementTree.ElementTree
        A cim-xml tree to serch for the terminals
    element_id : Str
        The id of the element whose terminals are to be found.
    CE : Bool
        True if the element is a Conducting Equipment, 
        False if the element is a Connectivity Node
    Returns
    -------
    Terminals, a list of all the terminals connected to the element.

    """
    Terminals = []
    if CE:
        key = 'Terminal.ConductingEquipment'
    else:
        key = 'Terminal.ConnectivityNode'
        
    for terminal in tree.findall('cim:Terminal',ns):
        res = get_resources(terminal)
        if res[key] == element_id:
            Terminals.append(terminal.attrib[ns['rdf'] + 'ID'])
    
    return Terminals

def get_terminals2(tree):
    terms = []
    for term in tree.findall('cim:Terminal', ns):
        res = get_resources(term)
        ID = get_ID(term)
        CN = res['cim:Terminal.ConnectivityNode']
        CE = res['cim:Terminal.ConductingEquipment']
        t = {'ID':ID, 'CN':CN, 'CE':CE}
        terms.append(t)
    return terms

def get_name(element):
    """
    

    Parameters
    ----------
    element : etree.ElementTree.Element
           Find the name of the element in cim-xml.

    Returns
    -------
    name (str).

    """
    name = element.find('cim:IdentifiedObject.name', ns).text
    return name
def get_ID(element):
    ID = element.attrib[ns['rdf'] + 'ID']
    return ID

def get_transformer_ends(tree, transformer_id):
    terms = get_terminals(tree, transformer_id, True)
    transformer_ends = []
    for end in tree.findall('cim:PowerTransformerEnd', ns):
        res = get_resources(end)
        if res['TransformerEnd.Terminal'] in terms:
            ratedU = end.find('cim:PowerTransformerEnd.ratedU',ns).text
            ratedS = end.find('cim:PowerTransformerEnd.ratedS',ns).text
            trafo_end = {}
            trafo_end['ID'] = get_ID(end)
            trafo_end['Rated_U'] = ratedU
            trafo_end['Terminal'] = res['TransformerEnd.Terminal']
            trafo_end['Rated_S'] = ratedS
            transformer_ends.append(trafo_end)
    return transformer_ends

def get_tap_changer(tree, transformer_end_ID):
    
    for tap_changer in tree.findall('cim:RatioTapChanger', ns):
        res = get_resources(tap_changer)
        if res['RatioTapChanger.TransformerEnd'] == transformer_end_ID:
            ID = get_ID(tap_changer)
            TC_type = 'RatioTapChanger'
            return ID, TC_type
    for tap_changer in tree.findall('cim:PhaseTapChangerAsymmetrical', ns):
        res = get_resources(tap_changer)
        if res['PhaseTapChanger.TransformerEnd'] == transformer_end_ID:
            ID = get_ID(tap_changer)
            TC_type = 'PhaseTapChangerAsymmetrical'
            return ID, TC_type
    raise Exception("Could not find tap changer for Transformer End")
        
def get_resources(element):
    """
    

    Parameters
    ----------
    element : TYPE
        An element of a cim-xml tree.

    Returns
    -------
    Resources, a dictionary with all resources and their tags.

    """
    resources = {}
    for resource in element.iter():
        if ns['rdf'] + 'resource' in resource.attrib.keys():
            tag = resource.tag.replace('{' + ns['cim'] + '}', '')
            resources[tag] = resource.attrib[ns['rdf'] + 'resource'].replace('#','')
    return resources

def get_voltage_level(element):
    # get the voltage_level ID of an element
    VL = element.find('cim:Equipment.EquipmentContainer', ns)
    VL_ID = VL.attrib[ns['rdf'] + 'resource'].replace('#', '')
    return VL_ID
def get_base_voltage_ID(VoltageLevel):
    # Get the ID of the BaseVoltage associated with a voltage level
    # Input is a VoltageLevel element
    BV = VoltageLevel.find('cim:VoltageLevel.BaseVoltage', ns)
    BV_ID = BV.attrib[ns['rdf'] + 'resource'].replace('#', '')
    return BV_ID

def get_base_voltage(tree, element):
    # Find the basevoltage of an element in the EQ file tree
    VL_ID = get_voltage_level(element)
    
    for VL in tree.findall('cim:VoltageLevel', ns):
        if get_ID(VL) == VL_ID:
            BV_ID = get_base_voltage_ID(VL)
            break
    for BV in tree.findall('cim:BaseVoltage', ns):
        if get_ID(BV) == BV_ID:
            NV = BV.find('cim:BaseVoltage.nominalVoltage', ns).text
            return NV
        
def get_CN(tree):
    
    connectivity_nodes = []
    
    for CN in tree.findall('cim:ConnectivityNode', ns):
        ID = get_ID(CN)
        terms = get_terminals(tree, ID, False)
        n_attch_terms = len(terms)
        node = {}
        node['ID'] = ID
        node['n_attch_terms'] = n_attch_terms
        node['attch_terms'] = terms
        connectivity_nodes.append(node)
    return connectivity_nodes

def get_CE(tree):
    CondEq = []
    
    for CE_type in conductive_equipment:
        for CE in tree.findall('cim:{}'.format(CE_type), ns):
            ID = get_ID(CE)
            terms = get_terminals(tree, ID, True)
            n_attch_terms = len(terms)
            node = {}
            node['ID'] = ID
            node['n_attch_terms'] = n_attch_terms
            node['attch_terms'] = terms
            node['Type'] = CE_type
            CondEq.append(node)
    return CondEq