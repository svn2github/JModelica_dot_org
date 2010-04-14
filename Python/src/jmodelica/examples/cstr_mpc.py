#!/usr/bin/env python 
# -*- coding: utf-8 -*-

# Copyright (C) 2010 Modelon AB
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# Import library for path manipulations
import os.path

import jmodelica
import jmodelica.jmi as jmi
from jmodelica.compiler import OptimicaCompiler
from jmodelica.initialization.ipopt import NLPInitialization
from jmodelica.initialization.ipopt import InitializationOptimizer
from jmodelica.optimization import ipopt

try:
    from jmodelica.simulation.assimulo import JMIDAE, write_data
    from Assimulo.Implicit_ODE import IDA
except:
    raise ImportError('Could not find Assimulo package.')

import numpy as N
import scipy as S
import scipy.optimize as opt
import ctypes as ct
import matplotlib.pyplot as plt

def run_demo(with_plots=True):
    """ Model predicitve control of the Hicks-Ray CSTR reactor.
        This example demonstrates how to use the blocking factor
        feature of the collocation algorithm.
    """

    curr_dir = os.path.dirname(os.path.abspath(__file__));

    # Create a Modelica compiler instance
    oc = OptimicaCompiler()
    
    # Compile the stationary initialization model into a DLL
    oc.compile_model("CSTR.CSTR_Init", curr_dir+"/files/CSTR.mo", target='ipopt')

    # Load a model instance into Python
    init_model = jmi.Model("CSTR_CSTR_Init")

    # Create DAE initialization object.
    init_nlp = NLPInitialization(init_model)

    # Create an Ipopt solver object for the DAE initialization system
    init_nlp_ipopt = InitializationOptimizer(init_nlp)

    def compute_stationary(Tc_stat):
        init_model.set_value('Tc',Tc_stat)
        # Solve the DAE initialization system with Ipopt
        init_nlp_ipopt.init_opt_ipopt_solve()
        return (init_model.get_value('c'),init_model.get_value('T'))

    # Set inputs for Stationary point A
    Tc_0_A = 250
    c_0_A, T_0_A = compute_stationary(Tc_0_A)

    # Print some data for stationary point A
    print(' *** Stationary point A ***')
    print('Tc = %f' % Tc_0_A)
    print('c = %f' % c_0_A)
    print('T = %f' % T_0_A)
    
    # Set inputs for Stationary point B
    Tc_0_B = 280
    c_0_B, T_0_B = compute_stationary(Tc_0_B)
    
    # Print some data for stationary point B
    print(' *** Stationary point B ***')
    print('Tc = %f' % Tc_0_B)
    print('c = %f' % c_0_B)
    print('T = %f' % T_0_B)
    
    oc.compile_model("CSTR.CSTR_Opt_MPC", curr_dir+"/files/CSTR.mo", target='ipopt')

    cstr = jmi.Model("CSTR_CSTR_Opt_MPC")

    cstr.set_value('Tc_ref',Tc_0_B)
    cstr.set_value('c_ref',c_0_B)
    cstr.set_value('T_ref',T_0_B)
    
    cstr.set_value('cstr.c_init',c_0_A)
    cstr.set_value('cstr.T_init',T_0_A)
    
    # Initialize the mesh
    n_e = 50 # Number of elements 
    hs = N.ones(n_e)*1./n_e # Equidistant points
    n_cp = 3; # Number of collocation points in each element

    # Create an NLP object
    # The lenght of the optimization interval is 50s and the
    # number of elements is 50, which gives a blocking factor
    # vector of 2*ones(n_e/2) to match the sampling interval
    # of 2s.
    nlp = ipopt.NLPCollocationLagrangePolynomials(cstr,n_e,hs,n_cp,
                                                  blocking_factors=2*N.ones(n_e/2,dtype=N.int))

    # Create an Ipopt NLP object
    nlp_ipopt = ipopt.CollocationOptimizer(nlp)
   
    nlp_ipopt.opt_sim_ipopt_set_int_option("max_iter",500)

    h = 2. # Sampling interval
    T_final = 180. # Final time of simulation
    t_mpc = N.linspace(0,T_final,T_final/h+1)
    n_samples = N.size(t_mpc)

    ref_mpc = N.zeros(n_samples)
    ref_mpc[0:3] = N.ones(3)*Tc_0_A
    ref_mpc[3:] = N.ones(n_samples-3)*Tc_0_B
    
    cstr.set_value('cstr.c_init',c_0_A)
    cstr.set_value('cstr.T_init',T_0_A)
    
    # Compile the simulation model into a DLL
    oc.compile_model("CSTR.CSTR", curr_dir+"/files/CSTR.mo", target='ipopt')
    
    # Load a model instance into Python
    sim_model = jmi.Model("CSTR_CSTR")
    
    sim_model.set_value('c_init',c_0_A)
    sim_model.set_value('T_init',T_0_A)
    
    
    global cstr_mod
    global cstr_sim
    
    cstr_mod = JMIDAE(sim_model) #Create an Assimulo problem
    cstr_sim = IDA(cstr_mod) #Create an IDA solver
    
    i = 0
    
    plt.figure(4)
    plt.clf()
    
    for t in t_mpc[0:-1]:
        Tc_ref = ref_mpc[i]
        c_ref, T_ref = compute_stationary(Tc_ref)

        cstr.set_value('Tc_ref',Tc_ref)
        cstr.set_value('c_ref',c_ref)
        cstr.set_value('T_ref',T_ref)
        
        # Solve the optimization problem
        nlp_ipopt.opt_sim_ipopt_solve()
        
        # Write to file. 
        nlp.export_result_dymola()
        
        # Load the file we just wrote to file
        res = jmodelica.io.ResultDymolaTextual('CSTR_CSTR_Opt_MPC_result.txt')
        
        # Extract variable profiles
        c_res=res.get_variable_data('cstr.c')
        T_res=res.get_variable_data('cstr.T')
        Tc_res=res.get_variable_data('cstr.Tc')
        
        # Get the first Tc sample
        Tc_ctrl = Tc_res.x[0]
        
        # Solve initialization problem for simulation model
        sim_model.set_value('Tc',Tc_ctrl)
        
        cstr_sim.re_init(t_mpc[i],cstr_sim.y[-1],cstr_sim.yd[-1]) #Re initiates the problem
        
      
        cstr_sim.initiate() #Calculate initial conditions
        cstr_sim.simulate(t_mpc[i+1]) #Simulate
        
        t_T_sim = cstr_sim.t
        
        # Set terminal values of the states
        cstr.set_value('cstr.c_init',cstr_sim.y[-1][0])
        cstr.set_value('cstr.T_init',cstr_sim.y[-1][1])
        sim_model.set_value('c_init',cstr_sim.y[-1][0])
        sim_model.set_value('T_init',cstr_sim.y[-1][1])
        plt.figure(4)
        plt.subplot(3,1,1)
        plt.plot(t_T_sim,N.array(cstr_sim.y)[:,0],'b')
        plt.show()
        
        plt.subplot(3,1,2)
        plt.plot(t_T_sim,N.array(cstr_sim.y)[:,1],'b')
        plt.show()
        
        if t_mpc[i]==0:
            plt.subplot(3,1,3)
            plt.plot([t_mpc[i],t_mpc[i+1]],[Tc_ctrl,Tc_ctrl],'b')
        else:
            plt.subplot(3,1,3)
            plt.plot([t_mpc[i],t_mpc[i],t_mpc[i+1]],[Tc_ctrl_old,Tc_ctrl,Tc_ctrl],'b')
            
        Tc_ctrl_old = Tc_ctrl
            
        i = i+1
        plt.show()


    plt.figure(4)
    plt.subplot(3,1,1)
    plt.ylabel('c')
    plt.plot([0,T_final],[c_0_B,c_0_B],'--')
    plt.grid()
    plt.subplot(3,1,2)
    plt.ylabel('T')
    plt.plot([0,T_final],[T_0_B,T_0_B],'--')
    plt.grid()
    plt.subplot(3,1,3)
    plt.ylabel('Tc')
    plt.plot([0,T_final],[Tc_0_B,Tc_0_B],'--')
    plt.grid()
    plt.xlabel('t')


if __name__ == "__main__":
    run_demo()

