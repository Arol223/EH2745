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
            trafo_end = {}
            trafo_end['ID'] = get_ID(end)
            trafo_end['Rated_U'] = ratedU
            trafo_end['Terminal'] = res['TransformerEnd.Terminal']
            transformer_ends.append(trafo_end)
    return transformer_ends

def get_tap_changer(tree, transformer_end_ID):
    
    for tap_changer in tree.findall('cim:RatioTapChanger', ns):
        res = get_resources(tap_changer)
        if res['RatioTapChanger.TransformerEnd'] == transformer_end_ID:
            ID = get_ID(tap_changer)
            return ID
    for tap_changer in tree.findall('cim:PhaseTapChangerAsymmetrical', ns):
        res = get_resources(tap_changer)
        if res['RatioTapChanger.TransformerEnd'] == transformer_end_ID:
            ID = get_ID(tap_changer)
            return ID
        
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
        
    def set_busbar_ID(self, busbar_ID):
        self.busbar_ID = busbar_ID
    def traverse(self):
        self.traversed = True

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

def print_topology(topology):
    for i, top in enumerate(topology):
        print("The {}th topology section is: ".format(i))
        for node in top:
            print(node.CE_type)
            
def get_topology(filename):
    # process topology from a cim-xml file, follows proposed algo from provided paper 
    root = ET.parse(filename).getroot()
    traversal_nodes = get_nodes(root)
    set_busbar_IDs(traversal_nodes)
    print_node_types(traversal_nodes)
    CN_stack = deque()
    CE_stack = deque()
    everything_stack = deque()
    
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
        print('Number of iterations: {}'.format(loop_number))
        next_node = traversal_nodes[find_next_node(previous_node, current_node)]
        print(previous_node.node_type)
        print(current_node.node_type)
        print(next_node.node_type)
        previous_ID = previous_node.ID
        current_id = current_node.ID
        if current_node.node_type == 'Te':
            #previous_node.Terminal_List[current_id] = True # Indicate that the terminal has been traversed
            #next_node.Terminal_List[current_id] = True
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
                    next_node.Terminal_List[terminal_ID] = True
                    CE_stack.append(traversal_nodes[busbar_ID])
                    topology.append(CE_stack)
                    CE_stack = deque()  # Clear the CE-stack to get a clean slate for next publication
                    CE_stack.append(traversal_nodes[busbar_ID])
                    previous_node = current_node
                    current_node = next_node
                    print_topology(topology)
                
            elif next_node.node_type == 'CE':
                previous_node = current_node
                current_node = next_node
                
        
        elif current_node.node_type == 'CN':
            current_node.Terminal_List[previous_ID] = True
            if current_node not in CN_stack:
                CN_stack.append(current_node)
            if current_node not in everything_stack:
                everything_stack.append(current_node)
            found_non_traversed = False
            for term, trav in current_node.Terminal_List.items():
                if not trav:
                    previous_node = current_node
                    current_node = next_node
                    found_non_traversed = True
                    break
            if not found_non_traversed:
                topology.append(CE_stack)
                print_topology(topology)
                CE_stack = deque()
                CN_stack.pop()
                current_node = CN_stack[-1]
            
        elif current_node.node_type == 'CE':
            previous_type = previous_node.node_type
            #print(current_node.CE_type)
            if previous_type == 'Te':
                current_node.Terminal_List[previous_ID] = True
            CE_stack.append(current_node)
            everything_stack.append(current_node)
            found_non_traversed = False
            for term, trav in current_node.Terminal_List.items():
                if not trav:
                    previous_node = current_node
                    current_node = next_node
                    found_non_traversed = True
                    break
            if not found_non_traversed:
                topology.append(CE_stack)
                print_topology(topology)
                CE_stack = deque()
                current_node = CN_stack[0]
                bb_ID = current_node.busbar_ID
                if bb_ID is not None:
                    CE_stack.append(traversal_nodes[bb_ID['Busbar']]) # Add the busbar if one exists
    return topology, everything_stack
    
class Terminal:
    
    def __init__(self, ID, CE_ID, CN_ID):
        self.ID = ID
        self.CE_ID = CE_ID
        self.CN_ID = CN_ID
        self.visited = False
        
    def traverse(self):
        self.visited = True

class Transformer:
    
    def __init__(self, tree, ID):
        self.ID = ID
        
        ends = self.get_ends(tree)
        
    def get_ends(self, tree):
        pass

class TransformerEnd:
    
    def __init__(self, tree, ID):
        self.ID = ID
    
class NetReader:
    
    def __init__(self, EQ_filename=EQ_filename, SSH_filename=SSH_filename):
         self.load_EQ(EQ_filename)
         self.load_SSH(SSH_filename)
    
    def load_EQ(self, EQfilename):
        self.EQTree = ET.parse(EQfilename).getroot()
        
    
    def load_SSH(self, SSHfilename):
        self.SSHTree = ET.parse(SSHfilename).getroot()
        
    def get_busbar_list(self, tree=None):
        if tree is None:
            tree = self.EQTree
        busbars = tree.findall('cim:BusbarSection', ns)
        return busbars
    
    def get_line_list(self, tree=None):
            if tree is None:
                tree = self.EQTree
            lines = tree.findall('cim:ACLineSegment', ns)
            return lines
    def get_terminal_list(self, tree=None):
            if tree is None:
                tree = self.EQTree
            terminals = tree.findall('cim:Terminal', ns)
            return terminals
    def get_connectivity_node_list(self, tree=None):
            if tree is None:
                tree = self.EQTree
            connectivity_nodes = tree.findall('cim:ConnectivityNode', ns)
            return connectivity_nodes
    
    def get_breaker_list(self, tree=None):
            if tree is None:
                tree = self.EQTree
            breakers = tree.findall('cim:Breaker', ns)
            
            
            
            
    
    def make_equipment(self):
        pass
    
    
class BusBar:
    def __init__(self):
        pass
    
class LineSegment:
    def __init__(self):
        pass


#tree = ET.parse('Assignment_EQ_reduced.xml')
#root = tree.getroot()

#tn = get_nodes(root)
#set_busbar_IDs(tn)
get_topology('Assignment_EQ_reduced.xml')