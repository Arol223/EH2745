# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 13:51:23 2022

@author: arvidro
"""
import xml.etree.ElementTree as ET

ns = {'cim':'http://iec.ch/TC57/2013/CIM-schema-cim16#',
      'entsoe':'http://entsoe.eu/CIM/SchemaExtension/3/1#',
      'rdf':'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'}

EQ_filename = "Assignment_EQ_reduced.xml"
SSH_filename = "Assignment_SSH_reduced.xml"
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
