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
    
    def __init__(self, ID, node_type, CE_type, Terminal_List=[],
                 num_attch_terms=0):
        self.node_type = node_type
        self.CE_type = CE_type
        self.Terminal_List = Terminal_List
        self.num_attch_terms = num_attch_terms

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
