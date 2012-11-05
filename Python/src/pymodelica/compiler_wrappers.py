#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) 2009 Modelon AB
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Interfaces to the JModelica.org Modelica and Optimica compilers.

"""
import jpype

import pymodelica as pym
from compiler_interface import *
from pymodelica.common.core import list_to_string


class ModelicaCompiler(object):
    """ 
    User class for accessing the Java ModelicaCompiler class. 
    """
    
    LOG_ERROR = ModelicaCompilerInterface.ERROR
    LOG_WARNING = ModelicaCompilerInterface.WARNING
    LOG_INFO = ModelicaCompilerInterface.INFO
    
    jm_home = pym.environ['JMODELICA_HOME']

    options_file_path = os.path.join(jm_home, 'Options','options.xml')


    def __init__(self):
        """ 
        Create a Modelica compiler. The compiler can be used to compile pure 
        Modelica models. A compiler instance can be used multiple times.
        """
        try:
            options = OptionRegistryInterface(self.options_file_path)
        except jpype.JavaException as ex:
            self._handle_exception(ex)
            
        options.addStringOption('MODELICAPATH',pym.environ['MODELICAPATH'])
        
        self._compiler = pym._create_compiler(ModelicaCompilerInterface, options)
            
    @classmethod
    def set_log_level(self,level):
        """ 
        Set the level of log messages. Valid options are 
        ModelicaCompiler.LOG_ERROR, ModelicaCompiler.LOG_WARNING and 
        ModelicaCompiler.LOG_INFO. They will print, errors only, both errors and 
        warnings and all log messages respectively.
        
        Parameters::
        
            level --
                Level of log messages to set. Valid options are 
                ModelicaCompiler.LOG_ERROR, ModelicaCompiler.LOG_WARNING and 
                ModelicaCompiler.LOG_INFO.
        """
        ModelicaCompilerInterface.setLogLevel(ModelicaCompilerInterface.log, level)

    @classmethod
    def get_log_level(self):
        """ 
        Get the current level of log messages set. 
        
        Returns::
        
            The current level of log messages.
        """
        return ModelicaCompilerInterface.getLogLevel(ModelicaCompilerInterface.log)
    
    
    def set_options(self, compiler_options):
        """
        Set compiler options. See available options in the file options.xml.
        
        Parameters::
        
            compiler_options --
                A dict of options where the key specifies which option to modify 
                and the value the new value for the option.
        
        Raises::
        
            JMIException if the value of the option is not one of the allowed 
            types (float, boolean, string, integer or list).
        """
        # set compiler options
        for key, value in compiler_options.iteritems():
            if isinstance(value, bool):
                self.set_boolean_option(key, value)
            elif isinstance(value, basestring):
                self.set_string_option(key,value)
            elif isinstance(value, int):
                self.set_integer_option(key,value)
            elif isinstance(value, float):
                self.set_real_option(key,value)
            elif isinstance(value, list):
                self.set_string_option(key, list_to_string(value))
            else:
                raise JMIException("Unknown compiler option type for key: %s. \
                Should be of the following types: boolean, string, integer, \
                float or list" %key)

    def set_compiler_log_level(self, compiler_log_level):
        # set compiler log level
        if compiler_log_level.lower().startswith('w'):
            self.set_log_level(ModelicaCompiler.LOG_WARNING)
        elif compiler_log_level.lower().startswith('e'):
            self.set_log_level(ModelicaCompiler.LOG_ERROR)
        elif compiler_log_level.lower().startswith('i'):
            self.set_log_level(ModelicaCompiler.LOG_INFO)
        else:
            logging.warning("Invalid compiler_log_level: "+str(compiler_log_level) + 
            " using level 'warning' instead.")

        
    def get_modelicapath(self):
        """ 
        Get the path to Modelica libraries set for this compiler.
        
        Returns::
        
            Path to Modelica libraries set.
        """
        return self._compiler.getModelicapath()
    
    def set_modelicapath(self, path):
        """ 
        Set the path to Modelica libraries for this compiler instance. 
        
        Parameters::
        
            path --
                The path to Modelica libraries.
        """
        self._compiler.setModelicapath(path)

    def get_boolean_option(self, key):
        """ 
        Get the boolean option set for the specific key. 
        
        Parameters::
        
            key --
                Get the boolean option for this key.
        
        Raises::
        
            UnknownOptionError if the option does not exist.
        """
        try:
            option = self._compiler.getBooleanOption(key)
        except jpype.JavaException as ex:
            self._handle_exception(ex)
        return bool(option)
    
    def set_boolean_option(self, key, value):
        """ 
        Set the boolean option with key to value. If the option does not exist 
        an exception will be raised. 
        
        Parameters::
        
            key --
                Key for the boolean option.
                
            value --
                Boolean option.
                
        Raises::
        
            UnknownOptionError if the option does not exist.
        """
        try:
            self._compiler.setBooleanOption(key, value)
        except jpype.JavaException as ex:
            self._handle_exception(ex)
        
    def get_integer_option(self, key):
        """ 
        Get the integer option set for the specific key. 
        
        Parameters::
        
            key --
                Get the integer option for this key.
        
        Raises::
        
            UnknownOptionError if the option does not exist.
        """
        try:
            option = self._compiler.getIntegerOption(key)
        except jpype.JavaException as ex:
            self._handle_exception(ex)
        return option
    
    def set_integer_option(self, key, value):
        """ 
        Set the integer option with key to value. If the option does not exist 
        an exception will be raised. 
        
        Parameters::
        
            key --
                Key for the integer option.
                
            value --
                Integer option.
                
        Raises::
        
            UnknownOptionError if the options does not exist.
        """
        try:
            self._compiler.setIntegerOption(key, value)
        except jpype.JavaException as ex:
            self._handle_exception(ex)
        
    def get_real_option(self, key):
        """ 
        Get the real option set for the specific key. 
        
        Parameters::
        
            key --
                Get the real option for this key.
        
        Raises::
        
            UnknownOptionError if the option does not exist.
        """
        try:
            option = self._compiler.getRealOption(key)
        except jpype.JavaException as ex:
            self._handle_exception(ex)
        return option
    
    def set_real_option(self, key, value):
        """ 
        Set the real option with key to value. If the option does not exist an 
        exception will be raised.
        
        Parameters::
        
            key --
                Key for the real option.
                
            value --
                Real option.
                
        Raises::
        
            UnknownOptionError if the options does not exist.
        """
        try:
            self._compiler.setRealOption(key, value)
        except jpype.JavaException as ex:
            self._handle_exception(ex)
                    
    def get_string_option(self, key):
        """ 
        Get the string option set for the specific key. 
        
        Parameters::
        
            key --
                Get the string option for this key.
                
        Raises::
        
            UnknownOptionError if the option does not exist.
        """
        try:
            option = self._compiler.getStringOption(key)
        except jpype.JavaException as ex:
            self._handle_exception(ex)
        return str(option)
        
    def set_string_option(self, key, value):
        """ 
        Set the string option with key to value. If the option does not exist an 
        exception will be raised.
        
        Parameters::
        
            key --
                Key for the string option.
                
            value --
                String option.
                
        Raises::
        
            UnknownOptionError if the options does not exist.
        """
        try:
            self._compiler.setStringOption(key, value)
        except jpype.JavaException as ex:
            self._handle_exception(ex)
    
    def get_XML_tpl(self):
        """ 
        Get the file path to the XML model description template.
        
        Returns::
        
            The file path for the XML model description template.
        """
        return self._compiler.getXMLTpl()

    def set_XML_tpl(self, template):
        """ 
        Set the XML model description template to the file pointed out by 
        template.
        
        Parameters::
        
            template --
                The new XML model description template.       
        """
        self._compiler.setXMLTpl(template)
        
    def get_cTemplate(self):
        """ 
        Get the file path to the c code template. 
        
        Returns::
        
            The file path for the c code template.
        """
        return self._compiler.getCTemplate()
    
    def set_cTemplate(self, template):
        """ 
        Set the c code template to the file pointed out by template.
        
        Parameters::
        
            template --
                The new c code template.
        """
        self._compiler.setCTemplate(template)
        
        
    def compile_JMU(self, class_name, file_name, target, compile_to):
        """
        Compiles a model (parsing, instantiating, flattening, code generation 
        and binary file generation) and creates a JMU on the file system. Set 
        target to specify the contents of the object file used to build the 
        binary. The different targets are "model", "model_noad", "algorithms" 
        and "ipopt". See makefile in install folder for details on the different 
        targets.
        
        Parameters::
        
            class_name --
                Name of model class in the model file to compile.
            
            file_name --
                Path to file or list of paths to files in which the model is 
                contained.
                
            target --
                The build target. Valid options are 'model', 'model_noad', 
                'algorithms' and 'ipopt'.
                
            compile_to --
                Specify location of the compiled JMU. Directory will be created 
                if it does not exist.
        """
        try:
            self._compiler.compileJMU(class_name, file_name, target, compile_to)
        except jpype.JavaException as ex:
            self._handle_exception(ex)
        
    def compile_FMU(self, class_name, file_name, target, compile_to):
        """
        Compiles a model (parsing, instantiating, flattening, code generation 
        and binary file generation) and creates an FMU on the file system. Set 
        target to specify the contents of the object file used to build the 
        binary. The different targets are "model_fmume" and "model_fmucs". 
        See makefile in install folder for details on the different targets.
        
        Note: target must currently be set to 'model_fmume'.
        
        Parameters::
        
            class_name --
                Name of model class in the model file to compile.
            
            file_name --
                Path to file or list of paths to files or libraries 
                in which the model is contained.
                
            target --
                The build target. Valid options are 'model_fmume' and 
                'model_fmucs'.
                Note: Must currently be set to 'model_fmume'.
                
            compile_to --
                Specify location of the compiled FMU. Directory will be created 
                if it does not exist.
        """
        try:
            self._compiler.compileFMU(class_name, file_name, target, compile_to)
        except jpype.JavaException as ex:
            self._handle_exception(ex)

    def compile_FMUX(self, class_name, file_name, compile_to):
        """
        Compiles a model (parsing, instantiating, flattening and XML code 
        generation) and creates an FMUX on the file system.
        
        Parameters::
        
            class_name --
                Name of model class in the model file to compile.
            
            file_name --
                Path to file or list of paths to files or libraries 
                in which the model is contained.
                
            compile_to --
                Specify location of the compiled FMUX. Directory will be created 
                if it does not exist.
        """
        try:
            self._compiler.compileFMUX(class_name, file_name, compile_to)
        except jpype.JavaException as ex:
            self._handle_exception(ex)

    def parse_model(self,model_file_name):   
        """ 
        Parse a model.

        Parse a model and return a reference to the source tree representation.

        Parameters::
            
            model_file_name -- 
                Path to file or list of paths to files or libraries 
                in which the model is contained.

        Returns::
        
            Reference to the root of the source tree representation of the 
            parsed model.

        Raises::
        
            CompilerError if one or more error is found during compilation.
            
            IOError if the model file is not found, can not be read or any other 
            IO related error.
            
            Exception if there are general errors related to the parsing of the 
            model.
            
            JError if there was a runtime exception thrown by the underlying 
            Java classes.
        """        
        if isinstance(model_file_name, basestring):
            model_file_name = [model_file_name]
        try:
            sr = self._compiler.parseModel(model_file_name)
            return sr        
        except jpype.JavaException as ex:
            self._handle_exception(ex)

    def instantiate_model(self, source_root, model_class_name):
        """ 
        Generate an instance tree representation for a model.

        Generate an instance tree representation for a model using the 
        source tree belonging to the model which must first be created 
        with parse_model.

        Parameters::
          
            source_root -- 
                Reference to the root of the source tree representation.
                
            model_class_name -- 
                Name of model class in the model file to compile.

        Returns::
        
            Reference to the instance AST node representing the model instance. 

        Raises::
        
            CompilerError if one or more error is found during compilation.
            
            ModelicaClassNotFoundError if the model class is not found.
            
            JError if there was a runtime exception thrown by the underlying 
            Java classes.
        """    
        try:
            ipr = self._compiler.instantiateModel(source_root, model_class_name)
            return ipr    
        except jpype.JavaException as ex:
            self._handle_exception(ex)

    def flatten_model(self, inst_class_decl):
        """ 
        Compute a flattened representation of a model. 

        Compute a flattened representation of a model using the instance tree 
        belonging to the model which must first be created with 
        instantiate_model.

        Parameters::
          
            inst_class_decl -- 
                Reference to a model instance. 

        Returns::
        
            Object (FClass) representing the flattened model. 

        Raises::
        
            CompilerError if one or more error is found during compilation.
            
            ModelicaClassNotFoundError if the model class is not found.
            
            IOError if the model file is not found, can not be read or any 
            other IO related error.
            
            JError if there was a runtime exception thrown by the underlying 
            Java classes.
        """
        try:
            fclass = self._compiler.flattenModel(inst_class_decl)
            return fclass    
        except jpype.JavaException as ex:
            self._handle_exception(ex)

    def generate_code(self,fclass):
        """ 
        Generate code for a model.

        Generate code for a model c and xml code for a model using the FClass 
        represenation created with flatten_model and template files located in 
        the JModelica installation folder. Default output folder is the current 
        folder from which this module is run.

        Parameters::
        
            fclass -- 
                Reference to the flattened model object representation.  

        Raises::
        
            IOError if the model file is not found, can not be read or any other 
            IO related error.
                
            JError if there was a runtime exception thrown by the underlying 
            Java classes.
        """
        try:
            self._compiler.generateCode(fclass)
        except jpype.JavaException as ex:
            self._handle_exception(ex)
            
    def _handle_exception(self, ex):
        """ 
        Catch and handle all expected Java Exceptions that the 
        underlying Java classes might throw. Raises an appropriate Python error 
        or the default JError.
        """
        if ex.javaClass() is ModelicaCompilerException \
            or ex.javaClass() is OptimicaCompilerException:
            arraylist = ex.__javaobject__.getProblems()
            itr = arraylist.iterator()

            compliance_errors = []
            errors = []
            warnings = []
            while itr.hasNext():
                p = str(itr.next())
                if p.count('Compliance error')>0:
                    compliance_errors.append(p)
                elif p.count('Warning')>0:
                    warnings.append(p)
                else:
                    errors.append(p)
                    
            raise CompilerError(errors,compliance_errors,warnings)
        
        if ex.javaClass() is ModelicaClassNotFoundException:
            raise ModelicaClassNotFoundError(
                str(ex.__javaobject__.getClassName()))
        
        if ex.javaClass() is OptimicaClassNotFoundException:
            raise OptimicaClassNotFoundError(
                str(ex.__javaobject__.getClassName()))
        
        if ex.javaClass() is jpype.java.io.FileNotFoundException:
            raise IOError(
                '\nMessage: '+ex.message().encode('utf-8')+\
                '\nStacktrace: '+ex.stacktrace().encode('utf-8'))
        
        if ex.javaClass() is jpype.java.io.IOException:
            raise IOError(
                '\nMessage: '+ex.message().encode('utf-8')+\
                '\nStacktrace: '+ex.stacktrace().encode('utf-8'))
        
        if ex.javaClass() is jpype.javax.xml.xpath.XPathExpressionException:
            raise XPathExpressionError(
                '\nMessage: '+ex.message().encode('utf-8')+\
                '\nStacktrace: '+ex.stacktrace().encode('utf-8'))
        
        if ex.javaClass() is jpype.javax.xml.parsers.ParserConfigurationException:
            raise ParserConfigurationError(
                '\nMessage: '+ex.message().encode('utf-8')+\
                '\nStacktrace: '+ex.stacktrace().encode('utf-8'))
        
        if ex.javaClass() is SAXException or \
            ex.javaClass() is SAXNotRecognizedException or \
            ex.javaClass() is SAXNotSupportedException or \
            ex.javaClass() is SAXParseException:
            raise SAXError(
                '\nMessage: '+ex.message().encode('utf-8')+\
                '\nStacktrace: '+ex.stacktrace().encode('utf-8'))
    
        if ex.javaClass() is UnknownOptionException:
            raise UnknownOptionError(
                ex.message().encode('utf-8')+'\nStacktrace: '+\
                    ex.stacktrace().encode('utf-8'))
        
        if ex.javaClass() is jpype.java.lang.Exception:
            raise Exception(
                '\nMessage: '+ex.message().encode('utf-8')+\
                '\nStacktrace: '+ex.stacktrace().encode('utf-8'))
        
        if ex.javaClass() is jpype.java.lang.NullPointerException:
            raise JError(ex.stacktrace().encode('utf-8'))
        
        if ex.javaClass() is ModelicaCCodeCompilationException or \
            ex.javaClass() is OptimicaCCodeCompilationException:
            raise CcodeCompilationError(
                '\nMessage: '+ex.message().encode('utf-8')+\
                '\nStacktrace: '+ex.stacktrace().encode('utf-8'))
        
        raise JError(ex.stacktrace().encode('utf-8'))

class OptimicaCompiler(ModelicaCompiler):
    """ 
    User class for accessing the Java OptimicaCompiler class. 
    """

    jm_home = pym.environ['JMODELICA_HOME']

    def __init__(self):
        """ 
        Create an Optimica compiler. The compiler can be used to compile both 
        Modelica and Optimica models. A compiler instance can be used multiple 
        times.
        """
        try:
            options = OptionRegistryInterface(self.options_file_path)
        except jpype.JavaException as ex:
            self._handle_exception(ex)
            
        options.addStringOption('MODELICAPATH',pym.environ['MODELICAPATH'])
        
        self._compiler = pym._create_compiler(OptimicaCompilerInterface, options)

    @classmethod
    def set_log_level(self,level):
        """ 
        Set the level of log messages. Valid options are 
        OptimicaCompiler.LOG_ERROR, OptimicaCompiler.LOG_WARNING and 
        OptimicaCompiler.LOG_INFO. They will print, errors only, both errors and 
        warnings and all log messages respectively.
        
        Parameters::
        
            level --
                Level of log messages to set. Valid options are 
                OptimicaCompiler.LOG_ERROR, OptimicaCompiler.LOG_WARNING 
                and OptimicaCompiler.LOG_INFO.
        """
        OptimicaCompilerInterface.setLogLevel(OptimicaCompilerInterface.log, level)

    @classmethod
    def get_log_level(self):
        """ 
        Get the current level of log messages set. 
        
        Returns::
        
            The current level of log messages.
        """
        return OptimicaCompilerInterface.getLogLevel(OptimicaCompilerInterface.log)

    def set_boolean_option(self, key, value):
        """ 
        Set the boolean option with key to value. If the option does not exist 
        an exception will be raised. 
        
        Parameters::
        
            key --
                Key for the boolean option.
                
            value --
                Boolean option.
                
        Raises::
        
            UnknownOptionError if the options does not exist.
        """
        try:
            self._compiler.setBooleanOption(key, value)
        except jpype.JavaException as ex:
            self._handle_exception(ex)

class JError(Exception):
    """ 
    Base class for exceptions specific to this module.
    """
    
    def __init__(self, message):
        """ 
        Create new error with a specific message. 
        
        Parameters::
        
            message --
                The error message.
        """
        self.message = message
        
    def __str__(self):
        """ 
        Print error message when class instance is printed.
         
        Override the general-purpose special method such that a string 
        representation of an instance of this class will be the error message.
        
        Returns::
        
            The error message.
        """
        return self.message

class ModelicaClassNotFoundError(JError):
    """ 
    Class for errors raised if the Modelica model class to be compiled can not 
    be found.
    """
    pass

class OptimicaClassNotFoundError(JError):
    """ 
    Class for a errors raised if the Optimica model class to be compiled can not 
    be found.
    """ 
    pass


class CompilerError(JError):
    """ 
    Class representing a compiler error. Raised if there were one or more errors 
    found during compilation of the model. If there are several errors in one 
    model, they are collected and presented in one CompilerError.
    """

    def __init__(self, errors, compliance_errors, warnings):
        """ 
        Create CompilerError with a list of error messages. 
        """
        self.compliance_errors = compliance_errors
        self.warnings = warnings
        self.errors = errors
        
    def __str__(self):
        """ 
        Print error messages.
         
        Override the general-purpose special method such that a string 
        representation of an instance of this class will a string representation
        of the error messages.
        """
    
        problems = '\n' + str(len(self.errors)) + ' error(s), ' + \
            str(len(self.compliance_errors)) + ' compliance error(s) and ' + \
            str(len(self.warnings)) + ' warning(s) found:\n\n' 
        for e in self.errors:
            problems = problems + e + "\n\n"
        for ec in self.compliance_errors:
            problems = problems + ec + "\n\n"
        for w in self.warnings:
            problems = problems + w + "\n\n"
        
        return problems

class CcodeCompilationError(JError):
    """ 
    Class for errors thrown when compiling a binary file from c code.
    """
    pass

class XPathExpressionError(JError):
    """ 
    Class representing errors in XPath expressions. 
    """
    pass

class ParserConfigurationError(JError):
    """ 
    Class for errors thrown when configuring XML parser. 
    """
    pass

class SAXError(JError):
    """ 
    Class representing a SAX error. 
    """
    pass

class UnknownOptionError(JError):
    """ 
    Class for error thrown when trying to access unknown compiler option. 
    """
    pass
