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

#ifndef _MODELICACASADI_BLOCK
#define _MODELICACASADI_BLOCK

#include <iostream>
#include "casadi/casadi.hpp"
#include "Variable.hpp"
#include "RealVariable.hpp"
#include "Equation.hpp"
#include "RefCountedNode.hpp"
#include <vector>
#include <set>
#include <map>
#include <utility>
#include <string>
#include <assert.h>



namespace ModelicaCasADi 
{

class Block : public RefCountedNode{
    public:
    //Default constructor
    Block(): simple_flag(false),linear_flag(false),solve_flag(false){}
    
    /***************************TO BE REMOVE*******************************/
    //Might be kept
    std::vector< casadi::MX > variablesVector() const;
    /**********************************************************************/
    
    
    /**************VariablesMethods*************/
    int getNumVariables()const {return variables_.size();}
    int getNumUnsolvedVariables() const {return unSolvedVariables_.size();}
    int getNumExternalVariables() const {return externalVariables_.size();}
    int getVariableIndex(const Variable* var);
    const std::set<const Variable*>& variables() const;
    const std::set<const Variable*>& unsolvedVariables() const;
    const std::set<const Variable*>& externalVariables() const;
    bool isExternal(const Variable* var) const;
    bool removeSolutionOfVariable(const Variable* var);
    std::map<const Variable*, casadi::MX> getSolutionMap() const;
    casadi::MX getSolutionOfVariable(const Variable* var) const;
    bool hasSolution(const Variable*) const;
    void addVariable(const Variable* var, bool solvable);
    void addExternalVariable(const Variable* var);
    std::set<const Variable*> eliminateableVariables() const;
    void addSolutionToVariable(const Variable* var, casadi::MX sol);
    /*******************************************/
    
    /**************EquationMethods*************/
    int getNumEquations() const {return equations.size();}
    int getNumUnsolvedEquations() const {return unSolvedEquations.size();}
    std::vector< Ref<Equation> > allEquations() const;
    std::vector< Ref<Equation> > notSolvedEquations() const;
    void addEquation(Ref<Equation> eq, bool solvable);
    std::vector< Ref<Equation> > getEquationsforModel() const;
    /*******************************************/
    
    
    /**************AuxiliaryMethods*************/
    void setJacobian(const casadi::MX& jac);
    casadi::MX computeJacobianCasADi();
    void printBlock(std::ostream& out, bool withData=false) const;
    void checkLinearityWithJacobian();
    
    bool isSimple() const;
    bool isLinear() const;
    bool isSolvable() const;
    bool setasSimple(bool flag){simple_flag=flag;}
    bool setasLinear(bool flag){linear_flag=flag;}
    bool setasSolvable(bool flag){solve_flag=flag;}
    
    //Requires the jacobian to be computed in beforehand
    void solveLinearSystem();
    void substitute(const std::map<const Variable*, casadi::MX>& mapVariableToExpression);
    /*******************************************/

    
        
    MODELICACASADI_SHAREDNODE_CHILD_PUBLIC_DEFS
    private:
    
    // Vector containing pointers to block equations
    std::vector< Ref<Equation> > equations;
    // Vector containing pointers to block unsolved equations
    std::vector< Ref<Equation> > unSolvedEquations;
    
    // Vector containing pointers to block solved variables
    std::set< const Variable* > variables_;
    // Vector containing pointers to block unsolved variables
    std::set< const Variable* > unSolvedVariables_;
    //External variables
    std::set< const Variable* > externalVariables_;
    
    // Map with solution of variables
    std::map< const Variable* ,casadi::MX> variableToSolution_;
    
    // Map with variable names to index for jacobian computation
    std::map<const Variable*,int> variableToIndex_;
    void addIndexToVariable(const Variable* var);
    
    
    //The jacobian stuff must be more efficiently implemented
    casadi::MX jacobian;
    //For handling jacobian with casadi
    casadi::MX symbolicVariables; 
    
    //Simple flag
    bool simple_flag;
    bool linear_flag;
    bool solve_flag;

};

inline void Block::setJacobian(const casadi::MX& jac){jacobian = jac;}
inline bool Block::isSimple() const {return simple_flag;}
inline bool Block::isLinear() const {return linear_flag;}
inline bool Block::isSolvable() const {return solve_flag;}

inline void Block::addVariable(const Variable* var, bool solvable){
  addIndexToVariable(var);
  variables_.insert(var);
  if(!solvable){unSolvedVariables_.insert(var);}
}

inline void Block::addExternalVariable(const Variable* var){externalVariables_.insert(var);}

inline void Block::addSolutionToVariable(const Variable* var, casadi::MX sol){
  std::map< const Variable* ,casadi::MX>::iterator it =variableToSolution_.find(var);
  if(it==variableToSolution_.end()){
    variableToSolution_.insert(std::pair<const Variable*, casadi::MX>(var,sol));
  }
  else{
    std::cout<<"Warning: The variable "<<(it->first)->getVar()<<" has already a solution "<<it->second;
  }
}

inline bool Block::removeSolutionOfVariable(const Variable* var){
  std::map< const Variable* ,casadi::MX>::iterator it =variableToSolution_.find(var);
  if(it!=variableToSolution_.end()){
      variableToSolution_.erase(it);
      return 1;
  }
  return 0;  
}

inline std::map<const Variable*, casadi::MX> Block::getSolutionMap() const{
  return std::map<const Variable*, casadi::MX>(variableToSolution_);
}

inline bool Block::hasSolution(const Variable* var) const{
  std::map<const Variable*, casadi::MX>::const_iterator it = variableToSolution_.find(var);
  return ((it!=variableToSolution_.end()) ? 1 : 0);
}

inline const std::set< const Variable* >& Block::variables() const{
  return variables_;
}  

inline const std::set< const Variable* >& Block::unsolvedVariables() const{
  return unSolvedVariables_;  
}

inline const std::set< const Variable* >& Block::externalVariables() const{
  return externalVariables_;  
}

inline bool Block::isExternal(const Variable* var) const{ 
  std::set< const Variable* >::iterator it = externalVariables_.find(var);
  if(it!=externalVariables_.end()){return 1;}
  else{return 0;}
}

inline void Block::checkLinearityWithJacobian(){
  if(!jacobian.isEmpty()){
    std::vector< casadi::MX > vars;
    for (std::set<const Variable*>::const_iterator it = variables_.begin(); 
        it != variables_.end(); ++it){
        vars.push_back((*it)->getVar());      
    }
    linear_flag = !casadi::dependsOn(jacobian,vars);
    if(!symbolicVariables.isEmpty()){
      linear_flag = !casadi::dependsOn(jacobian,std::vector< casadi::MX >(1,symbolicVariables));
    }
  }
}

inline std::vector< casadi::MX > Block::variablesVector() const{
  std::vector< casadi::MX > vars;
  for (std::set<const Variable*>::const_iterator it = variables_.begin(); 
      it != variables_.end(); ++it){
      vars.push_back((*it)->getVar());      
  }
  return vars;
}  

inline std::vector< Ref<Equation> > Block::allEquations() const{
  return std::vector< Ref<Equation> >(equations);  
}  

inline std::vector< Ref<Equation> > Block::notSolvedEquations() const{
  return std::vector< Ref<Equation> >(unSolvedEquations);  
} 

inline int Block::getVariableIndex(const Variable* var) {
  std::map<const Variable*,int>::iterator it = variableToIndex_.find(var);
  if(it!=variableToIndex_.end()){
    return it->second;   
  }
  else{
    //To change later
    std::cout<<"The variable was not found returning -1\n";
    return -1;
  }
}

inline void Block::addIndexToVariable(const Variable* var){
  std::set<const Variable*>::iterator it = variables_.find(var);
  if(it==variables_.end()){
      variableToIndex_.insert(std::pair<const Variable*, int>(var,variables_.size()));
  }
}

inline casadi::MX Block::getSolutionOfVariable(const Variable* var) const{
  std::map<const Variable*,casadi::MX>::const_iterator it = variableToSolution_.find(var);
  if(it!=variableToSolution_.end()){
    return it->second;   
  }
  else{
    // Returns empty variable (check nonEmpty at substitutions)
    return casadi::MX();
  }
}


}; // End namespace
#endif