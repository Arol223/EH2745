# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 13:51:23 2022

@author: arvidro
"""
import xml.etree.ElementTree as ET

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
    name = element.find('cim:IdentifiedObject.name').text
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
    
    def __init__(self, ID, node_type, CE_type, name=None, Terminal_List=[],
                 num_attch_terms=0, CE = None, CN=None):
        # The CE and CN attributes are None if the node is not a terminal
        if name is not None:
            self.name = name
        self.node_type = node_type
        self.CE = CE
        self.CN = CN
        self.CE_type = CE_type
        self.Terminal_List = Terminal_List
        self.num_attch_terms = num_attch_terms
        self.traversed = False
    
    def traverse(self):
        self.traversed = True
    
    
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
        for terminal in current_node.Terminal_List:
            if not terminal['traversed']:
                next_ID = terminal['ID']
    
    return next_ID

def get_nodes(tree):
    traversal_nodes = {}
    for child in tree.iter():
        if ns['cim'] + 'ConnectivityNode' in child.tag:
            
    return traversal_nodes

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


tree = ET.parse('Assignment_EQ_reduced.xml')
root = tree.getroot()

trafo = root.find('cim:PowerTransformer',ns)

ends = get_transformer_ends(root, get_ID(trafo))