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

"""Tests for the pyfmi.simulation.assimulo module."""
import logging
import nose
import os
import numpy as N
import pylab as P
from scipy.io.matlab.mio import loadmat

from pymodelica.compiler import compile_jmu, compile_fmu
from pyfmi.fmi_deprecated import FMUModel2
from pyfmi.fmi import FMUModel, load_fmu, FMUException
from pyfmi.common.io import ResultDymolaTextual
from tests_jmodelica import testattr, get_files_path

try:
    from pyfmi.simulation.assimulo_interface import FMIODE
    from pyfmi.simulation.assimulo_interface import write_data
    from pyfmi.common.core import TrajectoryLinearInterpolation
    from assimulo.solvers import CVode
    from assimulo.solvers import IDA
except (NameError, ImportError):
    logging.warning('Could not load Assimulo module. Check pyfmi.check_packages()')

path_to_fmus = os.path.join(get_files_path(), 'FMUs')
path_to_fmus_me1 = os.path.join(path_to_fmus,"ME1.0")
path_to_fmus_cs1 = os.path.join(path_to_fmus,"CS1.0")
path_to_mos  = os.path.join(get_files_path(), 'Modelica')


def input_linear(t):
    if t < 0.5:
        return t
    elif t < 1.0:
        return 0.5
    elif t < 1.5:
        return t-0.5
    elif t < 2.0:
        return 2.5-t
    elif t < 2.5:
        return 0.5
    else:
        return 3.0-t
        
input_object = (["u"],input_linear)

class Test_When:
    @classmethod
    def setUpClass(cls):
        file_name = os.path.join(get_files_path(), 'Modelica', 'WhenTests.mo')
        
        compile_fmu("WhenTests.WhenTest5", file_name)
        
    @testattr(stddist = True)
    def test_sequence_of_pre(self):
        model = load_fmu("WhenTests_WhenTest5.fmu")
        
        res = model.simulate(final_time=3.5)
        
        assert res.final("nextTime") == 4.0
        assert res.final("nextTime2") == 3.0
        assert res.final("nextTime3") == 8.0
        
class Test_Sensitivities_FMI2:
    @classmethod
    def setUpClass(cls):
        file_name = os.path.join(get_files_path(), 'Modelica', 'Sensitivities.mo')
        compile_fmu("BasicSens1", file_name, version=2.0)
        compile_fmu("BasicSens2", file_name, version=2.0, compiler_options={"generate_ode_jacobian": True})
        compile_fmu("BasicSens1", file_name, version=2.0, compiler_options={"generate_ode_jacobian": True}, compile_to="BasicSens1Dir.fmu")
        
    @testattr(noncompliantfmi = True)
    def test_basicsens1(self):
        model = load_fmu("BasicSens1.fmu")
        
        opts = model.simulate_options()
        opts["sensitivities"] = ["d"]

        res = model.simulate(options=opts)
        nose.tools.assert_almost_equal(res.final('dx/dd'), 0.36789, 3)
        
        assert res.solver.statistics["nsensfcnfcns"] > 0
        
    @testattr(noncompliantfmi = True)
    def test_basicsens1dir(self):
        model = load_fmu("BasicSens1Dir.fmu")
        
        opts = model.simulate_options()
        opts["sensitivities"] = ["d"]

        res = model.simulate(options=opts)
        nose.tools.assert_almost_equal(res.final('dx/dd'), 0.36789, 3)
        
        assert res.solver.statistics["nsensfcnfcns"] > 0
        
    @testattr(stddist = True)
    def test_basicsens2(self):
        model = load_fmu("BasicSens2.fmu")
        
        opts = model.simulate_options()
        opts["sensitivities"] = ["d"]

        res = model.simulate(options=opts)
        nose.tools.assert_almost_equal(res.final('dx/dd'), 0.36789, 3)
        
        assert res.solver.statistics["nsensfcnfcns"] == 0
        

class Test_Time_Events:
    @classmethod
    def setUpClass(cls):
        """
        Compile the test model.
        """
        file_name = os.path.join(get_files_path(), 'Modelica', 'TimeEvents.mo')

        compile_fmu("TimeEvents.Basic1", file_name, compiler_options={"relational_time_events":True}, compiler_log_level="debug:log.txt")
        compile_fmu("TimeEvents.Basic2", file_name, compiler_options={"relational_time_events":True})
        compile_fmu("TimeEvents.Basic3", file_name, compiler_options={"relational_time_events":True})
        compile_fmu("TimeEvents.Basic4", file_name, compiler_options={"relational_time_events":True})
        
        compile_fmu("TimeEvents.Advanced1", file_name, compiler_options={"relational_time_events":True})
        compile_fmu("TimeEvents.Advanced2", file_name, compiler_options={"relational_time_events":True})
        compile_fmu("TimeEvents.Advanced3", file_name, compiler_options={"relational_time_events":True})
        compile_fmu("TimeEvents.Advanced4", file_name, compiler_options={"relational_time_events":True})
        
        compile_fmu("TimeEvents.Mixed1", file_name, compiler_options={"relational_time_events":True})
        compile_fmu("TimeEvents.TestSampling", file_name)
        compile_fmu("TimeEvents.TestSampling2", file_name)
    
    @testattr(stddist = True)
    def test_time_event_basic_1(self):
        model = load_fmu("TimeEvents_Basic1.fmu")
        model.initialize()
        ev = model.get_event_info()
        print ev.nextEventTime
        assert ev.nextEventTime == 1
        
    @testattr(stddist = True)
    def test_time_event_basic_2(self):
        model = load_fmu("TimeEvents_Basic2.fmu")
        model.initialize()
        ev = model.get_event_info()
        print ev.nextEventTime
        assert ev.nextEventTime == 2
        assert ev.nextEventTime == model.get("p")
        
    @testattr(stddist = True)
    def test_time_event_basic_3(self):
        model = load_fmu("TimeEvents_Basic3.fmu")
        model.initialize()
        ev = model.get_event_info()
        print ev.nextEventTime
        assert ev.nextEventTime == 1.5
        
    @testattr(stddist = True)
    def test_time_event_basic_4(self):
        model = load_fmu("TimeEvents_Basic4.fmu")
        
        model.initialize()
        ev = model.get_event_info()
        assert ev.upcomingTimeEvent == False
        assert model.get("x")== 2
        
        model.reset()
        model.time = 1
        model.initialize()
        
        assert ev.upcomingTimeEvent == False
        assert model.get("x") == 1
        
    @testattr(stddist = True)
    def test_time_event_advanced1(self):
        model = load_fmu("TimeEvents_Advanced1.fmu")
        model.initialize()
        ev = model.get_event_info()
        print ev.nextEventTime
        assert ev.nextEventTime == 0.5
        
        model.simulate(options={"initialize":False})
        
        print "i (should be 2): ", model.get("i") 
        assert model.get("i") == 2
        
    @testattr(stddist = True)
    def test_time_event_advanced2(self):
        model = load_fmu("TimeEvents_Advanced2.fmu")
        model.initialize()
        ev = model.get_event_info()
        print ev.nextEventTime
        assert ev.nextEventTime == 0.5
        
        model.simulate(options={"initialize":False})
        
        print "i (should be 2): ", model.get("i") 
        assert model.get("i") == 2
        
    @testattr(stddist = True)
    def test_time_event_advanced3(self):
        model = load_fmu("TimeEvents_Advanced3.fmu")
        model.initialize()
        ev = model.get_event_info()
        print ev.nextEventTime
        assert ev.nextEventTime == 0.5
        
        model.simulate(options={"initialize":False})
        
        print "i (should be 2): ", model.get("i") 
        print "j (should be 1): ", model.get("j") 
        assert model.get("i") == 2
        assert model.get("j") == 1
        
    @testattr(stddist = True)
    def test_time_event_advanced4(self):
        model = load_fmu("TimeEvents_Advanced4.fmu")
        model.initialize()
        ev = model.get_event_info()
        print ev.nextEventTime
        assert ev.nextEventTime == 0.5
        
        model.simulate(options={"initialize":False})
        
        print "i (should be 1): ", model.get("i") 
        print "j (should be 1): ", model.get("j") 
        assert model.get("i") == 1
        assert model.get("j") == 1
        
    @testattr(stddist = True)
    def test_time_event_mixed1(self):
        model = load_fmu("TimeEvents_Mixed1.fmu")
        model.initialize()
        ev = model.get_event_info()
        print ev.nextEventTime
        assert ev.nextEventTime == 1.5
        
        res = model.simulate(final_time=4, options={"initialize":False})
        
        print "x: ", res["x"]
        print "dx: ", res["der(x)"]
        
        assert res.solver.statistics["ntimeevents"] == 2
        assert res.solver.statistics["nstateevents"] == 2
        
    @testattr(stddist = True)
    def test_time_event_sampling(self):
        model = load_fmu("TimeEvents_TestSampling.fmu")
        model.initialize()
        res = model.simulate(0, 1e4, options={"initialize":False});
        assert res.solver.statistics["ntimeevents"] == 1e5
        
    @testattr(stddist = True)
    def test_time_event_sampling2(self):
        model = load_fmu("TimeEvents_TestSampling2.fmu")
        model.initialize()
        res = model.simulate(0,1e-6, options={"initialize":False});
        assert res.solver.statistics["ntimeevents"] == 1e4
        

class Test_Events:
    @classmethod
    def setUpClass(cls):
        """
        Compile the test model.
        """
        file_name = os.path.join(get_files_path(), 'Modelica', 'EventIter.mo')

        compile_fmu("EventIter.EventInfiniteIteration1", file_name)
        compile_fmu("EventIter.EventInfiniteIteration2", file_name)
        compile_fmu("EventIter.EventInfiniteIteration3", file_name)
        compile_fmu("EventIter.EnhancedEventIteration1", file_name)
        compile_fmu("EventIter.EnhancedEventIteration2", file_name)
        compile_fmu("EventIter.SingularSystem1", file_name)
        compile_fmu("EventIter.InitialPhasing1", file_name)
    
    @testattr(stddist = True)
    def test_event_infinite_iteration_1(self):
        model = load_fmu("EventIter_EventInfiniteIteration1.fmu")
        nose.tools.assert_raises(FMUException, model.initialize)
        
    @testattr(stddist = True)
    def test_event_infinite_iteration_2(self):
        model = load_fmu("EventIter_EventInfiniteIteration2.fmu")
        nose.tools.assert_raises(FMUException, model.initialize)
        
    @testattr(stddist = True)
    def test_event_infinite_iteration_3(self):
        model = load_fmu("EventIter_EventInfiniteIteration3.fmu")
        nose.tools.assert_raises(FMUException, model.simulate)
        
    @testattr(stddist = True)
    def test_singular_system_event_1(self):
        model = load_fmu("EventIter_SingularSystem1.fmu")
        
        #Check that we can initialize without error!
        model.initialize()
        
        nose.tools.assert_almost_equal(model.get("mode"), 0.0)
        nose.tools.assert_almost_equal(model.get("sa"), 0.0)
        
    @testattr(stddist = True)
    def test_enhanced_event_iteration_1(self):
        model = load_fmu("EventIter_EnhancedEventIteration1.fmu")
        res = model.simulate()
        
        nose.tools.assert_almost_equal(res["x[1]"][-1], 0)
        nose.tools.assert_almost_equal(res["x[2]"][-1], 0)
        nose.tools.assert_almost_equal(res["x[3]"][-1], 0)
        nose.tools.assert_almost_equal(res["x[4]"][-1], -0.406)
        nose.tools.assert_almost_equal(res["x[5]"][-1], -0.406)
        nose.tools.assert_almost_equal(res["x[6]"][-1], -0.406)
        nose.tools.assert_almost_equal(res["x[7]"][-1], 0.94)
        
    @testattr(stddist = True)
    def test_enhanced_event_iteration_2(self):
        model = load_fmu("EventIter_EnhancedEventIteration2.fmu")
        res = model.simulate(final_time=2.0)
        
        nose.tools.assert_almost_equal(res["y"][0], 1.0)
        nose.tools.assert_almost_equal(res["w"][0], 0.0)
        nose.tools.assert_almost_equal(res["x"][-1], 2.0)
        nose.tools.assert_almost_equal(res["y"][-1],1.58385,4)
        nose.tools.assert_almost_equal(res["z"][-1], 0.0)
        nose.tools.assert_almost_equal(res["w"][-1], 1.0)
    
    @testattr(stddist = True)
    def test_initial_phasing_1(self):
        model = load_fmu("EventIter_InitialPhasing1.fmu")
        res = model.simulate(final_time=0.1)
        nose.tools.assert_almost_equal(res["b1"][0], 0.0)
        nose.tools.assert_almost_equal(res["b2"][0], 1.0)

class Test_Relations:
    @classmethod
    def setUpClass(cls):
        """
        Compile the test model.
        """
        file_name = os.path.join(get_files_path(), 'Modelica', 'RelationTests.mo')

        compile_fmu("RelationTests.RelationLE", file_name)
        compile_fmu("RelationTests.RelationGE", file_name)
        compile_fmu("RelationTests.RelationLEInv", file_name)
        compile_fmu("RelationTests.RelationGEInv", file_name)
        compile_fmu("RelationTests.RelationLEInit", file_name)
        compile_fmu("RelationTests.RelationGEInit", file_name)
        compile_fmu("RelationTests.TestRelationalOp1", file_name)
        
    @testattr(stddist = True)
    def test_relation_le(self):
        model = load_fmu("RelationTests_RelationLE.fmu")
        opts = model.simulate_options()
        opts["CVode_options"]["maxh"] = 0.001
        res = model.simulate(final_time=3.5, input=input_object,options=opts)
        
        nose.tools.assert_almost_equal(N.interp(0.75,res["time"],res["y"]),0.5,places=2)
        nose.tools.assert_almost_equal(N.interp(2.25,res["time"],res["y"]),0.5,places=2)
        nose.tools.assert_not_almost_equal(N.interp(0.25,res["time"],res["y"]),0.5,places=2)
        nose.tools.assert_not_almost_equal(N.interp(2.75,res["time"],res["y"]),0.5,places=2)
        nose.tools.assert_not_almost_equal(N.interp(0.75,res["time"],res["x"]),0.5,places=2)
        nose.tools.assert_not_almost_equal(N.interp(2.25,res["time"],res["x"]),0.5,places=2)
        nose.tools.assert_almost_equal(N.interp(1.5,res["time"],res["y"]),0.5,places=2)
        
    @testattr(stddist = True)
    def test_relation_leinv(self):
        model = load_fmu("RelationTests_RelationLEInv.fmu")
        opts = model.simulate_options()
        opts["CVode_options"]["maxh"] = 0.001
        res = model.simulate(final_time=3.5, input=input_object,options=opts)
        
        nose.tools.assert_almost_equal(N.interp(0.75,res["time"],res["y"]),0.5,places=2)
        nose.tools.assert_almost_equal(N.interp(2.25,res["time"],res["y"]),0.5,places=2)
        nose.tools.assert_not_almost_equal(N.interp(0.25,res["time"],res["y"]),0.5,places=2)
        nose.tools.assert_not_almost_equal(N.interp(2.75,res["time"],res["y"]),0.5,places=2)
        nose.tools.assert_not_almost_equal(N.interp(0.75,res["time"],res["x"]),0.5,places=2)
        nose.tools.assert_not_almost_equal(N.interp(2.25,res["time"],res["x"]),0.5,places=2)
        nose.tools.assert_almost_equal(N.interp(1.5,res["time"],res["y"]),0.5,places=2)
        
    @testattr(stddist = True)
    def test_relation_ge(self):
        model = load_fmu("RelationTests_RelationGE.fmu")
        opts = model.simulate_options()
        opts["CVode_options"]["maxh"] = 0.001
        res = model.simulate(final_time=3.5, input=input_object,options=opts)
        
        nose.tools.assert_almost_equal(N.interp(0.75,res["time"],res["y"]),0.5,places=2)
        nose.tools.assert_almost_equal(N.interp(2.25,res["time"],res["y"]),0.5,places=2)
        nose.tools.assert_not_almost_equal(N.interp(0.25,res["time"],res["y"]),0.5,places=2)
        nose.tools.assert_not_almost_equal(N.interp(2.75,res["time"],res["y"]),0.5,places=2)
        nose.tools.assert_not_almost_equal(N.interp(0.75,res["time"],res["x"]),0.5,places=2)
        nose.tools.assert_not_almost_equal(N.interp(2.25,res["time"],res["x"]),0.5,places=2)
        nose.tools.assert_almost_equal(N.interp(1.5,res["time"],res["y"]),0.5,places=2)
        
    @testattr(stddist = True)
    def test_relation_geinv(self):
        model = load_fmu("RelationTests_RelationGEInv.fmu")
        opts = model.simulate_options()
        opts["CVode_options"]["maxh"] = 0.001
        res = model.simulate(final_time=3.5, input=input_object,options=opts)
        
        nose.tools.assert_almost_equal(N.interp(0.75,res["time"],res["y"]),0.5,places=2)
        nose.tools.assert_almost_equal(N.interp(2.25,res["time"],res["y"]),0.5,places=2)
        nose.tools.assert_not_almost_equal(N.interp(0.25,res["time"],res["y"]),0.5,places=2)
        nose.tools.assert_not_almost_equal(N.interp(2.75,res["time"],res["y"]),0.5,places=2)
        nose.tools.assert_not_almost_equal(N.interp(0.75,res["time"],res["x"]),0.5,places=2)
        nose.tools.assert_not_almost_equal(N.interp(2.25,res["time"],res["x"]),0.5,places=2)
        nose.tools.assert_almost_equal(N.interp(1.5,res["time"],res["y"]),0.5,places=2)
        
    @testattr(stddist = True)
    def test_relation_leinit(self):
        model = load_fmu("RelationTests_RelationLEInit.fmu")
        
        res = model.simulate(final_time=0.1)
        
        nose.tools.assert_almost_equal(res.initial("x"),1.0,places=3)
        nose.tools.assert_almost_equal(res.initial("y"),0.0,places=3)
        
    @testattr(stddist = True)
    def test_relation_geinit(self):
        model = load_fmu("RelationTests_RelationGEInit.fmu")
        
        res = model.simulate(final_time=0.1)
        
        nose.tools.assert_almost_equal(res.initial("x"),0.0,places=3)
        nose.tools.assert_almost_equal(res.initial("y"),1.0,places=3)

    @testattr(stddist = True)
    def test_relation_op_1(self):
        model = load_fmu("RelationTests_TestRelationalOp1.fmu")
        
        res = model.simulate(final_time=10)
        
        nose.tools.assert_almost_equal(N.interp(3.00,res["time"],res["der(v1)"]),1.0,places=3)
        nose.tools.assert_almost_equal(N.interp(3.40,res["time"],res["der(v1)"]),0.0,places=3)
        nose.tools.assert_almost_equal(N.interp(8.00,res["time"],res["der(v1)"]),0.0,places=3)
        nose.tools.assert_almost_equal(N.interp(8.25,res["time"],res["der(v1)"]),1.0,places=3)
        nose.tools.assert_almost_equal(N.interp(4.00,res["time"],res["der(v2)"]),1.0,places=3)
        nose.tools.assert_almost_equal(N.interp(4.20,res["time"],res["der(v2)"]),0.0,places=3)
        nose.tools.assert_almost_equal(N.interp(7.00,res["time"],res["der(v2)"]),0.0,places=3)
        nose.tools.assert_almost_equal(N.interp(7.20,res["time"],res["der(v2)"]),1.0,places=3)

class Test_NonLinear_Systems:
    
    @classmethod
    def setUpClass(cls):
        """
        Compile the test model.
        """
        file_name = os.path.join(get_files_path(), 'Modelica', 'NonLinear.mo')

        compile_fmu("NonLinear.NominalStart1", file_name)
        compile_fmu("NonLinear.NominalStart2", file_name)
        compile_fmu("NonLinear.NominalStart3", file_name)
        compile_fmu("NonLinear.NominalStart4", file_name)
        compile_fmu("NonLinear.NominalStart5", file_name)
        compile_fmu("NonLinear.NominalStart6", file_name)
        compile_fmu("NonLinear.DoubleRoot1", file_name)
        compile_fmu("NonLinear.NonLinear3", file_name)
        compile_fmu("NonLinear.NonLinear4", file_name)
        compile_fmu("NonLinear.ResidualHeuristicScaling1", file_name)
        compile_fmu("NonLinear.NonLinear5", file_name, compiler_options={"generate_ode_jacobian": True})
        compile_fmu("NonLinear.EventIteration1", file_name)
    
    @testattr(stddist = True)
    def test_Brent_AD(self):
        
        model = load_fmu("NonLinear_NonLinear5.fmu", log_level=6)
        model.set("_log_level", 8)
        
        model.initialize()
        
        def get_history(filename):
            import re
            data = [[],[]]
            with open(filename, 'r') as f:
                line = f.readline()
                while line:
                    if line.find("Iteration variable") != -1:
                        iv = re.search('<value name="ivs">(.*)</value>, Function', line).group(1).strip()
                        df = re.search('<value name="df">(.*)</value>, Delta', line).group(1).strip()
                        data[0].append(float(iv))
                        data[1].append(float(df))
                    line = f.readline()
            return data[0], data[1]
            
        ivs,df = get_history("NonLinear_NonLinear5_log.txt")

        fprime = lambda y: -200*y;

        for i,iv in enumerate(ivs):
            nose.tools.assert_almost_equal(fprime(iv) ,df[i], places=12)  
            
    @testattr(stddist = True)
    def test_Brent_double_root1(self):
        def run_model(init):
            model = load_fmu("NonLinear_DoubleRoot1.fmu")
            model.set("_use_Brent_in_1d", True)
            model.set("x", init)
            model.initialize()
            return model.get("x")
        
        sol_pos = N.sqrt(1e-7)+1.5
        sol_neg =-N.sqrt(1e-7)+1.5

        nose.tools.assert_almost_equal(run_model(sol_pos+1e-16) ,sol_pos)
        nose.tools.assert_almost_equal(run_model(sol_pos-1e-16) ,sol_pos)
        nose.tools.assert_almost_equal(run_model(sol_pos+1e-14) ,sol_pos)
        nose.tools.assert_almost_equal(run_model(sol_pos-1e-14) ,sol_pos)
        
        nose.tools.assert_almost_equal(run_model(sol_neg+1e-16) ,sol_neg)
        nose.tools.assert_almost_equal(run_model(sol_neg-1e-16) ,sol_neg)
        nose.tools.assert_almost_equal(run_model(sol_neg+1e-14) ,sol_neg)
        nose.tools.assert_almost_equal(run_model(sol_neg-1e-14) ,sol_neg)
        
    @testattr(stddist = True)
    def test_Brent_close_to_root(self):
        model = load_fmu("NonLinear_NonLinear3.fmu")
        model.set("_use_Brent_in_1d", True)
        
        model.set("i",-9.9760004108556469E-03)
        model.initialize()
        
        nose.tools.assert_almost_equal(model.get("i"),-9.9760004108556469E-03)
        
    @testattr(stddist = True)
    def test_Brent_close_to_root(self):
        model = load_fmu("NonLinear_NonLinear4.fmu")
        model.set("_use_Brent_in_1d", True)
        
        scale = model.get("scale")
        i = -9.9760004108556469E-03*scale
        model.set("i",i)
        model.initialize()
        nose.tools.assert_almost_equal(model.get("i"),i)
        
        model.reset()
        
        model.set("i", i+i*1e-15)
        model.initialize()
        nose.tools.assert_almost_equal(model.get("i"),i)
        
        model.reset()
        
        model.set("i", i-i*1e-15)
        model.initialize()
        nose.tools.assert_almost_equal(model.get("i"),i)
        
        
    
    @testattr(stddist = True)
    def test_nominals_fallback_1(self):
        model = load_fmu("NonLinear_NominalStart1.fmu")
        model.set("_nle_solver_use_nominals_as_fallback", True)
        model.initialize()
    
    @testattr(stddist = True)
    def test_nominals_fallback_2(self):
        model = load_fmu("NonLinear_NominalStart1.fmu")
        model.set("_nle_solver_use_nominals_as_fallback", False)
        nose.tools.assert_raises(FMUException, model.initialize)
        
    @testattr(stddist = True)
    def test_nominals_fallback_3(self):
        model = load_fmu("NonLinear_NominalStart2.fmu")
        model.set("_nle_solver_use_nominals_as_fallback", True)
        nose.tools.assert_raises(FMUException, model.initialize)
        
    @testattr(stddist = True)
    def test_nominals_fallback_4(self):
        model = load_fmu("NonLinear_NominalStart4.fmu")
        model.set("_use_Brent_in_1d", False)
        model.set("_nle_solver_use_nominals_as_fallback", True)
        nose.tools.assert_raises(FMUException, model.initialize)

    @testattr(stddist = True)
    def test_nominals_fallback_5(self):
        model = load_fmu("NonLinear_NominalStart5.fmu")
        model.set("_use_Brent_in_1d", False)
        model.set("_nle_solver_use_nominals_as_fallback", True)
        nose.tools.assert_raises(FMUException, model.initialize)
        
    @testattr(stddist = True)
    def test_nominals_fallback_6(self):
        model = load_fmu("NonLinear_NominalStart3.fmu")
        model.set("_use_Brent_in_1d", False)
        model.set("_nle_solver_use_nominals_as_fallback", True)
        model.set('_nle_jacobian_update_mode', 0)
        model.initialize()
        
        nose.tools.assert_almost_equal(model.get("x") ,2.76929235)
        
    @testattr(stddist = True)
    def test_nominals_fallback_7(self):
        model = load_fmu("NonLinear_NominalStart6.fmu")
        model.set("_nle_solver_use_nominals_as_fallback", True)
        model.initialize()
        
        nose.tools.assert_almost_equal(model.get("x"), 0.680716920494911)
        nose.tools.assert_almost_equal(model.get("y"), 0.0)
        
    @testattr(stddist = True)
    def test_residual_scaling_heuristics(self):
        model = load_fmu("NonLinear_ResidualHeuristicScaling1.fmu")
        model.set("_use_Brent_in_1d", False)
        model.initialize()
        nose.tools.assert_almost_equal(model.get('state_a_p'), 17.78200351)
        
    @testattr(stddist = True)
    def test_event_iternation_inf_check_warmup(self):
        # Test where event inf check cannot only look at the switches but need
        # to look at the iteration variables too. Generally this is needed for
        # models with systems that have many solutions and bad start values. In
        # this model the variable iter_var_1 will go from 300 to ca 874 and then
        # if it don't get stuck in inf check it will go to 872.98062403
        model = load_fmu("NonLinear_EventIteration1.fmu")
        model.initialize()
        nose.tools.assert_almost_equal(model.get('iter_var_1'), 872.98062403)
    
class Test_Singular_Systems:
    
    @classmethod
    def setUpClass(cls):
        """
        Compile the test model.
        """
        file_name = os.path.join(get_files_path(), 'Modelica', 'Singular.mo')

        compile_fmu("Singular.LinearInf", file_name)
        compile_fmu("Singular.Linear2", file_name)
        compile_fmu("Singular.LinearEvent1", file_name)
        compile_fmu("Singular.LinearEvent2", file_name)
        compile_fmu("Singular.NonLinear1", file_name)
        compile_fmu("Singular.NonLinear4", file_name)
        compile_fmu("Singular.NonLinear5", file_name)
        compile_fmu("Singular.NoMinimumNormSolution", file_name)
    
    @testattr(stddist = True)
    def test_linear_event_1(self):
        model = load_fmu("Singular_LinearEvent1.fmu", log_level=3)
        model.set("_log_level", 3)
        
        res = model.simulate(final_time=2)
        nose.tools.assert_almost_equal(res.final('y') ,1.000000000)
        
    @testattr(stddist = True)
    def test_linear_event_2(self):
        model = load_fmu("Singular_LinearEvent2.fmu", log_level=3)
        model.set("_log_level", 3)
        
        res = model.simulate(final_time=4)
        nose.tools.assert_almost_equal(res.final('y') ,1.000000000)
        nose.tools.assert_almost_equal(res.final('w') ,2.000000000)
    
    @testattr(stddist = True)
    def test_linear_inf_1(self):
        
        model = load_fmu("Singular_LinearInf.fmu", log_level=6)
        model.set("_log_level", 6)
        
        model.set("a22", N.inf)
        nose.tools.assert_raises(FMUException, model.initialize)
        
    @testattr(stddist = True)
    def test_linear_inf_2(self):
        
        model = load_fmu("Singular_LinearInf.fmu", log_level=6)
        model.set("_log_level", 6)
        
        model.set("a33", 0)
        model.set("a22", N.inf)
        nose.tools.assert_raises(FMUException, model.initialize)
        
    @testattr(stddist = True)
    def test_linear_inf_3(self):
        
        model = load_fmu("Singular_LinearInf.fmu", log_level=6)
        model.set("_log_level", 6)
        
        model.set("b[1]", N.inf)
        nose.tools.assert_raises(FMUException, model.initialize)
        
    @testattr(stddist = True)
    def test_nonlinear_1(self):
        
        model = load_fmu("Singular_NonLinear1.fmu")
        model.set("a33", 0)
        model.set("b[3]", 0)
        
        model.initialize()
        
        nose.tools.assert_almost_equal(model.get("x") ,1.000000000)
        nose.tools.assert_almost_equal(model.get("y") ,2.000000000)
        nose.tools.assert_almost_equal(model.get("z") ,0.000000000)
        
    @testattr(stddist = True)
    def test_nonlinear_2(self):
        
        model = load_fmu("Singular_NonLinear1.fmu")
        model.set("a33", 0)
        model.set("b[3]", 3)
        
        nose.tools.assert_raises(FMUException, model.initialize)
        
    @testattr(stddist = True)
    def test_nonlinear_3(self):
        
        model = load_fmu("Singular_NonLinear1.fmu")
        model.set("a33", 0)
        model.set("a22", 1e-5)
        model.set("b[3]", 0)
        
        model.initialize()
        
        nose.tools.assert_almost_equal(model.get("x") ,1.000000000)
        nose.tools.assert_almost_equal(model.get("y") ,200000.0000)
        nose.tools.assert_almost_equal(model.get("z") ,0.000000000)
        
    @testattr(stddist = True)
    def test_nonlinear_4(self):
        
        model = load_fmu("Singular_NonLinear1.fmu")
        model.set("a33", 0)
        model.set("a22", 1e10)
        model.set("b[3]", 0)
        
        model.initialize()
        
        nose.tools.assert_almost_equal(model.get("x") ,1.000000000)
        nose.tools.assert_almost_equal(model.get("y") ,2e-10)
        nose.tools.assert_almost_equal(model.get("z") ,0.000000000)
        
    @testattr(stddist = True)
    def test_nonlinear_6(self):
        
        model = load_fmu("Singular_NonLinear5.fmu")
        
        model.initialize()
        
        nose.tools.assert_almost_equal(model.get("x") ,5)
        nose.tools.assert_almost_equal(model.get("y") ,0)
        nose.tools.assert_almost_equal(model.get("z") ,0.000000000)
    
    @testattr(stddist = True)
    def test_nonlinear_5(self):
        model = load_fmu("Singular_NonLinear4.fmu")

        model.set("b[3]", 0)
        model.set("a31", 1)
        model.set("a32", -0.5)

        res = model.simulate()
        
        nose.tools.assert_almost_equal(res["z"][0] ,0.000000000)
        nose.tools.assert_almost_equal(res["z"][-1] ,-1.000000000)
    
    @testattr(stddist = True)
    def test_no_valid_minimum_norm_sol(self):
        model = load_fmu("Singular_NoMinimumNormSolution.fmu", log_level=3)
        model.set("_log_level", 3)
        model.set_log_level(3)
        nose.tools.assert_raises(FMUException, model.initialize)

class Test_FMI_ODE_CS_2:
    @classmethod
    def setUpClass(cls):
        """
        Compile the test model.
        """
        file_name = os.path.join(get_files_path(), 'Modelica', 'noState.mo')
        file_name_in = os.path.join(get_files_path(), 'Modelica', 'InputTests.mo')
        file_name_linear = os.path.join(get_files_path(), 'Modelica', 'Linear.mo')
        file_name_time_event = os.path.join(get_files_path(), 'Modelica', 'TimeEvents.mo')

        _in3_name = compile_fmu("LinearTest.Linear1", file_name_linear, version=2.0, target="cs")
        _t1_name = compile_fmu("TimeEvents.Basic5", file_name_time_event, version=2.0, target="cs")
        _t1_name = compile_fmu("TimeEvents.Advanced5", file_name_time_event, version=2.0, target="cs")
        
    @testattr(stddist = True)
    def test_updated_values_in_result(self):
        model = load_fmu("LinearTest_Linear1.fmu")
        opts = model.simulate_options()
        
        res = model.simulate(final_time=1,options=opts)
        
        for i in range(len(res["der(x)"])):
            assert res["der(x)"][i] == 0.0
    
    @testattr(stddist = True)
    def test_time_event_basic_5(self):
        model = load_fmu("TimeEvents_Basic5.fmu")
        opts = model.simulate_options()
        
        res = model.simulate(final_time=1,options=opts)
        
        assert res["der(x)"][-1] == -1.0
        
    @testattr(stddist = True)
    def test_time_event_at_do_step_end(self):
        model = load_fmu("TimeEvents_Advanced5.fmu")
        opts = model.simulate_options()
        opts["ncp"] = 100
        res = model.simulate(final_time=1,options=opts)
        
        nose.tools.assert_almost_equal(res.final("x"), 3.89, 2)

class Test_FMI_ODE_CS:
    @classmethod
    def setUpClass(cls):
        """
        Compile the test model.
        """
        file_name = os.path.join(get_files_path(), 'Modelica', 'noState.mo')
        file_name_in = os.path.join(get_files_path(), 'Modelica', 'InputTests.mo')
        file_name_linear = os.path.join(get_files_path(), 'Modelica', 'Linear.mo')
        file_name_time_event = os.path.join(get_files_path(), 'Modelica', 'TimeEvents.mo')

        _in3_name = compile_fmu("LinearTest.Linear1", file_name_linear, target="cs")
        _t1_name = compile_fmu("TimeEvents.Advanced5", file_name_time_event, target="cs")
       
    @testattr(stddist = True)
    def test_time_event_at_do_step_end(self):
        model = load_fmu("TimeEvents_Advanced5.fmu")
        opts = model.simulate_options()
        opts["ncp"] = 100
        res = model.simulate(final_time=1,options=opts)
        
        nose.tools.assert_almost_equal(res.final("x"), 3.89, 2)
            
    @testattr(stddist = True)
    def test_updated_values_in_result(self):
        model = load_fmu("LinearTest_Linear1.fmu")
        opts = model.simulate_options()
        
        res = model.simulate(final_time=1,options=opts)
        
        for i in range(len(res["der(x)"])):
            assert res["der(x)"][i] == 0.0

class Test_FMI_ODE:
    """
    This class tests pyfmi.simulation.assimulo.FMIODE and together
    with Assimulo. Requires that Assimulo is installed.
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Compile the test model.
        """
        file_name = os.path.join(get_files_path(), 'Modelica', 'noState.mo')
        file_name_in = os.path.join(get_files_path(), 'Modelica', 'InputTests.mo')
        file_name_linear = os.path.join(get_files_path(), 'Modelica', 'Linear.mo')

        _ex1_name = compile_fmu("NoState.Example1", file_name)
        _ex2_name = compile_fmu("NoState.Example2", file_name)
        _in1_name = compile_fmu("Inputs.SimpleInput", file_name_in)
        _in3_name = compile_fmu("Inputs.SimpleInput3", file_name_in)
        _cc_name = compile_fmu("Modelica.Mechanics.Rotational.Examples.CoupledClutches")
        _in3_name = compile_fmu("LinearTest.Linear1", file_name_linear)
        
    def setUp(self):
        """
        Load the test model.
        """
        self._bounce  = load_fmu('bouncingBall.fmu',path_to_fmus_me1)
        self._dq = load_fmu('dq.fmu',path_to_fmus_me1)
        self._bounce.initialize()
        self._dq.initialize()
        self._bounceSim = FMIODE(self._bounce)
        self._dqSim     = FMIODE(self._dq)
        
    @testattr(stddist = True)
    def test_updated_values_in_result(self):
        model = load_fmu("LinearTest_Linear1.fmu")
        opts = model.simulate_options()
        opts["solver"] = "CVode"
        
        res = model.simulate(final_time=1,options=opts)
        
        for i in range(len(res["der(x)"])):
            assert res["der(x)"][i] == 0.0
    
    @testattr(stddist = True)
    def test_cc_with_cvode(self):
        model = load_fmu("Modelica_Mechanics_Rotational_Examples_CoupledClutches.fmu")
        opts = model.simulate_options()
        opts["solver"] = "CVode"
        opts["CVode_options"]["rtol"] = 1e-7
        
        res = model.simulate(final_time=1.5,options=opts)
        
        assert (N.abs(res.final("J1.w") - 3.2450903041811698)) < 1e-4
        
    @testattr(stddist = True)
    def test_no_result(self):
        opts = self._bounce.simulate_options()
        opts["result_handling"] = "none"
        opts["initialize"] = False
        res = self._bounce.simulate(options=opts)
        
        nose.tools.assert_raises(Exception,res._get_result_data)
    
    @testattr(stddist = True)
    def test_reset_internal_variables(self):
        model = load_fmu("Inputs_SimpleInput.fmu")
        
        model.initialize()
        
        model.set("u",2)
        model.time = 1
        assert model.get("u") == 2.0
        
        model.time = 0.5
        assert model.get("u") == 2.0
        
    @testattr(stddist = True)
    def test_reset_internal_variables2(self):
        model = load_fmu("Inputs_SimpleInput3.fmu")
        
        model.initialize()
        
        model.set("p",2)
        model.time = 1
        assert model.get("p") == 2.0
        
        model.time = 0.5
        assert model.get("p") == 2.0
        
    @testattr(stddist = True)
    def test_cc_with_radau(self):
        model = load_fmu("Modelica_Mechanics_Rotational_Examples_CoupledClutches.fmu")
        opts = model.simulate_options()
        opts["solver"] = "Radau5ODE"
        
        res = model.simulate(final_time=1.5,options=opts)
        
        assert (N.abs(res.final("J1.w") - 3.2450903041811698)) < 1e-3
    
    @testattr(stddist = True)
    def test_cc_with_dopri(self):
        model = load_fmu("Modelica_Mechanics_Rotational_Examples_CoupledClutches.fmu")
        opts = model.simulate_options()
        opts["solver"] = "Dopri5"
        
        res = model.simulate(final_time=1.5,options=opts)
        
        assert (N.abs(res.final("J1.w") - 3.2450903041811698)) < 1e-3
        
    @testattr(stddist = True)
    def test_cc_with_lsodar(self):
        model = load_fmu("Modelica_Mechanics_Rotational_Examples_CoupledClutches.fmu")
        opts = model.simulate_options()
        opts["solver"] = "LSODAR"
        opts["LSODAR_options"]["rtol"] = 1e-6
        
        res = model.simulate(final_time=1.5,options=opts)
        
        assert (N.abs(res.final("J1.w") - 3.2450903041811698)) < 1e-3
        
    @testattr(stddist = True)
    def test_cc_with_rodas(self):
        model = load_fmu("Modelica_Mechanics_Rotational_Examples_CoupledClutches.fmu")
        opts = model.simulate_options()
        opts["solver"] = "RodasODE"
        opts["RodasODE_options"]["rtol"] = 1e-6
        
        res = model.simulate(final_time=1.5,options=opts)
        
        assert (N.abs(res.final("J1.w") - 3.2450903041811698)) < 1e-3
        
    @testattr(stddist = True)
    def test_cc_with_impliciteuler(self):
        model = load_fmu("Modelica_Mechanics_Rotational_Examples_CoupledClutches.fmu")
        opts = model.simulate_options()
        opts["solver"] = "ImplicitEuler"
        opts["ImplicitEuler_options"]["rtol"] = 1e-8
        opts["ImplicitEuler_options"]["atol"] = 1e-8
        opts["ImplicitEuler_options"]["h"] = 0.001
        
        res = model.simulate(final_time=1.5,options=opts)
        assert (N.abs(res.final("J1.w") - 3.2450903041811698)) < 1e-2
        
    @testattr(stddist = True)
    def test_cc_with_expliciteuler(self):
        model = load_fmu("Modelica_Mechanics_Rotational_Examples_CoupledClutches.fmu")
        opts = model.simulate_options()
        opts["solver"] = "ExplicitEuler"
        opts["ExplicitEuler_options"]["h"] = 0.001

        res = model.simulate(final_time=1.5,options=opts)
        assert (N.abs(res.final("J1.w") - 3.2450903041811698)) < 1e-2
        
    @testattr(stddist = True)
    def test_no_state1(self):
        """
        Tests simulation when there is no state in the model (Example1).
        """
        model = load_fmu("NoState_Example1.fmu")
        
        res = model.simulate(final_time=10)
        
        nose.tools.assert_almost_equal(res.initial('x') ,1.000000000)
        nose.tools.assert_almost_equal(res.final('x'),-2.000000000)
        nose.tools.assert_almost_equal(res.initial('y') ,-1.000000000)
        nose.tools.assert_almost_equal(res.final('y'),-1.000000000)
        nose.tools.assert_almost_equal(res.initial('z') ,1.000000000)
        nose.tools.assert_almost_equal(res.final('z'),4.000000000)
        
    @testattr(stddist = True)
    def test_no_state2(self):
        """
        Tests simulation when there is no state in the model (Example2).
        """
        model = load_fmu("NoState_Example2.fmu")
        
        res = model.simulate(final_time=10)
        
        nose.tools.assert_almost_equal(res.initial('x') ,-1.000000000)
        nose.tools.assert_almost_equal(res.final('x'),-1.000000000)
    
    @testattr(stddist = True)
    def test_result_name_file(self):
        """
        Tests user naming of result file (FMIODE).
        """
        res = self._dq.simulate(options={"initialize":False})
        
        #Default name
        assert res.result_file == "dq_result.txt"
        assert os.path.exists(res.result_file)
        
        res = self._bounce.simulate(options={"result_file_name":
                                    "bouncingBallt_result_test.txt",
                                             "initialize":False})
                                    
        #User defined name
        assert res.result_file == "bouncingBallt_result_test.txt"
        assert os.path.exists(res.result_file)
        
    @testattr(stddist = True)
    def test_result_enumeration(self):
        """
        Tests that enumerations are written to the result
        """
        file_name = os.path.join(get_files_path(), 'Modelica', 'Friction.mo')

        enum_name = compile_fmu("Friction2", file_name)
        
        model = load_fmu(enum_name)
        
        data_type = model.get_variable_data_type("mode")
        
        from pyfmi.fmi import FMI_ENUMERATION
        assert data_type == FMI_ENUMERATION
        
        opts = model.simulate_options()
        
        res = model.simulate(options=opts)
        res["mode"] #Check that the enumeration variable is in the dict, otherwise exception
        
        model.reset()
        opts["result_handling"] = "memory"
        
        res = model.simulate(options=opts)
        res["mode"] #Check that the enumeration variable is in the dict, otherwise exception
        
        from pyfmi.common.io import ResultHandlerCSV
        model.reset()
        opts["result_handling"] = "custom"
        opts["result_handler"] = ResultHandlerCSV(model)
        
        res = model.simulate(options=opts)
        res["mode"] #Check that the enumeration variable is in the dict, otherwise exception
        
    @testattr(stddist = True)
    def test_result_enumeration_2(self):
        file_name = os.path.join(get_files_path(), 'Modelica', 'Enumerations.mo')

        enum_name = compile_fmu("Enumerations.Enumeration2", file_name)
        model = load_fmu(enum_name)
        
        opts = model.simulate_options()
        
        res = model.simulate(options=opts)
        assert res["one"][0] == 1
        assert res["one"][-1] == 3
        assert res["two"][0] == 2
        assert res["two"][-1] == 2
        assert res["three"][0] == 3
        assert res["three"][-1] == 3
        
        model.reset()
        opts["result_handling"] = "memory"
        
        res = model.simulate(options=opts)
        
        assert res["one"][0] == 1
        assert res["one"][-1] == 3
        assert res["two"][0] == 2
        assert res["two"][-1] == 2
        assert res["three"][0] == 3
        assert res["three"][-1] == 3
        
        from pyfmi.common.io import ResultHandlerCSV
        model.reset()
        opts["result_handling"] = "custom"
        opts["result_handler"] = ResultHandlerCSV(model)
        
        res = model.simulate(options=opts)
        
        assert res["one"][0] == 1
        assert res["one"][-1] == 3
        assert res["two"][0] == 2
        assert res["two"][-1] == 2
        assert res["three"][0] == 3
        assert res["three"][-1] == 3
    
    @testattr(stddist = True)
    def test_init(self):
        """
        This tests the functionality of the method init. 
        """
        assert self._bounceSim._f_nbr == 2
        assert self._bounceSim._g_nbr == 1
        assert self._bounceSim.state_events == self._bounceSim.g
        assert self._bounceSim.y0[0] == 1.0
        assert self._bounceSim.y0[1] == 0.0
        assert self._dqSim._f_nbr == 1
        assert self._dqSim._g_nbr == 0
        try:
            self._dqSim.state_events
            raise FMUException('')
        except AttributeError:
            pass
        
        #sol = self._bounceSim._sol_real
        
        #nose.tools.assert_almost_equal(sol[0][0],1.000000000)
        #nose.tools.assert_almost_equal(sol[0][1],0.000000000)
        #nose.tools.assert_almost_equal(sol[0][2],0.000000000)
        #nose.tools.assert_almost_equal(sol[0][3],-9.81000000)
        
    @testattr(stddist = True)
    def test_f(self):
        """
        This tests the functionality of the rhs.
        """
        t = 1.0
        y = N.array([1.0,1.0])
        
        rhs = self._bounceSim.rhs(t,y)
        
        nose.tools.assert_almost_equal(rhs[0],1.00000000)
        nose.tools.assert_almost_equal(rhs[1],-9.8100000)

    
    @testattr(stddist = True)
    def test_g(self):
        """
        This tests the functionality of the event indicators.
        """
        t = 1.0
        y = N.array([1.0,1.0])
        
        event = self._bounceSim.g(t,y,None)
        
        nose.tools.assert_almost_equal(event[0],1.00000000)
        
        y = N.array([0.5,1.0])
        event = self._bounceSim.g(t,y,None)
        
        nose.tools.assert_almost_equal(event[0],0.50000000)

        
    @testattr(stddist = True)
    def test_t(self):
        """
        This tests the functionality of the time events.
        """
        t = 1.0
        y = N.array([1.0,1.0])
        
        time = self._bounceSim.t(t,y,None)
        
        assert time == None
        #Further testing of the time event function is needed.
        
        
    @testattr(stddist = True)
    def test_handle_event(self):
        """
        This tests the functionality of the method handle_event.
        """
        y = N.array([1.,1.])
        self._bounceSim._model.continuous_states = y
        solver = lambda x:1
        solver.rtol = 1.e-4
        solver.t = 1.0
        solver.y = y
        solver.y_sol = [y]
        solver.report_continuously = False
        
        self._bounceSim.initialize(solver)
        self._bounceSim.handle_event(solver, None)

        nose.tools.assert_almost_equal(solver.y[0],1.00000000)
        nose.tools.assert_almost_equal(solver.y[1],-0.70000000)
        
        #Further testing of the handle_event function is needed.
    
    @testattr(stddist = True)
    def test_completed_step(self):
        """
        This tests the functionality of the method completed_step.
        """
        y = N.array([1.,1.])
        solver = lambda x:1
        solver.t = 1.0
        solver.y = y
        assert self._bounceSim.step_events(solver) == 0
        #Further testing of the completed step function is needed.
        
    @testattr(windows = True)
    def test_simulation_completed_step_cvode(self):
        """
        This tests a simulation of a Pendulum with dynamic state selection.
        """
        model = load_fmu('Pendulum_0Dynamic.fmu', path_to_fmus_me1)
        
        opts = model.simulate_options()
        opts["CVode_options"]["atol"] = 1e-8
        opts["CVode_options"]["rtol"] = 1e-8
        res = model.simulate(final_time=10, options=opts)
    
        nose.tools.assert_almost_equal(res.initial('x'), 1.000000, 4)
        nose.tools.assert_almost_equal(res.initial('y'), 0.000000, 4)
        nose.tools.assert_almost_equal(res.final('x'), 0.25370773767354998, 4)
        nose.tools.assert_almost_equal(res.final('y'), -0.96728092291979395, 4)
        
        model = FMUModel('Pendulum_0Dynamic.fmu', path_to_fmus_me1)
        
        res = model.simulate(final_time=10, options={'ncp':1000})
    
        nose.tools.assert_almost_equal(res.initial('x'), 1.000000, 4)
        nose.tools.assert_almost_equal(res.initial('y'), 0.000000, 4)
        
    @testattr(windows = True)
    def test_simulation_completed_step_radau(self):
        model = load_fmu('Pendulum_0Dynamic.fmu', path_to_fmus_me1)
        
        opts = model.simulate_options()
        opts["solver"] = "Radau5ODE"
        res = model.simulate(final_time=10, options=opts)
    
        assert N.abs(res.final('y')+0.956993467) < 1e-2
        assert N.abs(res.final('x')-0.290109468) < 1e-1
        
        model = FMUModel('Pendulum_0Dynamic.fmu', path_to_fmus_me1)
        
        opts["ncp"] = 1000
        res = model.simulate(final_time=10, options=opts)

        assert N.abs(res.final('y')+0.956993467) < 1e-2
        assert N.abs(res.final('x')-0.290109468) < 1e-1
        
    @testattr(windows = True)
    def test_simulation_completed_step_dopri(self):
        model = load_fmu('Pendulum_0Dynamic.fmu', path_to_fmus_me1)
        
        opts = model.simulate_options()
        opts["solver"] = "Dopri5"
        res = model.simulate(final_time=10, options=opts)
    
        assert N.abs(res.final('y')+0.956993467) < 1e-1
        assert N.abs(res.final('x')-0.290109468) < 1e-1
        
        model = FMUModel('Pendulum_0Dynamic.fmu', path_to_fmus_me1)
        
        opts["ncp"] = 1000
        res = model.simulate(final_time=10, options=opts)

        assert N.abs(res.final('y')+0.956993467) < 1e-1
        assert N.abs(res.final('x')-0.290109468) < 1e-1
    
    @testattr(windows = True)
    def test_simulation_completed_step_rodas(self):
        model = load_fmu('Pendulum_0Dynamic.fmu', path_to_fmus_me1)
        
        opts = model.simulate_options()
        opts["solver"] = "RodasODE"
        res = model.simulate(final_time=10, options=opts)
    
        assert N.abs(res.final('y')+0.956993467) < 1e-1
        assert N.abs(res.final('x')-0.290109468) < 1e-1
        
        model = FMUModel('Pendulum_0Dynamic.fmu', path_to_fmus_me1)
        
        opts["ncp"] = 1000
        res = model.simulate(final_time=10, options=opts)

        assert N.abs(res.final('y')+0.956993467) < 1e-1
        assert N.abs(res.final('x')-0.290109468) < 1e-1
        
    @testattr(windows = True)
    def test_simulation_completed_step_lsodar(self):
        model = load_fmu('Pendulum_0Dynamic.fmu', path_to_fmus_me1)
        
        opts = model.simulate_options()
        opts["solver"] = "LSODAR"
        res = model.simulate(final_time=10, options=opts)
    
        assert N.abs(res.final('y')+0.956993467) < 1e-1
        assert N.abs(res.final('x')-0.290109468) < 1e-1
        
        model = FMUModel('Pendulum_0Dynamic.fmu', path_to_fmus_me1)
        
        opts["ncp"] = 1000
        res = model.simulate(final_time=10, options=opts)

        assert N.abs(res.final('y')+0.956993467) < 1e-1
        assert N.abs(res.final('x')-0.290109468) < 1e-1
    
    @testattr(windows = True)
    def test_terminate_simulation(self):
        """
        This tests a simulation with an event of terminate simulation.
        """
        model = load_fmu('Robot.fmu', path_to_fmus_me1)
        
        res = model.simulate(final_time=2.0)
        solver = res.solver
        
        nose.tools.assert_almost_equal(solver.t, 1.856045, places=3)    
        
    @testattr(windows = True)
    def test_typeDefinitions_simulation(self):
        """
        This tests a FMU with typeDefinitions including StringType and BooleanType
        """
        model = load_fmu('Robot_Dym74FD01.fmu', path_to_fmus_me1)
        
        res = model.simulate(final_time=2.0)
        solver = res.solver
        
        nose.tools.assert_almost_equal(solver.t, 1.856045, places=3)        

    @testattr(noncompliantfmi = True)
    def test_assert_raises_sensitivity_parameters(self):
        """
        This tests that an exception is raised if a sensitivity calculation
        is to be perfomed and the parameters are not contained in the model.
        """
        fmu_name = compile_fmu('EventIter.EventMiddleIter', os.path.join(path_to_mos,'EventIter.mo'))

        model = load_fmu(fmu_name)
        opts = model.simulate_options()
        opts["sensitivities"] = ["hej", "hopp"]
        
        nose.tools.assert_raises(FMUException,model.simulate,0,1,(),'AssimuloFMIAlg',opts)
        
    @testattr(windows = True)
    def test_assert_raises_sensitivity_without_jmodelica(self):
        model = load_fmu("Modelica_Mechanics_Rotational_Examples_CoupledClutches_ME.fmu", path_to_fmus_me1)
        opts = model.simulate_options()
        opts["sensitivities"] = ["J1.w"]
        
        nose.tools.assert_raises(Exception,model.simulate,0,1,(),'AssimuloFMIAlg',opts)

    @testattr(stddist = True)
    def test_event_iteration(self):
        """
        This tests FMUs with event iteration (JModelica.org).
        """
        fmu_name = compile_fmu('EventIter.EventMiddleIter', os.path.join(path_to_mos,'EventIter.mo'))

        model = load_fmu(fmu_name)

        sim_res = model.simulate(final_time=10)

        nose.tools.assert_almost_equal(sim_res.initial('x'), 2.00000, 4)
        nose.tools.assert_almost_equal(sim_res.final('x'), 10.000000, 4)
        nose.tools.assert_almost_equal(sim_res.final('y'), 3.0000000, 4)
        nose.tools.assert_almost_equal(sim_res.final('z'), 2.0000000, 4)
        
        fmu_name = compile_fmu('EventIter.EventStartIter', os.path.join(path_to_mos,'EventIter.mo'))
        
        model = FMUModel(fmu_name)

        sim_res = model.simulate(final_time=10)

        nose.tools.assert_almost_equal(sim_res.initial('x'), 1.00000, 4)
        nose.tools.assert_almost_equal(sim_res.initial('y'), -1.00000, 4)
        nose.tools.assert_almost_equal(sim_res.initial('z'), 1.00000, 4)
        nose.tools.assert_almost_equal(sim_res.final('x'), -2.000000, 4)
        nose.tools.assert_almost_equal(sim_res.final('y'), -1.0000000, 4)
        nose.tools.assert_almost_equal(sim_res.final('z'), 4.0000000, 4)
    
    @testattr(stddist = True)
    def test_changed_starttime(self):
        """
        This tests a simulation with different start time.
        """
        bounce = FMUModel('bouncingBall.fmu', path_to_fmus_me1)
        #bounce.initialize()
        opts = bounce.simulate_options()
        opts["CVode_options"]["rtol"] = 1e-4
        opts["CVode_options"]["atol"] = 1e-6
        res = bounce.simulate(start_time=2.,final_time=5.,options=opts)

        nose.tools.assert_almost_equal(res.initial('h'),1.000000,5)
        nose.tools.assert_almost_equal(res.final('h'),-0.98048862,4)
        nose.tools.assert_almost_equal(res.final('time'),5.000000,5)
        
    
    @testattr(stddist = True)
    def test_basic_simulation(self):
        """
        This tests the basic simulation and writing.
        """
        #Writing continuous
        bounce = load_fmu('bouncingBall.fmu', path_to_fmus_me1)
        #bounce.initialize()
        opts = bounce.simulate_options()
        opts["CVode_options"]["rtol"] = 1e-4
        opts["CVode_options"]["atol"] = 1e-6
        res = bounce.simulate(final_time=3., options=opts)
        
        nose.tools.assert_almost_equal(res.initial('h'),1.000000,5)
        nose.tools.assert_almost_equal(res.final('h'),-0.9804523,5)
        nose.tools.assert_almost_equal(res.final('time'),3.000000,5)
        
        #Writing after
        bounce = load_fmu('bouncingBall.fmu', path_to_fmus_me1)
        bounce.initialize()
        opt = bounce.simulate_options()
        opt['initialize']=False
        opt["CVode_options"]["rtol"] = 1e-4
        opt["CVode_options"]["atol"] = 1e-6
        res = bounce.simulate(final_time=3., options=opt)
        
        nose.tools.assert_almost_equal(res.initial('h'),1.000000,5)
        nose.tools.assert_almost_equal(res.final('h'),-0.9804523,5)
        nose.tools.assert_almost_equal(res.final('time'),3.000000,5)
        
        #Test with predefined FMUModel
        model = load_fmu(os.path.join(path_to_fmus_me1,'bouncingBall.fmu'))
        #model.initialize()
        res = model.simulate(final_time=3.,options=opts)

        nose.tools.assert_almost_equal(res.initial('h'),1.000000,5)
        nose.tools.assert_almost_equal(res.final('h'),-0.9804523,5)
        nose.tools.assert_almost_equal(res.final('time'),3.000000,5)


    @testattr(stddist = True)
    def test_default_simulation(self):
        """
        This test the default values of the simulation using simulate.
        """
        #Writing continuous
        bounce = load_fmu('bouncingBall.fmu', path_to_fmus_me1)
        opts = bounce.simulate_options()
        opts["CVode_options"]["rtol"] = 1e-4
        opts["CVode_options"]["atol"] = 1e-6
        res = bounce.simulate(final_time=3., options=opts)

        nose.tools.assert_almost_equal(res.solver.rtol, 1e-4, 6)
        assert res.solver.iter == 'Newton'
        
        nose.tools.assert_almost_equal(res.initial('h'),1.000000,5)
        nose.tools.assert_almost_equal(res.final('h'),-0.9804523,5)
        nose.tools.assert_almost_equal(res.final('time'),3.000000,5)
        
        #Writing continuous
        bounce = load_fmu('bouncingBall.fmu', path_to_fmus_me1)
        #bounce.initialize(options={'initialize':False})
        res = bounce.simulate(final_time=3.,
            options={'initialize':True,'CVode_options':{'iter':'FixedPoint','rtol':1e-6,'atol':1e-6}})
    
        nose.tools.assert_almost_equal(res.solver.rtol, 0.00000100, 7)
        assert res.solver.iter == 'FixedPoint'
        
        nose.tools.assert_almost_equal(res.initial('h'),1.000000,5)
        nose.tools.assert_almost_equal(res.final('h'),-0.98018113,5)
        nose.tools.assert_almost_equal(res.final('time'),3.000000,5)

    @testattr(stddist = True)
    def test_reset(self):
        """
        Test resetting an FMU. (Multiple instances is NOT supported on Dymola
        FMUs)
        """
        #Writing continuous
        bounce = load_fmu('bouncingBall.fmu', path_to_fmus_me1)
        opts = bounce.simulate_options()
        opts["CVode_options"]["rtol"] = 1e-4
        opts["CVode_options"]["atol"] = 1e-6
        #bounce.initialize()
        res = bounce.simulate(final_time=3., options=opts)
        
        nose.tools.assert_almost_equal(res.initial('h'),1.000000,5)
        nose.tools.assert_almost_equal(res.final('h'),-0.9804523,5)
        
        bounce.reset()
        #bounce.initialize()
        
        nose.tools.assert_almost_equal(bounce.get('h'), 1.00000,5)
        
        res = bounce.simulate(final_time=3.,options=opts)

        nose.tools.assert_almost_equal(res.initial('h'),1.000000,5)
        nose.tools.assert_almost_equal(res.final('h'),-0.9804523,5)
    
class Test_ODE_JACOBIANS1:
    
    @classmethod
    def setUpClass(cls):
        cname='Furuta'
        fname = os.path.join(get_files_path(), 'Modelica', 'furuta.mo')
        
        _fn_furuta = compile_fmu(cname, fname, compiler_options={'generate_ode_jacobian':True}, version="2.0alpha")
        
    def setUp(self):
        pass

    @testattr(stddist = True)
    def test_ode_simulation_furuta(self): 
        
        m_furuta = FMUModel2('Furuta.fmu')
        
        print "Starting simulation"
        
        opts = m_furuta.simulate_options()
        opts['with_jacobian'] = True
        res = m_furuta.simulate(final_time=100, options=opts)
    
        A,B,C,D,n_err1 = m_furuta.check_jacobians()
        
        opts['with_jacobian'] = False
        opts['initialize'] = False
        res = m_furuta.simulate(final_time=100, options=opts)
        
        A,B,C,D,n_err2 = m_furuta.check_jacobians()
        nose.tools.assert_equals(n_err1+n_err2, 0)

class Test_ODE_JACOBIANS2:
    
    @classmethod
    def setUpClass(cls):
        cname='NonLinear.MultiSystems'
        fname = os.path.join(get_files_path(), 'Modelica', 'NonLinear.mo')
        
        _fn_nonlin = compile_fmu(cname, fname, compiler_options={'generate_ode_jacobian':True,'automatic_tearing':False}, version="2.0alpha")
        
    def setUp(self):
        pass

    @testattr(stddist = True)
    def test_ode_simulation_NonLinear(self):
        pass
        """
        #Disabled the test temporary, see https://trac.jmodelica.org/ticket/4612 
        m_nonlin = FMUModel2('NonLinear_MultiSystems.fmu')
        
        m_nonlin.initialize()
        
        A,B,C,D,n_err = m_nonlin.check_jacobians()
        nose.tools.assert_equals(n_err, 0)
        """
        
        
class Test_ODE_JACOBIANS3:
    
    @classmethod
    def setUpClass(cls):
        cname='DISTLib.Examples.Simulation'
        fname = os.path.join(get_files_path(), 'Modelica', 'DISTLib.mo')
        
        _fn_distlib = compile_fmu(cname, fname, compiler_options={'generate_ode_jacobian':True}, version="2.0alpha")
        
    def setUp(self):
        pass
    
    @testattr(stddist = True)
    def test_ode_simulation_distlib(self): 
        
        m_distlib1 = FMUModel2('DISTLib_Examples_Simulation.fmu')
        m_distlib2 = FMUModel2('DISTLib_Examples_Simulation.fmu')
        
        opts = m_distlib1.simulate_options()
        opts['with_jacobian'] = True
        res = m_distlib1.simulate(final_time=70, options=opts)
        res = m_distlib2.simulate(final_time=70)
        
        A,B,C,D,n_err1 = m_distlib1.check_jacobians()

        A,B,C,D,n_err2 = m_distlib2.check_jacobians()
        nose.tools.assert_equals(n_err1+n_err2, 0)
        
 
class Test_ODE_JACOBIANS4:
    
    @classmethod
    def setUpClass(cls):
        cname='NonLinear.TwoSystems_wIO'
        fname = os.path.join(get_files_path(), 'Modelica', 'NonLinearIO.mo')
        
        fn_nonlinIO = compile_fmu(cname, fname, compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'automatic_tearing':False}, version="2.0alpha")
        
    def setUp(self):
        pass       
        
    @testattr(stddist = True)
    def test_ode_simulation_NonLinearIO(self):
        m_nonlinIO = FMUModel2('NonLinear_TwoSystems_wIO.fmu')
        
        m_nonlinIO.set('u', 1)
        m_nonlinIO.set('u1', 10000)
        m_nonlinIO.set('u2', 1)
        m_nonlinIO.set('u3', 10000)
        
        m_nonlinIO.initialize()
        
        A,B,C,D,n_err = m_nonlinIO.check_jacobians()
        nose.tools.assert_equals(n_err, 0)
        
        
class Test_ODE_JACOBIANS5:
    
    @classmethod
    def setUpClass(cls):
        cname='BlockOdeJacTest'
        fname = os.path.join(get_files_path(), 'Modelica', 'BlockOdeJacTest.mo')
        
        _fn_block = compile_fmu(cname, fname, compiler_options={'generate_ode_jacobian':True, 'automatic_tearing':False}, version="2.0alpha")
        
    def setUp(self):
        pass
    
    @testattr(stddist = True)
    def test_ode_simulation_distlib(self):
        pass #THIS NEEDS TO BE FIXED SEE TICKET 3430
        """
        m_block = FMUModel2('BlockOdeJacTest.fmu')
        m_block.initialize()
        
        A,B,C,D,n_err = m_block.check_jacobians()
        nose.tools.assert_equals(n_err, 0)
        """
