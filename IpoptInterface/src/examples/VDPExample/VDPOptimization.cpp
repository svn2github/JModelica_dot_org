#include "VDPOptimization.hpp"

VDPOptimization::VDPOptimization()
:
SimultaneousInterface(),
model_(NULL), // TODO: Is this one really needed?
modelInitialized_(false)
{
}

VDPOptimization::~VDPOptimization()
{
}

/**
 * getDimension returns the number of variables and the number of
 * constraints, respectively, in the problem.
 */
bool VDPOptimization::getDimensionsImpl(int& nVars, int& nEqConstr, int& nIneqConstr,
                                  int& nNzJacEqConstr, int& nNzJacIneqConstr) {

	ModelInterface* model;
	getModelImpl(model);
	
	int nStates = model->getNumStates();
	int nDerivatives = model->getNumDerivatives();
	int nInputs = model->getNumInputs();
	int nOutputs = model->getNumOutputs();
	int nAlgebraic = model->getNumAlgebraic();
	int nEqns = model->getNumEqns();

	// This model uses a hard coded backward euler scheme with N elements
	int nEl = getNumEl();
			
	nVars = (nEl+1)*nStates + nEl*(nDerivatives + nInputs + nOutputs + nAlgebraic);
	
	// This problem has no constraints apart from the equalit constraint resulting from
	// transcribed dynamical system
	nEqConstr = nEl*nEqns + // Equations for the differential equation
	            nEl*nDerivatives + // Equations for the backward Euler approximation
	            nStates; // Equations for the initial conditions
	
	nIneqConstr = 0;
	
	nNzJacEqConstr = nEl*nEqns*(nStates + nDerivatives + nInputs + nOutputs + nAlgebraic) + // Collocation of residuals
	                 nEl*3*nDerivatives + // Backward euler approximation of derivatives
	                 nStates; // initial conditions
	nNzJacIneqConstr = 0;
	
	return true;
}

bool VDPOptimization::getModelImpl(ModelInterface* model) {
 
	if (!modelInitialized_) {
    	model_ = new VDPModel();
    	modelInitialized_ = true;
    }
    model = model_;
	return true;

}

bool VDPOptimization::getNumElImpl(int& nEl) {
	nEl = 100;
	return true;
}

bool VDPOptimization::getMeshImpl(double* mesh) {
	int nEl;
	getNumElImpl(nEl);
	for (int i=0;i<nEl;i++) {
		mesh[i] = 1/nEl;
	}
	return true;
}

/**
 * evalCost returns the cost function value at a given point in search space.
 */
bool VDPOptimization::evalCostImpl(const double* x, double& f) {

	ModelInterface* model = getModel();
	
	int nStates = model->getNumStates();
	int nDerivatives = model->getNumDerivatives();
	int nInputs = model->getNumInputs();
	int nOutputs = model->getNumOutputs();
	int nAlgebraic = model->getNumAlgebraic();
//	int nEqns = model->getNumEqns();

	int N = getNumEl();
	
	// Find x_3(t_f)
	f = x[(nStates + (N-1)*(nStates + nDerivatives + nInputs + nOutputs + nAlgebraic) + nStates - 1) - 1];
	return true;

}

/**
 * evalGradCost returns the gradient of the cost function value at
 * a given point in search space.
 */
bool VDPOptimization::evalGradCostImpl(const double* x, double* grad_f) {

	ModelInterface* model = getModel();
	
	int nStates = model->getNumStates();
	int nDerivatives = model->getNumDerivatives();
	int nInputs = model->getNumInputs();
	int nOutputs = model->getNumOutputs();
	int nAlgebraic = model->getNumAlgebraic();
//	int nEqns = model->getNumEqns();
	
	int nEl = getNumEl();
	
	grad_f[(nStates + (nEl-1)*(nStates + nDerivatives + nInputs + nOutputs + nAlgebraic) + nStates - 1) - 1] = 1;

	return true;

}

/**
 * evalEqConstraints returns the residual of the equality constraints
 */
bool VDPOptimization::evalEqConstraintImpl(const double* x, double* gEq) {

	ModelInterface* model = getModel();
	
	int nStates = model->getNumStates();
	int nDerivatives = model->getNumDerivatives();
	int nInputs = model->getNumInputs();
//	int nOutputs = model->getNumOutputs();
	int nAlgebraic = model->getNumAlgebraic();
//	int nEqns = model->getNumEqns();
		
	int nEl = getNumEl();
	
	const double* h = getMesh();
	
	// Evaluate the Collocation residuals
	double* _x = NULL;
	double* xInit = NULL;
	double* dx = NULL;
	double* p = NULL;
	double* u = NULL;
	double* y = NULL;
	double* z = NULL;
	
	model->getInitial(xInit,dx,p,u,y,z);
	
	double* gEqPtr = gEq;
	
	for (int i=0;i<nEl;i++) {
		
		_x = (double*) x + nStates + (nStates + nDerivatives + nInputs + nAlgebraic)*i;
		dx = (double*)x + nStates + (nStates + nDerivatives + nInputs + nAlgebraic)*i + nStates;
		u = (double*)x + nStates + (nStates + nDerivatives + nInputs + nAlgebraic)*i + nStates + nDerivatives;
		z = (double*)x + nStates + (nStates + nDerivatives + nInputs + nAlgebraic)*i + nStates + nDerivatives + nInputs;
	
		gEqPtr += (nStates + nAlgebraic);
		model->evalDAEResidual(_x, dx, p, u, y,  z, gEqPtr);
		
	}

	// Evaluate the equations for the derivatives
		
	for (int i=0;i<nEl;i++) {
		_x = (double*)x + nStates + (nStates + nDerivatives + nInputs + nAlgebraic)*i;
		dx = (double*)x + nStates + (nStates + nDerivatives + nInputs + nAlgebraic)*i + nStates;
		
		for (int j=0;j<nStates;j++) {
			gEqPtr[j] = dx[j] - (_x[j] - _x[j-nStates])/h[i];
		}
		gEqPtr += nStates;
		
	}
	
	// Evaluate the equations for the initial conditions
	for (int j=0;j<nStates;j++) {
		gEqPtr[j] = x[j] - xInit[j];
	}
	
	return true;
}

/**
 * evalJacEqConstraints returns the Jacobian of the residual of the
 * equality constraints.
 */
bool VDPOptimization::evalJacEqConstraintImpl(const double* x, double* jac_gEq) {

	return true;
}

/**
 * evalIneqConstraints returns the residual of the inequality constraints g(x)<=0
 */
bool VDPOptimization::evalIneqConstraintImpl(const double* x, double* gIneq) {

	return true;
}

/**
 * evalJacIneqConstraints returns Jacobian of the residual of the
 * inequality constraints g(x)<=0
 */
bool VDPOptimization::evalJacIneqConstraintImpl(const double* x, double* jac_gIneq) {
	return 1;
}

/**
 * getBounds returns the upper and lower bounds on the optimization variables.
 */
bool VDPOptimization::getBoundsImpl(double* x_lb, double* x_ub) {

	int nVars;
	int nEqConstr;
	int nIneqConstr;
	int nNzJacEqConstr;
	int nNzJacIneqConstr;
	
	getDimensionsImpl(nVars, nEqConstr, nIneqConstr, nNzJacEqConstr, nNzJacIneqConstr);

	// Set wide bounds. TODO: check what the values are to make IPOPT ignore them
	for (int i=0; i<=nVars; i++) {
		x_lb[i] = 1e-20;
		x_ub[i] = 1e20;
	}

	return true;
	
}

/**
 * getInitial returns the initial point.
 */
bool VDPOptimization::getInitialImpl(double* xInit){

	int nVars;
	int nEqConstr;
	int nIneqConstr;
	int nNzJacEqConstr;
	int nNzJacIneqConstr;
	
	getDimensionsImpl(nVars, nEqConstr, nIneqConstr, nNzJacEqConstr, nNzJacIneqConstr);

	// Initialize everything to zero
	for (int i=0; i<=nVars; i++) {
		xInit[i] = 0;
	}
	
	return true;
}

/** 
 * getEqConstraintNzElements returns the indices of the non-zeros in the 
 * equality constraint Jacobian.
 */
bool VDPOptimization::getJacEqConstraintNzElementsImpl(int* rowIndex, int* colIndex) {
	ModelInterface* model = getModel();
	
	int nStates = model->getNumStates();
	int nDerivatives = model->getNumDerivatives();
	int nInputs = model->getNumInputs();
//	int nOutputs = model->getNumOutputs();
	int nAlgebraic = model->getNumAlgebraic();
	int nEqns = model->getNumEqns();
	
	int nEl = getNumEl();
	
	int _xIndex = 0;
	int dxIndex = 0;
	int uIndex = 0;
	int zIndex = 0;
	int eqnIndex = 0;
	int _colIndex = 0;
	int _rowIndex = 0;
	
	// Set sparsity pattern for DAE residuals
	for (int i=0;i<nEl;i++) {
		_xIndex = nStates + (nStates + nDerivatives + nInputs + nAlgebraic)*i;
		dxIndex = nStates + (nStates + nDerivatives + nInputs + nAlgebraic)*i + nStates;
		uIndex = nStates + (nStates + nDerivatives + nInputs + nAlgebraic)*i + nStates + nDerivatives;
		zIndex = nStates + (nStates + nDerivatives + nInputs + nAlgebraic)*i + nStates + nDerivatives + nInputs;
		eqnIndex = nEqns*i;
		
		for (int j=0;j<nStates;j++) {
			for (int k=0;k<nEqns;k++) {
				rowIndex[_rowIndex++] = eqnIndex + k +1;
				colIndex[_colIndex++] = _xIndex + j +1;
			}
		}

		for (int j=0;j<nDerivatives;j++) {
			for (int k=0;k<nEqns;k++) {
				rowIndex[_rowIndex++] = eqnIndex + k + 1;
				colIndex[_colIndex++] = dxIndex + j + 1;
			}
		}

		for (int j=0;j<nInputs;j++) {
			for (int k=0;k<nEqns;k++) {
				rowIndex[_rowIndex++] = eqnIndex + k + 1;
				colIndex[_colIndex++] = uIndex + j + 1;
			}
		}

		for (int j=0;j<nAlgebraic;j++) {
			for (int k=0;k<nEqns;k++) {
				rowIndex[_rowIndex++] = eqnIndex + k + 1;
				colIndex[_colIndex++] = zIndex + j + 1;
			}
		}

	}
    
	// Set sparsity pattern for derivative approximations
	
	for (int i=0;i<nEl;i++) {
		
		_xIndex = nStates + (nStates + nDerivatives + nInputs + nAlgebraic)*i;
		dxIndex = nStates + (nStates + nDerivatives + nInputs + nAlgebraic)*i + nStates;
		uIndex = nStates + (nStates + nDerivatives + nInputs + nAlgebraic)*i + nStates + nDerivatives;
		zIndex = nStates + (nStates + nDerivatives + nInputs + nAlgebraic)*i + nStates + nDerivatives + nInputs;
		eqnIndex += nEqns;

		if (i==0) {
			for (int j=0;j<nDerivatives;j++) {
				rowIndex[_rowIndex++] = eqnIndex + j + 1;
				colIndex[_colIndex++] = _xIndex - nStates + j + 1;		
			}
		} else {
			for (int j=0;j<nDerivatives;j++) {
				rowIndex[_rowIndex++] = eqnIndex + j + 1;
				colIndex[_colIndex++] = _xIndex - nStates -nDerivatives - nInputs - nAlgebraic + j + 1;		
			}			
		}
		
		for (int j=0;j<nStates;j++) {
				rowIndex[_rowIndex++] = eqnIndex + j + 1;
				colIndex[_colIndex++] = _xIndex + j + 1;
		}

		for (int j=0;j<nDerivatives;j++) {
				rowIndex[_rowIndex++] = eqnIndex + j + 1;
				colIndex[_colIndex++] = dxIndex + j + 1;
		}

	}

	eqnIndex += nEqns;

	for (int j=0;j<nStates;j++) {
		rowIndex[_rowIndex++] = eqnIndex + j + 1;
		colIndex[_colIndex++] = j + 1;		
	}
	
	return true;

}

/** 
 * getIneqConstraintElements returns the indices of the non-zeros in the 
 * inequality constraint Jacobian.
 */
bool VDPOptimization::getJacIneqConstraintNzElementsImpl(int* rowIndex, int* colIndex) {

	// No inequality constraints.
	return true;
	
}
