#!/usr/bin/env python 
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Modelon AB
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

"""
Module containing the tests for Jacobian generation. 
"""

import nose
import os
import numpy as N
import sys as S
import pyfmi as fmi
import pyfmi.fmi_algorithm_drivers as ad

from pymodelica import compile_fmu
from pyfmi.fmi import FMUModel2
from tests_jmodelica import testattr, get_files_path
from pyfmi.common.core import get_platform_dir
path_to_mofiles = os.path.join(get_files_path(), 'Modelica')



class Test_FMI_Jaobians_Elementary_operators:
	
	"""
	Test for arithmetic operators, as listed in section 3.4 of the Modelica specification 3.2. 3.2
	"""

	def setUp(self):	
		self.fname = os.path.join(path_to_mofiles,"JacGenTests.mo")
		

	@testattr(stddist = True)
	def test_elementary_addition(self):
		cname = "JacGenTests.JacTestAdd"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0
		
	
	@testattr(stddist = True)
	def test_elementary_substraction(self):
		cname = "JacGenTests.JacTestSub"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0

	
	@testattr(stddist = True)
	def test_elementary_multiplication(self):
		cname = "JacGenTests.JacTestMult"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0

	@testattr(stddist = True)
	def test_elementary_division(self):
		cname = "JacGenTests.JacTestDiv"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0
	
	
	@testattr(stddist = True)
	def test_elementary_exponentiation(self):
		cname = "JacGenTests.JacTestPow"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0

	
class Test_FMI_Jaobians_Elementary_functions:
	"""
	This class tests the elemenary functions as described in section 3.7.1.2 in the modelica specification v. 3.2
	"""


	def setUp(self):	
		self.fname = os.path.join(path_to_mofiles,"JacGenTests.mo")

	"""
	Fails in the check_jacobians test
	@testattr(stddist = True)
	def test_elementary_abs(self):
		cname = "JacGenTests.JacTestAbs"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0
	"""

	@testattr(stddist = True)
	def test_elementary_sqrt(self):
		cname = "JacGenTests.JacTestSqrt"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0	
		
	@testattr(stddist = True)
	def test_elementary_sin(self):
		cname = "JacGenTests.JacTestSin"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0
	
	@testattr(stddist = True)
	def test_elementary_cos(self):
		cname = "JacGenTests.JacTestCos"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0
	
	@testattr(stddist = True)
	def test_elementary_tan(self):	
		cname = "JacGenTests.JacTestTan"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0
	
	@testattr(stddist = True)
	def test_elementary_Cotan(self):	
		cname = "JacGenTests.JacTestCoTan"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0	

	@testattr(stddist = True)
	def test_elementary_asin(self):	
		cname = "JacGenTests.JacTestAsin"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0
	
	@testattr(stddist = True)
	def test_elementary_acos(self):	
		cname = "JacGenTests.JacTestAcos"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0
	
	@testattr(stddist = True)
	def test_elementary_atan(self):	
		cname = "JacGenTests.JacTestAtan"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0
		
		
	@testattr(stddist = True)
	def test_elementary_atan2(self):		
		cname = "JacGenTests.JacTestAtan2"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0
		
	@testattr(stddist = True)
	def test_elementary_sinh(self):	
		cname = "JacGenTests.JacTestSinh"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0
		
	@testattr(stddist = True)
	def test_elementary_cosh(self):	
		cname = "JacGenTests.JacTestCosh"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0

		
	@testattr(stddist = True)
	def test_elementary_tanh(self):	
		cname = "JacGenTests.JacTestTanh"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0

	
	@testattr(stddist = True)
	def test_elementary_exp(self):	
		cname = "JacGenTests.JacTestExp"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0

	
	@testattr(stddist = True)
	def test_elementary_log(self):
		cname = "JacGenTests.JacTestLog"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0

	
	@testattr(stddist = True)
	def test_elementary_log10(self):
		cname = "JacGenTests.JacTestLog10"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0
	
	
class Test_FMI_Jaobians_Whencases:
	
	def setUp(self):
		self.fname = os.path.join(path_to_mofiles,"JacGenTests.mo")
	
	"""
	Raises compliance error: "Else clauses in when equations are currently not supported". 
	Even if generate_ode_jacobian is set to false. 
	@testattr(stddist = True)
	def test_elementary_whenElse(self):
		cname = "JacGenTests.JacTestWhenElse"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':False,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0
	"""
	
	"""
	Raises: CcodeCompilationError: 
	Message: Compilation of generated C code failed.
	 Raises compliance error: "Else clauses in when equations are currently not supported". 
	Even if generate_ode_jacobian is set to false. 
	@testattr(stddist = True)
	def test_elementary_whenSimple(self):
		cname = "JacGenTests.JacTestWhenSimple"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0
	"""

	"""
	Raises: CcodeCompilationError: 
	Message: Compilation of generated C code failed.
	@testattr(stddist = True)
	def test_elementary_whenSample(self):
		cname = "JacGenTests.JacTestWhenSample"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0
	"""

	@testattr(stddist = True)
	def test_elementary_IfSimple(self):
		cname = "JacGenTests.JacTestIfSimple1"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0		
		
	
	@testattr(stddist = True)
	def test_elementary_IfSimple2(self):
		cname = "JacGenTests.JacTestIfSimple2"
		fn = compile_fmu(cname,self.fname,compiler_options={'generate_ode_jacobian':True,'eliminate_alias_variables':False,'fmi_version':2.0})
		m = FMUModel2(fn)
		m.set_debug_logging(True)
		Afd,Bfd,Cfd,Dfd,n_errs, s_errs = m.check_jacobians(delta_rel=1e-6,delta_abs=1e-3,tol=1e-5,check_sparsity_structure=True)
		assert n_errs ==0 and s_errs == 0
	
	











