# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 13:51:23 2022

@author: arvidro
"""
import xml.etree.ElementTree as ET
from HelpFunctions import *
from Definitions import *

class TraversalNode:
    
    def __init__(self, ID, node_type, CE_type=None, name=None, Terminal_List=[],
                  CE = None, CN=None, busbar_ID=None, busbar_voltage=None):
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
        self.busbar_voltage = busbar_voltage
        self.transformer_traversal_order = [] # used to indicate the order in which the terminals of a transformer were encountered
        
    def set_busbar_ID(self, busbar_ID):
        self.busbar_ID = busbar_ID
    def traverse_transformer(self, terminal_ID):
        # To keep track of which transformer end was traversed first for pairing
        # with the right busbar
        self.transformer_traversal_order.append(terminal_ID)
    def set_busbar_voltage(self, busbar_voltage):
        # this is useful to have when building e.g. transformers in 
        # pandapower, as the high, lo and medium windings have to be associated
        # with the right bb
        self.busbar_voltage = busbar_voltage
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
                    if CE_type == 'BusbarSection':
                        voltage = get_base_voltage(tree, child)
                        node.set_busbar_voltage(voltage)
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
    
        
    


    

        

    
#tree = ET.parse('Assignment_EQ_reduced.xml')
#root = tree.getroot()

#tn = get_nodes(root)
#set_busbar_IDs(tn)
topology, everything_stack = get_topology('Assignment_EQ_reduced.xml')
Trans = Transformer('_a708c3bc-465d-4fe7-b6ef-6fa6408a62b0')
#acls = ACLineSegment('_b58bf21a-096a-4dae-9a01-3f03b60c24c7')
bbs = Trans.get_connections(topology)