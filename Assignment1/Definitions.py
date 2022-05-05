# -*- coding: utf-8 -*-
"""
Created on Thu May  5 16:09:11 2022

@author: arvidro
"""

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

SynchronousMachine_params = {'EQ':('RotatingMachine.ratedS', 'RotatingMachine.ratedU'),
                             'SSH':('RotatingMachine.p', 'RotatingMachine.q')}
GeneratingUnit_params = {'EQ':('GeneratingUnit.nominalP', 'GeneratingUnit.initialP'),
                         'SSH':()}

AC_line_segment_params = ('r', 'x',
                          'length')
EnergyConsumer_params = ('p', 'q')

EQ_filename = "Assignment_EQ_reduced.xml"
SSH_filename = "Assignment_SSH_reduced.xml"