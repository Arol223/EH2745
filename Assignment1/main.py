#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  8 15:54:09 2022

@author: Arvid
"""

import GridBuilding as GB
import pandapower.plotting as plot

EQ_names = ('Assignment_EQ_reduced.xml', 'MicroGridEQ.xml',
            "MicroGridTestConfiguration_T1_BE_EQ_V2.xml",
            "MicroGridTestConfiguration_T1_NL_EQ_V2.xml",
            "MicroGridTestConfiguration_T4_NL_EQ_V2.xml")
SSH_names = ('Assignment_SSH_reduced.xml', 'MicroGridSSH.xml',
            "MicroGridTestConfiguration_T1_BE_SSH_V2.xml",
             "MicroGridTestConfiguration_T1_NL_SSH_V2.xml",
             "MicroGridTestConfiguration_T4_NL_SSH_V2.xml")

def main():
    print("Available files are: ")
    for i, f in enumerate(EQ_names):
        print("Number: {}".format(i))
        print("Filename: {}".format(f))
        cont = 'y'
    

    file_n = input("Choose the number of the file you want to plot: ")
    file_n = int(file_n)
    try:
        G = GB.GridBuilder(EQ_names[file_n],SSH_names[file_n])
    
        
        
        net = G.create_net()
        
        
        
        plot.simple_plot(net, respect_switches=False, line_width=1.0, bus_size=1.0, \
                         ext_grid_size=1.0, trafo_size=1.0, plot_loads=True, \
                             plot_sgens=True, load_size=2.0, sgen_size=2.0, switch_size=1.0,\
                                 switch_distance=1.0, plot_line_switches=True, scale_size=True, \
                              bus_color='b', line_color='grey', trafo_color='k',\
                              ext_grid_color='y', switch_color='k', library='igraph',\
                              show_plot=True, ax=None)
    except:
        print("Something went wrong while trying to build a grid, choose a different file")
        
        # cont = input("Continue? [y]/[n]")
        # if cont == 'n':
        #     print("Exiting")
        #     break
if __name__ == '__main__':
    main()