# -*- coding: utf-8 -*-
"""
Created on Tue May 31 11:03:45 2022

@author: arvidro
"""

import numpy as np
from numpy.random import random as rand
import pandas as pd

data_folder = "Simulation_results_temp/"

cases = ( "Gen3_disconn", "P_bus6_200",
         "Normal",  "Low -30% Load", "High 30% Load","Extra_load_bus_6",
         "Line_4-9_disconn")
variables = ("va_degree", "vm_pu")
folder_name = "res_bus/"

vm_keys = ["vm_pu_bus{}".format(i) for i in range(1,10)]
va_keys = ["va_degree_bus{}".format(i) for i in range(1,10)]
def get_case(case):
    path = data_folder + case + '/' + folder_name
    vm = pd.read_excel(path + 'vm_pu.xls', index_col=0)
    vm.columns = vm_keys
    va = pd.read_excel(path + 'va_degree.xls', index_col=0)
    va.columns = va_keys
    out_df = pd.concat([vm, va], axis=1)
    return out_df    

def get_all(cases=cases, include_class=True):
    frames = []
    for i, case in enumerate(cases):
        frames.append(get_case(case))
        if include_class:
            frames[i]["Class"] = [i] * frames[i].shape[0]
    return pd.concat(frames, ignore_index=True)

def case_to_class(case):
    for i, c in enumerate(cases):
        if c == case:
            return i 
    
get_all()