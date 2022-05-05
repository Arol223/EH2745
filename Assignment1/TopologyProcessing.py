# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 13:51:23 2022

@author: arvidro
"""
import xml.etree.ElementTree as ET
from collections import deque # This is used as a stack in the tree traversal, has faster methodws than lists which is relevant for larger grids
ns = {'cim':'http://iec.ch/TC57/2013/CIM-schema-cim16#',
      'entsoe':'http://entsoe.eu/CIM/SchemaExtension/3/1#',
      'rdf':'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'}

# 7 Types of conducting equipment. Special care has to be taken with the power 
# transformers, as these are defined with transformer ends with a given terminal.
conductive_equipment = ('ACLineSegment', 'BusbarSection', 'Breaker',
                        'EnergyConsumer', 'SynchronousMachine',
                        'LinearShuntCompensator', 'PowerTransformer')
tap_changer_EQ_parameters = ('lowStep', 'highStep', 'neutralStep', 
                             'normalStep', 'neutralU')
ratio_tap_changer_EQ_parameters = ('stepVoltageIncrement')
phase_tap_changer_EQ_parameters = ('PhaseTapChangerNonLinear.voltageStepIncrement')
tap_changer_SSH_parameters = ('step')
tapchanger_types = ('RatioTapChanger', 'PhaseTapChangerAsymmetrical')


AC_line_segment_params = ('ACLineSegment.r', 'ACLineSegment.x',
                          'Conductor.length')

EQ_filename = "Assignment_EQ_reduced.xml"
SSH_filename = "Assignment_SSH_reduced.xml"

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
    
    for VL in tree.findall('cim:VoltageLevel'):
        if get_ID(VL) == VL_ID:
            BV_ID = get_base_voltage_ID(VL)
            break
    for BV in tree.findall('cim:BaseVoltage'):
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

class TraversalNode:
    
    def __init__(self, ID, node_type, CE_type=None, name=None, Terminal_List=[],
                  CE = None, CN=None, busbar_ID=None):
        # The CE and CN attributes are None if the node is not a terminal
        # The busbar_ID attribute applies to CN that are connected to busbars
        if name is not None:
            self.name = name
        self.ID = ID
        self.num_attch_terms = len(Terminal_List)
        self.node_type = node_type
        self.CE = CE
        self.CN = CN
        self.CE_type = CE_type
        self.Terminal_List = Terminal_List
        self.traversed = False
        self.busbar_ID = busbar_ID
        
        self.transformer_traversal_order = [] # used to indicate the order in which the terminals of a transformer were encountered
        
    def set_busbar_ID(self, busbar_ID):
        self.busbar_ID = busbar_ID
    def traverse_transformer(self, terminal_ID):
        # To keep track of which transformer end was traversed first for pairing
        # with the right busbar
        self.transformer_traversal_order.append(terminal_ID)
    
def set_busbar_IDs(traversal_nodes):
    for node in traversal_nodes.values():
        if node.node_type == 'CN':
            for term in node.Terminal_List.keys():
                CE = traversal_nodes[traversal_nodes[term].CE]
                if traversal_nodes[traversal_nodes[term].CE].CE_type == 'BusbarSection':
                    node.set_busbar_ID({'Busbar':CE.ID, 'Terminal':term})
                    break
        
def get_terminal_parents(terminal):
    res = get_resources(terminal)
    parents = {'CN': res['Terminal.ConnectivityNode'], 'CE':res['Terminal.ConductingEquipment']}
    return parents

def find_next_node(previous_node, current_node):
    curr_type = current_node.node_type
    prev_type = previous_node.node_type
    if curr_type == 'Te':
        if prev_type == 'CE':
            next_type = 'CN'
        else:
            next_type = 'CE'
    else:
        next_type = 'Te'
    if next_type == 'CE':
        next_ID = current_node.CE
    elif next_type == 'CN':
        next_ID = current_node.CN
    else:
        for terminal, traversed in current_node.Terminal_List.items():
            if not traversed:
                next_ID = terminal
                break
    
    return next_ID

def print_node_types(traversal_nodes):
    for node in traversal_nodes.values():
        if node.node_type == 'CE':
            print('Node object is a: ' + node.CE_type)
            
def get_nodes(tree):
    traversal_nodes = {}
    for child in tree.iter():
        if child.tag == '{' + ns['cim']  + '}' + 'ConnectivityNode':
            ID = get_ID(child)
            terms = get_terminals(tree, ID, CE=False)

            
            terminal_list = {ID:False for ID in terms}#{[{'ID':ID, 'traversed':False} for ID in terms]}
            
            node = TraversalNode(ID, node_type='CN', name=get_name(child),
                                 Terminal_List=terminal_list)
            traversal_nodes[ID] = node
        elif child.tag == '{' + ns['cim']  + '}' + 'Terminal':
            ID = get_ID(child)
            parents = get_terminal_parents(child)
            node = TraversalNode(ID, 'Te', **parents)
            traversal_nodes[ID] = node
        else:
            for CE_type in conductive_equipment:
                if child.tag == '{' + ns['cim'] + '}' + CE_type:
                    ID = get_ID(child)
                    name = get_name(child)
                    terms = get_terminals(tree, ID, CE=True)
                    terminal_list = {ID:False for ID in terms}
                    node = TraversalNode(ID, 'CE', CE_type=CE_type, name=name, 
                                         Terminal_List=terminal_list)
                    traversal_nodes[ID] = node
    
    return traversal_nodes

def print_topology(topology, index=None):
    if index is None:
        for i, top in enumerate(topology):
            print("The {}th topology section is: ".format(i))
            for node in top:
                print(node.CE_type)
    else:
        if index == -1:
            index = len(topology) - 1
        print("The {}th topology section is: ".format(index))
        top = topology[index]
        for node in top:
            print(node.CE_type)

def find_CE(filename='Assignment_EQ_reduced.xml'):
    tree = ET.parse(filename)
    root = tree.getroot()
    
    CE_types = []
    for element in root.iter():
        try:
            ID = get_ID(element)
        except KeyError:
            #print('Element did not have ID')
            #print(element.tag)
            continue
        terms = get_terminals(root, ID, CE=True)
        if len(terms) > 0:
            tag = element.tag.replace('{' + ns['cim'] + '}', '')
            if tag not in CE_types:
                CE_types.append(tag)
    return CE_types

def get_topology(filename):
    # process topology from a cim-xml file, follows proposed algo from provided paper 
    root = ET.parse(filename).getroot()
    traversal_nodes = get_nodes(root)
    set_busbar_IDs(traversal_nodes)
    print_node_types(traversal_nodes)
    CN_stack = []#deque()
    CE_stack = []#deque()
    all_ce = []
    everything_stack = []#deque()
    
    topology = []
    
    for node in traversal_nodes.values():
        # Find a suitable end device for the first node
        if node.num_attch_terms == 1 and node.CE_type != 'BusbarSection':
            previous_node = current_node = node
            break
    
    # This is the algorithm from the paper
    loop_number = 0
    while len(everything_stack) < len(traversal_nodes):
        loop_number += 1
        # print('Number of iterations: {}'.format(loop_number))
        # print("Length of everything_stack: {}".format(len(everything_stack)))
        # print("Found CE: {}".format(len(all_ce)))
        #next_node = traversal_nodes[find_next_node(previous_node, current_node)]
        # print(previous_node.node_type)
        # print(current_node.node_type)
        #print(next_node.node_type)
        previous_ID = previous_node.ID
        current_id = current_node.ID
        if current_node.node_type == 'Te':
            next_node = traversal_nodes[find_next_node(previous_node, current_node)]
            previous_node.Terminal_List[current_id] = True # Indicate that the terminal has been traversed
            #next_node.Terminal_List[current_id] = True
            if current_node not in everything_stack:
                everything_stack.append(current_node)
            if next_node.node_type == 'CN':
                if next_node not in CN_stack:
                    CN_stack.append(next_node)
                # Option 1: CN is not attached to a busbar
                if next_node.busbar_ID is None:
                    # Updating the nodes
                    previous_node = current_node
                    current_node = next_node
                    
                
                # Option 2: CN is attached to a busbar
                else:
                    busbar = traversal_nodes[next_node.ID].busbar_ID
                    terminal_ID = busbar['Terminal']
                    busbar_ID = busbar['Busbar']
                    bb = traversal_nodes[busbar_ID]
                    term = traversal_nodes[terminal_ID]
                    bb.Terminal_List[terminal_ID] = True
                    if bb not in everything_stack:
                        everything_stack.append(bb)
                    if term not in everything_stack:
                        everything_stack.append(term)
                    if bb not in all_ce:
                        all_ce.append(bb)
                    next_node.Terminal_List[terminal_ID] = True
                    CE_stack.append(traversal_nodes[busbar_ID])
                    topology.append(CE_stack)
                    CE_stack = []#deque()  # Clear the CE-stack to get a clean slate for next publication
                    CE_stack.append(traversal_nodes[busbar_ID])
                    previous_node = current_node
                    current_node = next_node
                    print_topology(topology)
                
            elif next_node.node_type == 'CE':
                previous_node = current_node
                current_node = next_node
                
        
        elif current_node.node_type == 'CN':
            if previous_ID in current_node.Terminal_List.keys():
                current_node.Terminal_List[previous_ID] = True
            if current_node not in CN_stack:
                CN_stack.append(current_node)
            if current_node not in everything_stack:
                everything_stack.append(current_node)
            found_non_traversed = False
            for term, trav in current_node.Terminal_List.items():
                if not trav:
                    next_node = traversal_nodes[find_next_node(previous_node, current_node)]
                    previous_node = current_node
                    current_node = next_node
                    found_non_traversed = True
                    break
            if not found_non_traversed:
                if len(CE_stack) > 2:
                    topology.append(CE_stack)
                    print_topology(topology, index=-1)
                    CE_stack = []#deque()
                CN_stack.pop()
                current_node = CN_stack[-1]
                #next_node = traversal_nodes[find_next_node(previous_node, current_node)]
            
        elif current_node.node_type == 'CE':
            if current_node not in all_ce:
                all_ce.append(current_node)
            previous_type = previous_node.node_type
            #print(current_node.CE_type)
            if previous_type == 'Te':
                current_node.Terminal_List[previous_ID] = True
            CE_stack.append(current_node)
            if current_node not in everything_stack:
                everything_stack.append(current_node)
            found_non_traversed = False
            if current_node.CE_type == 'PowerTransformer':
                # Keep track of traversal order
                current_node.traverse_transformer(previous_ID)
            for term, trav in current_node.Terminal_List.items():
                if not trav:
                    next_node = traversal_nodes[find_next_node(previous_node, current_node)]
                    if current_node.CE_type == 'PowerTransformer':
                        # adding the next node here in case an odd number of terminals 
                        # exist, e.g. three winding trafo.
                        current_node.traverse_transformer(next_node.ID)
                    previous_node = current_node
                    current_node = next_node
                    found_non_traversed = True
                    break
            if not found_non_traversed:
                topology.append(CE_stack)
                if len(CE_stack) > 2:
                    print_topology(topology, index=-1)
                CE_stack = []#deque()
                current_node = CN_stack[-1]
                bb_ID = current_node.busbar_ID
                if bb_ID is not None:
                    CE_stack.append(traversal_nodes[bb_ID['Busbar']]) # Add the busbar if one exists
    return topology, everything_stack
    

class Transformer:
    
    def __init__(self, ID, EQ_filename=EQ_filename, SSH_filename=SSH_filename):
        self.ID = ID
        self.get_ends(EQ_filename)
        self.get_tap_changer(EQ_filename, SSH_filename)
    
    def get_ends(self, EQ_filename):
        # get the transformer ends and rated voltages, rated S for the transformer 
        tree = ET.parse(EQ_filename).getroot()
        self.transformer_ends = get_transformer_ends(tree, self.ID)
        self.rated_S = self.terminal_end[0]['Rated_S']
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
        for child in TC.iter:
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
        
        for TC in SSH_tree.findall('cim:{}'.format(TC_type)):
            if get_about_SSH(TC) == tap_changer['ID']:
                step = TC.find('cim:TapChanger.step').text
                tap_changer['step'] = step
                break
        self.tap_changer = tap_changer
        
                
def get_about_SSH(element):        
    about = element.attrib[ns['rdf' + 'about']].replace('#', '')
    return about
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
            if breaker.attrib[ns['rdf'] + 'about'].replace('#', '') == self.ID:
                stat = breaker.find('cim:Switch.open',ns).text
                if stat == 'false':
                    self.set_open_status(False)
                else:
                    self.set_open_status(True)
                break

def find_element(tree, ID, element_type):
    # Find a particular element in the tree by matching ID and type
    # Implemented because this is used a __lot__
    for  element in tree.findall('cim:{}'.format(element_type), ns):
            if get_ID(element) == ID:
                return element
class BusBar:
    def __init__(self, ID, filename=EQ_filename):
        self.ID = ID
        
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
        for line in tree.findall('cim:ACLinesSegment'):
            if get_ID(line) = self.ID:
                break
        for 

#tree = ET.parse('Assignment_EQ_reduced.xml')
#root = tree.getroot()

#tn = get_nodes(root)
#set_busbar_IDs(tn)
#topology, everything_stack = get_topology('Assignment_EQ_reduced.xml')
