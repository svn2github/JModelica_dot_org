/*
    Copyright (C) 2012 Modelon AB

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

#include <FMI1/fmi1_capi.h>

fmi1_component_t fmi1_capi_instantiate_model(fmi1_capi_t* fmu, fmi1_string_t instanceName, fmi1_string_t GUID, fmi1_boolean_t loggingOn)
{
	return fmu->c = fmu->fmiInstantiateModel(instanceName, GUID, fmu->callBackFunctions, loggingOn);
}

void fmi1_capi_free_model_instance(fmi1_capi_t* fmu)
{
	fmu->fmiFreeModelInstance(fmu->c);
}

fmi1_status_t fmi1_capi_initialize(fmi1_capi_t* fmu, fmi1_boolean_t toleranceControlled, fmi1_real_t relativeTolerance, fmi1_event_info_t* eventInfo)
{
	return fmu->fmiInitialize(fmu->c, toleranceControlled, relativeTolerance, eventInfo);	
}

/* Call FMI function Macros */
#define CALL_FMI_FUNCTION_RETURN_STRING(functioncall) return functioncall;

#define CALL_FMI_FUNCTION_RETURN_FMISTATUS(functioncall) return functioncall;

const char* fmi1_capi_get_model_types_platform(fmi1_capi_t* fmu)
{
	CALL_FMI_FUNCTION_RETURN_STRING(fmu->fmiGetModelTypesPlatform());
}

fmi1_status_t fmi1_capi_set_time(fmi1_capi_t* fmu, fmi1_real_t time)
{
	CALL_FMI_FUNCTION_RETURN_FMISTATUS(fmu->fmiSetTime(fmu->c, time));
}

fmi1_status_t fmi1_capi_set_continuous_states(fmi1_capi_t* fmu, const fmi1_real_t x[], size_t nx)
{
	CALL_FMI_FUNCTION_RETURN_FMISTATUS(fmu->fmiSetContinuousStates(fmu->c, x, nx));
}

fmi1_status_t fmi1_capi_completed_integrator_step(fmi1_capi_t* fmu, fmi1_boolean_t* callEventUpdate)
{
	CALL_FMI_FUNCTION_RETURN_FMISTATUS(fmu->fmiCompletedIntegratorStep(fmu->c, callEventUpdate));
}

fmi1_status_t fmi1_capi_get_derivatives(fmi1_capi_t* fmu, fmi1_real_t derivatives[], size_t nx)
{
	CALL_FMI_FUNCTION_RETURN_FMISTATUS(fmu->fmiGetDerivatives(fmu->c, derivatives, nx));
}

fmi1_status_t fmi1_capi_get_event_indicators(fmi1_capi_t* fmu, fmi1_real_t eventIndicators[], size_t ni)
{
	CALL_FMI_FUNCTION_RETURN_FMISTATUS(fmu->fmiGetEventIndicators(fmu->c, eventIndicators, ni));
}

fmi1_status_t fmi1_capi_eventUpdate(fmi1_capi_t* fmu, fmi1_boolean_t intermediateResults, fmi1_event_info_t* eventInfo)
{
	CALL_FMI_FUNCTION_RETURN_FMISTATUS(fmu->fmiEventUpdate(fmu->c, intermediateResults, eventInfo));
}

fmi1_status_t fmi1_capi_get_continuous_states(fmi1_capi_t* fmu, fmi1_real_t states[], size_t nx)
{
	CALL_FMI_FUNCTION_RETURN_FMISTATUS(fmu->fmiGetContinuousStates(fmu->c, states, nx));
}

fmi1_status_t fmi1_capi_get_nominal_continuous_states(fmi1_capi_t* fmu, fmi1_real_t x_nominal[], size_t nx)
{
	CALL_FMI_FUNCTION_RETURN_FMISTATUS(fmu->fmiGetNominalContinuousStates(fmu->c, x_nominal, nx));
}

fmi1_status_t fmi1_capi_get_state_value_references(fmi1_capi_t* fmu, fmi1_value_reference_t vrx[], size_t nx)
{
	CALL_FMI_FUNCTION_RETURN_FMISTATUS(fmu->fmiGetStateValueReferences(fmu->c, vrx, nx));
}

fmi1_status_t fmi1_capi_terminate(fmi1_capi_t* fmu)
{
	CALL_FMI_FUNCTION_RETURN_FMISTATUS(fmu->fmiTerminate(fmu->c));
}
