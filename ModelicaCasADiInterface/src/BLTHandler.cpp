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

#include "BLTHandler.hpp"
#include <iomanip>
#include <iostream>

namespace ModelicaCasADi
{
    void BLTHandler::printBLT(std::ostream& out, bool with_details/*=false*/) const
    {
        int i=0;
        for(std::vector< Ref<Block> >::const_iterator it=blt.begin();
            it!=blt.end();++it){
                out << "Block[" <<i<<"]\n";
                (*it)->printBlock(out,with_details);
                ++i;
        }
    }
    
    //With variables
    std::set<const Variable*> BLTHandler::eliminatableVariables() const{
        std::set<const Variable*> vars;
        for(std::vector< Ref<Block> >::const_iterator it=blt.begin();
            it!=blt.end();++it){
            std::set<const Variable*> blockVars = (*it)->eliminateableVariables();
            vars.insert(blockVars.begin(), blockVars.end());
        }
        return vars;
    }
    
    std::vector< Ref<Equation> > BLTHandler::writeEquationsforModel() const{
        std::vector< Ref<Equation> > modelEquations;
        for(std::vector< Ref<Block> >::const_iterator it=blt.begin();
            it!=blt.end();++it){
            std::vector< Ref<Equation> > blockEqs = (*it)->getEquationsforModel();
            modelEquations.reserve( modelEquations.size() + blockEqs.size() ); 
            modelEquations.insert( modelEquations.end(), blockEqs.begin(), blockEqs.end() );
        }
        return modelEquations;
    }
    
    void BLTHandler::removeSolutionOfVariable(const Variable* var){
        bool found=0;
        for(std::vector< Ref<Block> >::iterator it=blt.begin();
            it!=blt.end() && !found ;++it){
            if((*it)->removeSolutionOfVariable(var)){              
               found=1;         
            }
        }
        if(!found){std::cout<<"The variable "<<var->getName()<<" does not have a solution in BLT.\n";}
    }
    
    
    void BLTHandler::substitute(const std::map<const Variable*,casadi::MX>& substituteMap){
        for(std::vector< Ref<Block> >::iterator it=blt.begin();
            it!=blt.end();++it){
            (*it)->substitute(substituteMap);
        } 
    }
    
    void BLTHandler::getSubstitues(const std::set<const Variable*>& eliminateables, std::map<const Variable*,casadi::MX>& storageMap) const{
        
        for(std::set<const Variable*>::const_iterator it_e = eliminateables.begin(); 
              it_e != eliminateables.end(); ++it_e){
            bool found=0;
            casadi::MX tmp_subs;
            for(std::vector< Ref<Block> >::const_iterator it=blt.begin();
                it!=blt.end() && !found;++it){
                if((*it)->hasSolution(*it_e)){
                   casadi::MX exp = (*it)->getSolutionOfVariable(*it_e);
                   tmp_subs=exp;
                   found=1;
                }
            }
            
            //substitute previous variables in eliminateables
            if(storageMap.size()>0){
                if(found){
                    std::vector<casadi::MX> inner_subs;
                    std::vector<casadi::MX> inner_elim;
                    for(std::map<const Variable*,casadi::MX>::const_iterator it_prev=storageMap.begin(); it_prev!=storageMap.end();++it_prev){
                        int ndeps =tmp_subs.getNdeps();
                        for(int j=0;j<ndeps;++j){
                            if(tmp_subs.getDep(j).isEqual(it_prev->first->getVar(),0) && !it_prev->second.isEmpty()){
                                 inner_subs.push_back(it_prev->second);
                                 inner_elim.push_back(it_prev->first->getVar()); 
                            }
                        }
                    }
                    std::vector<casadi::MX> subExp = casadi::substitute(std::vector<casadi::MX>(1,tmp_subs),inner_elim,inner_subs);
                    storageMap.insert(std::pair<const Variable*,casadi::MX>(*it_e,subExp.front()));
                    inner_subs.clear();
                    inner_elim.clear();
                }
            }
            else{
               if(found){storageMap.insert(std::pair<const Variable*,casadi::MX>(*it_e,tmp_subs));} 
            }
            if(!found){
                //If the variable is empty the substitution in the block will be ignored
                std::cout<<"Warning: The variable "<< (*it_e)->getName() << "is not eliminateable. It will be ignore at the substitution.\n";
                storageMap.insert(std::pair<const Variable*,casadi::MX>(*it_e,casadi::MX()));
            }
        }
    }
    
    void BLTHandler::substituteAllEliminateables(){
        std::set<const Variable*> externalVars;
        std::map<const Variable*,casadi::MX> substitutionMap;
        for(std::vector< Ref<Block> >::iterator fit=blt.begin()+1;
            fit!=blt.end();++fit){
            externalVars = (*fit)->externalVariables();
            for(std::set<const Variable*>::const_iterator it_e = externalVars.begin(); 
              it_e != externalVars.end(); ++it_e){
                bool found =0;
                for(std::vector< Ref<Block> >::reverse_iterator rit(fit);rit!=blt.rend() && !found;++rit){
                    if((*rit)->hasSolution((*it_e))){
                        casadi::MX exp = (*rit)->getSolutionOfVariable((*it_e));
                        substitutionMap.insert(std::pair<const Variable*,casadi::MX>((*it_e),exp));
                        found=1;
                    }
                }
                if(!found){
                    //If the variable is empty the substitution in the block will be ignored
                    substitutionMap.insert(std::pair<const Variable*,casadi::MX>((*it_e),casadi::MX()));
                }
            }
            (*fit)->substitute(substitutionMap);
            substitutionMap.clear();
        }
    }
}; //End namespace