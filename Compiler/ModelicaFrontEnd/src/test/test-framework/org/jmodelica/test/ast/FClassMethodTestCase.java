/*
    Copyright (C) 2009 Modelon AB

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/


package org.jmodelica.test.ast;
import org.jmodelica.parser.ModelicaParser;
import org.jmodelica.parser.FlatModelicaParser;
import org.jmodelica.ast.*;
import java.util.Collection;
import java.lang.reflect.Method;

public class FClassMethodTestCase extends TestCase {
	private String output = "";
    private String methodName = "";
    private String outputFileName = "";
    private boolean resultOnFile = false;
	
    private ModelicaParser parser = new ModelicaParser();
    private FlatModelicaParser flatParser = new FlatModelicaParser();
    
	public FClassMethodTestCase() {}
    
	/**
	 * @param name
	 * @param description
	 * @param sourceFileName
	 * @param className
	 * @param output
	 * @oaram methodName
	 * @param outputFileName
	 * @param resultOnFile
	 */
	public FClassMethodTestCase(String name, 
			                  String description,
			                  String sourceFileName, 
			                  String className, 
			                  String result,
			                  String methodName,
			                  boolean resultOnFile) {
		super(name, description, sourceFileName, className);
		this.methodName = methodName;
		this.resultOnFile = resultOnFile;		
		if (!resultOnFile) {
			this.output = result;
		} else {
			this.outputFileName = result;
		}
		
	}

	public void dump(StringBuffer str,String indent) {
		str.append(indent+"FClassMethodTestCase: \n");
		if (testMe())
			str.append("PASS\n");
		else
			str.append("FAIL\n");
		str.append(indent+" Name:                     "+getName()+"\n");
		str.append(indent+" Description:              "+getDescription()+"\n");
		str.append(indent+" Source file:              "+getSourceFileName()+"\n");
		str.append(indent+" Class name:               "+getClassName()+"\n");
		if (!isResultOnFile())
			str.append(indent+" Output:\n"+getOutput()+"\n");
		else
			str.append(indent+" Output file name: "+getOutputFileName()+"\n");
		
	}

	public String toString() {
		StringBuffer str = new StringBuffer();
		str.append("FClassMethodTestCase: \n");
		str.append(" Name:                     "+getName()+"\n");
		str.append(" Description:              "+getDescription()+"\n");
		str.append(" Source file:              "+getSourceFileName()+"\n");
		str.append(" Class name:               "+getClassName()+"\n");
		if (!isResultOnFile())
			str.append(" Output:\n"+getOutput()+"\n");
		else
			str.append(" Output file name: "+getOutputFileName()+"\n");
		return str.toString();
	}
	
	public boolean printTest(StringBuffer str) {
		str.append("TestCase: " + getName() +": ");
		if (testMe()) {
			str.append("PASS\n");
			return true;
		}else {
			str.append("FAIL\n");
			return false;
		}
	}
	
	public void dumpJunit(StringBuffer str, int index) {
		//StringBuffer strd=new StringBuffer();
		//dump(strd,"");
		testMe();
		//System.out.println(strd);
		str.append("  @Test public void " + getName() + "() {\n");
		str.append("    assertTrue(ts.get("+index+").testMe());\n");
	    str.append("  }\n\n");
	}
	
	public boolean testMe() {
        System.out.println("Running test: " + getClassName());
		SourceRoot sr = parser.parseFile(getSourceFileName());
		TestSuite.loadOptions(sr);
		sr.setFileName(getSourceFileName());
		InstProgramRoot ipr = sr.getProgram().getInstProgramRoot();
		Collection<Problem> problems;
		try {
			problems = ipr.checkErrorsInInstClass(getClassName());
		} catch (ModelicaClassNotFoundException e) {
			return false;
		}
	    if (problems.size()>0) {
	    	//System.out.println("***** Errors in Class!");
	    	return false;
	    }	    
	    FlatRoot flatRoot = new FlatRoot();
	    flatRoot.setFileName(getSourceFileName());
	    FClass fc = new FClass();
	    flatRoot.setFClass(fc);
	    
	    InstNode ir;
	    try {
	    	ir = ipr.findFlattenInst(getClassName(), fc);
	    } catch (ModelicaClassNotFoundException e) {
	    	return false;
	    }
	    
	    fc.transformCanonical();
	    
	    try {
	    	Method method =  fc.getClass().getDeclaredMethod(getMethodName(), 
	    			new Class[] {});
	    	Object args[] = new Object[0];
	    	String testResult =((String)method.invoke(fc, args));
	    	testResult = removeWhitespace(testResult);
	    	String outp = removeWhitespace(getOutput());

//	    	System.out.println("test ****  \n" +testResult);
//	    	System.out.println("fixture ****  \n" +outp);
//	    	for (int i=0;i<testResult.length();i++) {
//	    		System.out.println(outp.substring(i,i+1) + " | " +
//	    				testResult.substring(i,i+1));
//	    	}
	    	return testResult.compareTo(outp)==0;
	    } catch (Exception e) {
	    	e.printStackTrace();
	    }
	    return false;    	
	}	

	
	/**
	 * @return the output
	 */
	public String getOutput() {
		return output;
	}
	/**
	 * @param output the output to set
	 */
	public void setOutput(String output) {
		this.output = output;
		this.outputFileName = "";
		this.resultOnFile = false;
	}
	
	/**
	 * @return the methodName
	 */
	public String getMethodName() {
		return methodName;
	}
	/**
	 * @param methodName the methodName to set
	 */
	public void setMethodName(String methodName) {
		this.methodName = methodName;
	}

	/**
	 * @return the outputFileName
	 */
	public String getOutputFileName() {
		return outputFileName;
	}
	/**
	 * @param outputFileName the outputFileName to set
	 */
	public void setOutputFileName(String outputFileName) {
		this.outputFileName = outputFileName;
		this.output = "";
		this.resultOnFile = true;
	}
	/**
	 * @return the resultOnFile
	 */
	public boolean isResultOnFile() {
		return resultOnFile;
	}
	
	/**
	 * @param resultOnFile the resultOnFile to set
	 */
	public void setResultOnFile(boolean resultOnFile) {
		this.resultOnFile = resultOnFile;
	}
	
}
