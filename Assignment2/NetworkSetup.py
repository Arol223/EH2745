# -*- coding: utf-8 -*-
"""
Created on Mon May 30 10:49:53 2022

@author: arvidro
"""

import numpy as np
from numpy.random import random as randn
import pandas as pd

import pandapower as pp
import pandapower.plotting as plt

from pandapower.timeseries import DFData, OutputWriter
from pandapower.timeseries.run_time_series import run_timeseries
from pandapower.control import ConstControl
 
buses = (('Clark', 1) , ('Amherst', 1), ('Winlock', 1),
         ('Bowman', 2), ('Troy', 2), ('Maple', 2),
         ('Grand', 3), ('Wautaga', 3), ('Cross', 3))

vn_kv = 110
length_km = 10
line_type = '149-AL1/24-ST1A 110.0'

lines = ((1,4), (4,5), (5,6), (6,3), (6,7), (7,8), (8,2), (8,9), (9,4), )


loads = ({'Bus':5, 'P':90, 'Q':30},
         {'Bus':7, 'P':100, 'Q':35},
         {'Bus':9, 'P':125, 'Q':50},
         {'Bus':6, 'P':115, 'Q':65})

generators = ({'Bus':1, 'P':0, 'Q':0},
              {'Bus':2, 'P':163, 'Q':0},
              {'Bus':3, 'P':85, 'Q':0})

def run_sim(output_dir, n_timesteps, p_n_loads, q_n_loads, noise_level, x_line=[], x_load=[], x_gen=[]):
    net = setup_network(x_line, x_load, x_gen)
    
    profiles, ds = create_data_source(n_timesteps, p_n_loads, q_n_loads, noise_level)
    
    create_controllers(net, ds)
    
    time_steps = range(0, n_timesteps)
    
    ow = create_output_writer(net, time_steps, output_dir=output_dir)
    
    run_timeseries(net, time_steps)
    
def create_data_source(n_timesteps, p_n_loads, q_n_loads, noise_level):
    profiles = pd.DataFrame()
    
    for i, p in enumerate(p_n_loads):
        profiles['load{}_p'.format(i)] = p*np.ones(n_timesteps) + randn(n_timesteps)*p*noise_level
        
    for i, q in enumerate(q_n_loads):
        profiles['load{}_q'.format(i)] = q*np.ones(n_timesteps) + randn(n_timesteps)*q*noise_level
    
    ds = DFData(profiles)
    return profiles, ds

def create_controllers(net, ds):
    
    for i in range(len(net.load)):
        ConstControl(
            net, element='load', variable='p_mw', element_index=[i],
            data_source=ds, profile_name='load{}_p'.format(i)
            )
        ConstControl(
            net, element='load', variable='q_mvar', element_index=[i],
            data_source=ds, profile_name='load{}_q'.format(i)
            )
    

def create_output_writer(net, time_steps, output_dir):
    ow = OutputWriter(net, time_steps=time_steps, output_path=output_dir,
                      output_file_type=".xls", log_variables=list())
    ow.log_variable('res_bus', 'vm_pu')
    ow.log_variable('res_bus', 'va_degree')
    return ow



def setup_network(x_line=[], x_load=[], x_gen=[]):
    # exclude elements in x_***
    net = pp.create_empty_network(name="Basic Network")
    pp.set_user_pf_options(
        net, init_vm_pu = "flat", init_va_degree = "dc",
        calculate_voltage_angles=True
        )
    for bus in buses:
        pp.create_bus(net, vn_kv, name=bus[0], zone=bus[1])
    for i, line in enumerate(lines):
        if i not in x_line:
            f_bus = line[0]
            t_bus = line[1]
            name = "{}-{}".format(f_bus, t_bus)
            pp.create_line(net, line[0] - 1, line[1] - 1, length_km,
                           name=name, std_type=line_type)
    for i, load in enumerate(loads):
        bus = load["Bus"] - 1
        name = 'load ' + buses[bus][0]
        P = load['P']
        Q = load['Q']
        if i not in x_load:
            pp.create_load(net, bus, P, Q, name=name)
    for i, generator in enumerate(generators):
        bus = generator["Bus"] - 1
        name = 'gen ' + buses[bus][0]
        P = generator['P']
        Q = generator['Q']
        if i not in x_gen:
            if bus == 0:
                slack = True
            else:
                slack = False
            pp.create_gen(net, bus, P, name=name, slack=slack)
    return net

if __name__ == '__main__':
    p_n_loads = np.array([90, 100, 125, 115])*1#[70, 80, 105]#[110, 120, 145] #p_n_loads = [90, 100, 125]
    
    q_n_loads = np.array([30, 35, 50, 75])*1#[20, 25, 40]#[40, 45, 60] #[30, 35, 50]
    noise_level = 0.1
    x_line = [8]
    x_load = []
    x_gen = []
    output_dir = "Simulation_results_temp/"
    output_name = "Line_4-9_disconn"
    time_steps = 100
    run_sim(output_dir + output_name, time_steps, p_n_loads, q_n_loads, noise_level,
            x_line, x_load, x_gen)