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

#include "Model.hpp"

using casadi::MX; using casadi::MXFunction; 
using std::vector; using std::ostream;
using std::string; using std::pair;

namespace ModelicaCasADi{

const MX Model::getDaeResidual() const {
    MX daeRes;
    for (vector< Ref<Equation> >::const_iterator it = daeEquations.begin(); it != daeEquations.end(); ++it) {
        daeRes.append((*it)->getResidual());
    }
    return daeRes;
}

template <class T> 
void printVector(std::ostream& os, const std::vector<T> &makeStringOf) {
    typename std::vector<T>::const_iterator it;
    for ( it = makeStringOf.begin(); it < makeStringOf.end(); ++it) {
         os << **it << "\n";
    }
}

void Model::print(std::ostream& os) const {
//    os << "Model<" << this << ">"; return;

    using std::endl;
    os << "------------------------------- Variables -------------------------------\n" << endl;
    if (!timeVar.isEmpty()) {
        os << "Time variable: ";
        timeVar.print(os);
        os << endl;
    }
    printVector(os, z);
    os << "\n---------------------------- Variable types  ----------------------------\n" << endl;
    for (Model::typeMap::const_iterator it = typesInModel.begin(); it != typesInModel.end(); ++it) {
            os << it->second << endl;
    }
    os << "\n------------------------------- Functions -------------------------------\n" << endl;
    for (Model::functionMap::const_iterator it = modelFunctionMap.begin(); it != modelFunctionMap.end(); ++it){
            os << it->second << endl;
    }
    os << "\n------------------------------- Equations -------------------------------\n" << endl;
    if (!initialEquations.empty()) {
        os << " -- Initial equations -- \n";
        printVector(os, initialEquations);
    }
    if (!daeEquations.empty()) {
        os << " -- DAE equations -- \n";
        printVector(os, daeEquations);
    }
    os << endl;
}
}; // End namespace
