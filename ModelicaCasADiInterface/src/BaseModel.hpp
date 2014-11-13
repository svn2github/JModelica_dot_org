/*
Copyright (C) 2013 Modelon AB

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

#ifndef _MODELICACASADI_BASEMODEL 
#define _MODELICACASADI_BASEMODEL
#include <iostream>
#include <map>
#include <string>
#include <vector>
#include <utility>

#include "casadi/casadi.hpp"

#include "ModelFunction.hpp"
#include "types/VariableType.hpp"
#include "Variable.hpp"
#include "RealVariable.hpp"
#include "Equation.hpp"
#include "RefCountedNode.hpp"
#include "Ref.hpp"
#include "BLTHandler.hpp"
#include "EquationContainer.hpp"
#include "FlatEquationList.hpp"

namespace ModelicaCasADi 
{  
class BaseModel: public RefCountedNode {
    protected:
        typedef std::map< std::string, Ref<ModelFunction> > functionMap;
        typedef std::map< std::string, Ref<VariableType> > typeMap;
    public:
        enum VariableKind {
            REAL_CONSTANT,       
            REAL_PARAMETER_INDEPENDENT,                         
            REAL_PARAMETER_DEPENDENT,   

    INTEGER_CONSTANT,                           
    INTEGER_PARAMETER_INDEPENDENT,                         
    INTEGER_PARAMETER_DEPENDENT,      

    BOOLEAN_CONSTANT,                             
    BOOLEAN_PARAMETER_INDEPENDENT,                         
    BOOLEAN_PARAMETER_DEPENDENT,               

    STRING_CONSTANT,                       
    STRING_PARAMETER_INDEPENDENT,                         
    STRING_PARAMETER_DEPENDENT,                         

    DERIVATIVE,
    DIFFERENTIATED,
    REAL_INPUT, 
    REAL_ALGEBRAIC,
    REAL_DISCRETE,

    INTEGER_DISCRETE,
    INTEGER_INPUT,
    BOOLEAN_DISCRETE,
    BOOLEAN_INPUT,
    STRING_DISCRETE,
    STRING_INPUT,

    NUM_OF_VARIABLE_KIND  // This must be defined last & no other
        // variables may be explicitly defined with a number
}; // End enum VariableKind
    /** Create a blank, uninitialized Model */
    BaseModel() { 
        dirty = false; 
        timeVar = casadi::MX(0);
        equationContainer_ = new FlatEquationList(); //The default container is flat
        /* todo: just create a time variable instead? */
    }
    /** Initialize the Model, before populating it.
    * @param string identifier, typically <packagename>_<classname>, default empty string */
    void initializeModel(std::string identifier = "");
    ~BaseModel(){
        // Delete all the Model's variables, since they are OwnedNodes with the Model as owner.
        for (std::vector< Variable * >::iterator it = z.begin(); it != z.end(); ++it) {
            delete *it;
            *it = NULL;
        }
        // Delete all the Model's variables that were moved to the eliminated container, since they are OwnedNodes with the Model as owner.
        for (std::vector< Variable * >::iterator it = eliminated_z.begin(); it != eliminated_z.end(); ++it) {
            delete *it;
            *it = NULL;
        }         
    }        
    /** Evaluate the value of a parameter */
    double get(std::string varName);
    /** Evaluate the value of multiple parameters */
    std::vector<double> get(const std::vector<std::string> &varNames);

    /** Set the binding expression of a parameter to a value */
    void set(std::string varName, double value);
    /** Set the binding expressions of a number of parameters to a values */
    void set(const std::vector<std::string> &varNames,
        const std::vector<double> &values);

    /** @param A MX */
    void setTimeVariable(casadi::MX timeVar);
    /** @return A MX, this Model's time variable */
    casadi::MX getTimeVariable();

    /** 
        * Variables are assigned a default VariableType if they do not have one set. 
        * @param A pointer to a Variable. 
        */
    void addVariable(Ref<Variable> var);
    /** @param A pointer to an equation */    
    void addInitialEquation(Ref<Equation> eq);
    /** @param A pointer to an equation */ 
    virtual void addDaeEquation(Ref<Equation> eq);
    /** @param A pointer to a ModelFunction */
    void setModelFunctionByItsName(Ref<ModelFunction> mf);
    /** 
        * Adds a new VariableType. VariableTypes are singletons and all variable 
        * types must have unique names.
        * @param A reference to a VariableType
        */
    void addNewVariableType(Ref<VariableType> variableType);

    /** 
        * @param The name of the type
        * @return A reference to a VariableType, a reference to NULL if not present. 
        * */
    Ref<VariableType> getVariableType(std::string typeName) const;

    /** 
        * Get a vector of pointers to variables of a specific kind, as defined in 
        * the VariableKind enum.
        * @param A VariableKind enum
        * @return An std::vector of pointers to Variables
        */
    std::vector< Ref<Variable> > getVariables(VariableKind kind);

    /** @return A vector of pointers to Variables. */
    std::vector< Ref<Variable> > getAllVariables();

    /** @return A vector of pointers to all model variables (i.e. that haven't been aliaseliminated). */
    std::vector< Ref<Variable> > getModelVariables();
    /** @return A vector of pointers to all alias variables in the model. */
    std::vector< Ref<Variable> > getAliases();

    /**
        * Returns the Variable with a certain name in the Model.
        * If there is no variable with the name present NULL is returned.
        * This method does not discriminate between alias variables and
        * an alias variable may be returned.
        * @param String name of a Variable
        * @return A pointer to a Variable
        */
    Ref<Variable> getVariable(std::string name);

    /**
        * Returns the Variable with a certain name in the Model.
        * If there is no variable with the name present NULL is returned.
        * This method does discriminate between alias variables and if the
        * provided name is an alias variable its alias is returned instead. 
        * @param String name of a Variable
        * @return A pointer to a Variable
        */
    Ref<Variable> getModelVariable(std::string name);


    /** Calculates values for dependent parameters */
    void calculateValuesForDependentParameters();
    /**
        * Calculates the value of the supplied expression. Assumes that the 
        * MX in the expression are either parameters or constants present
        * in the Model.
        * @param A MX
        * @return A double
        */
    double evaluateExpression(casadi::MX exp);        

    /** 
        * Returns all initial equations in a stacked MX on the form: lhs - rhs.
        * @return A MX.
        */
    const casadi::MX getInitialResidual() const; 
    /** 
        * Returns all DAE equations in a stacked MX on the form: lhs - rhs.
        * @return A MX.
        */
    virtual const casadi::MX getDaeResidual() const;
    
    

    virtual std::vector< Ref< Equation> > getDaeEquations() const;
    std::vector< Ref< Equation> > getInitialEquations() const;

    /** 
        * @param The name of the ModelFunction
        * @return A pointer to a ModelFunction. Returns NULL if not present 
        */
    Ref<ModelFunction> getModelFunction(std::string name) const; 

    /** @return string Model identifier, typically <packagename>_<classname> */
    std::string getIdentifier();

    /** Allows the use of operator << to print this class, through Printable. */
    virtual void print(std::ostream& os) const;
    
    /** Allows the use of operator << to print this class, through Printable. */
    virtual std::set<const Variable*> getBLTEliminateables() const;
    
    virtual void substituteAllEliminateables();
    
    virtual void eliminateAlgebraics();
    virtual std::vector< Ref<Variable> >  getEliminatedVariables();
    
    virtual void setBLT(Ref<BLTHandler> nblt){std::cout<<"BaseModel setBLT should not be called\n.";}
    
    virtual void transferBLT(const std::vector< Ref<Block> >& nblt){equationContainer_->transferBLT(nblt);}

    /** Notify the Model that dependent parameters and attributes may need to be recalculated. */
    void setDirty() { dirty = true; }
    
    /** Notify the Model if it has a BLT for DAE equations **/
    virtual bool hasBLT() const;
    
    void addEntryToNodeVariableMap(const casadi::SharedObjectNode* node, const Variable* var)
    {mxnodeToVariable.insert(std::pair<const casadi::SharedObjectNode*, const Variable*>(node,var));}
    
    const std::map<const casadi::SharedObjectNode*, const Variable* >& getNodeToVariableMap() const {return mxnodeToVariable;}
    
    virtual void setEquationContainer(Ref<EquationContainer> eqCont);

    MODELICACASADI_SHAREDNODE_CHILD_PUBLIC_DEFS
    protected:
    /// Identifier, typically <packagename>_<classname>
    std::string identifier;
    /// The MX for independent parameters and constants. Filled by calculateValuesForDependentParameters.
    std::vector<casadi::MX> paramAndConstMXVec;
    /// The values for independent parameters and constants. Filled by calculateValuesForDependentParameters. 
    std::vector<double> paramAndConstValVec;
    casadi::MX timeVar;
    /// Vector containing pointers to all variables.
    std::vector< Variable * > z; 
    /// Vector containing pointers to all variables.
    std::vector< Variable * > eliminated_z;
    /// Vector containing pointers to all initial equations
    std::vector< Ref<Equation> > initialEquations; 
    /// A map for ModelFunction, key is ModelFunction's name.
    functionMap modelFunctionMap;  
    /// Indicates whether any parameter values have been updated since
    /// dependent parameters were last recalculated.
    bool dirty;
    /// For classification according to the VariableKind enum. Differentiated variables may have their 
    /// myDerivativeVariable field set in the process. 
    VariableKind classifyVariable(Ref<Variable> var) const; 
    VariableKind classifyInternalRealVariable(Ref<Variable> var) const; 
    VariableKind classifyInternalIntegerVariable(Ref<Variable> var) const; 
    VariableKind classifyInternalBooleanVariable(Ref<Variable> var) const; 
    VariableKind classifyInternalStringVariable(Ref<Variable> var) const; 
    VariableKind classifyInputVariable(Ref<Variable> var) const;
    VariableKind classifyInternalVariable(Ref<Variable> var) const;

    bool checkIfRealVarIsReferencedAsStateVar(Ref<RealVariable> var) const;
    /// May assign derivative variable to a state variable.
    bool isDifferentiated(Ref<RealVariable>  var) const;

    /// Adds the MX and their values for independent parameters and constants to paramAndConst(Val/MX)Vec
    void setUpValAndSymbolVecs();
    ///  Tries to evaluate the expression exp using values and nodes in paramAnd(ConstMX/Val)Vec
    double evalMX(casadi::MX exp);

    typeMap typesInModel;
    void assignVariableTypeToRealVariable(Ref<Variable> var);
    void assignVariableTypeToIntegerVariable(Ref<Variable> var);
    void assignVariableTypeToBooleanVariable(Ref<Variable> var);
    void handleVariableTypeForAddedVariable(Ref<Variable> var);
    void assignVariableTypeToVariable(Ref<Variable> var);
    
    //Map to build the blocks with CasADiInterface Variables 
    std::map<const casadi::SharedObjectNode*, const Variable* > mxnodeToVariable;
    Ref<EquationContainer> equationContainer_;
};
inline void BaseModel::initializeModel(std::string identifier) {
    this->identifier = identifier;
}
inline void BaseModel::setTimeVariable(casadi::MX timeVar) {this->timeVar = timeVar;}
inline casadi::MX BaseModel::getTimeVariable() {return timeVar;}
inline std::string BaseModel::getIdentifier() { return identifier; }

inline Ref<VariableType> BaseModel::getVariableType(std::string typeName) const { 
    return typesInModel.find(typeName) != typesInModel.end() ? 
        typesInModel.find(typeName)->second : 
        Ref<VariableType>(); 
}
inline void BaseModel::setModelFunctionByItsName(Ref<ModelFunction> mf) { modelFunctionMap[mf->getName()] = mf; }
inline Ref<ModelFunction> BaseModel::getModelFunction(std::string name) const { 
    return modelFunctionMap.find(name) != modelFunctionMap.end() ? 
        modelFunctionMap.find(name)->second :
        NULL; 
}
inline void BaseModel::addInitialEquation(Ref<Equation>eq) { initialEquations.push_back(eq); }
inline std::vector< Ref< Equation> > BaseModel::getInitialEquations() const { return initialEquations; }

}; // End namespace
#endif