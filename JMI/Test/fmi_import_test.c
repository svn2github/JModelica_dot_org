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

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>

#include <FMI1/fmi1_types.h>
#include <FMI1/fmi1_functions.h>
#include <Common/fmi_import_context.h>
#include <FMI1/fmi1_import.h>


void mylogger(jm_callbacks* c, jm_string module, jm_log_level_enu_t log_level, jm_string message)
{
        printf("module = %s, log level = %d: %s\n", module, log_level, message);
}

void do_exit(int code)
{
	printf("Press 'Enter' to exit\n");
	getchar();
	exit(code);
}

char* fmi_status_to_string(fmi1_status_t fmistatus)
{
	switch (fmistatus) {
		case fmi1_status_ok:
			return "fmiOK";
		case fmi1_status_warning:
			return "fmiWarning";
		case fmi1_status_discard:
			return "fmiDiscard";
		case fmi1_status_error:
			return "fmiError";
		case fmi1_status_fatal:
			return "fmiFatal";
		case fmi1_status_pending:
			return "fmiPending";
		default:
			return "...are you even trying?";
	}
}

int test_simulate_me(fmi1_import_t* fmu)
{	
	fmi1_status_t fmistatus;
	jm_status_enu_t jmstatus;
	fmi1_real_t tstart = 0.0;
	fmi1_real_t tcur;
	fmi1_real_t hstep = 0.1;
	fmi1_real_t tend = 2.0;
	size_t n_states;
	size_t n_event_indicators;
	fmi1_real_t* states;
	fmi1_real_t* states_der;
	fmi1_real_t* event_indicators;
	fmi1_real_t* event_indicators_prev;
	fmi1_boolean_t callEventUpdate;
	fmi1_boolean_t toleranceControlled = fmi1_true;
	fmi1_real_t relativeTolerance = 0.001;
	fmi1_event_info_t eventInfo;
	fmi1_boolean_t intermediateResults = fmi1_false;

	printf("Version returned from FMU:   %s\n", fmi1_import_get_version(fmu));
	printf("Platform type returned:      %s\n", fmi1_import_get_model_types_platform(fmu));

	n_states = fmi1_import_get_number_of_continuous_states(fmu);
	n_event_indicators = fmi1_import_get_number_of_event_indicators(fmu);

	states = calloc(n_states, sizeof(double));
	states_der = calloc(n_states, sizeof(double));
	event_indicators = calloc(n_event_indicators, sizeof(double));
	event_indicators_prev = calloc(n_event_indicators, sizeof(double));

	jmstatus = fmi1_import_instantiate_model(fmu, "Test model instance", fmi1_import_get_GUID(fmu), fmi1_true);
	if (jmstatus == jm_status_error) {
		printf("fmi1_import_instantiate_model failed\n");
		do_exit(1);
	}

	fmistatus = fmi1_import_set_debug_logging(fmu, fmi1_false);
	printf("fmi1_import_set_debug_logging:  %s\n", fmi_status_to_string(fmistatus));	

	fmistatus = fmi1_import_set_time(fmu, tstart);

	fmistatus = fmi1_import_initialize(fmu, toleranceControlled, relativeTolerance, &eventInfo);

	fmistatus = fmi1_import_get_continuous_states(fmu, states, n_states);
	fmistatus = fmi1_import_get_event_indicators(fmu, event_indicators_prev, n_event_indicators);

	tcur = tstart;
	callEventUpdate = fmi1_false;

	while (tcur < tend) {
		size_t k;
		int zero_crossning_event = 0;

		fmistatus = fmi1_import_set_time(fmu, tcur);
		fmistatus = fmi1_import_get_event_indicators(fmu, event_indicators, n_event_indicators);

		/* Check if an event inidcator has triggered */
		for (k = 0; k < n_event_indicators; k++) {
			if (event_indicators[k]*event_indicators_prev[k] < 0) {
				zero_crossning_event = 1;
				break;
			}
		}

		/* Handle any events */
		if (callEventUpdate || zero_crossning_event || (eventInfo.upcomingTimeEvent && tcur == eventInfo.nextEventTime)) {
			fmistatus = fmi1_import_eventUpdate(fmu, intermediateResults, &eventInfo);
			fmistatus = fmi1_import_get_continuous_states(fmu, states, n_states);
			fmistatus = fmi1_import_get_event_indicators(fmu, event_indicators, n_event_indicators);
			fmistatus = fmi1_import_get_event_indicators(fmu, event_indicators_prev, n_event_indicators);
		}

		/* Integrate a step */
		fmistatus = fmi1_import_get_derivatives(fmu, states_der, n_states);
		for (k = 0; k < n_states; k++) {
			states[k] = states[k] + hstep*states_der[k];
		}
		

		/* Set states */
		fmistatus = fmi1_import_set_continuous_states(fmu, states, n_states);
		/* Step is complete */
		fmistatus = fmi1_import_completed_integrator_step(fmu, &callEventUpdate);

		/* Updated next time step */
		if (eventInfo.upcomingTimeEvent) {
			if (tcur + hstep < eventInfo.nextEventTime) {
				tcur += hstep;
			} else {
				tcur +=eventInfo.nextEventTime;
			}
		} else {
			tcur += hstep;
		}
	}	

	fmistatus = fmi1_import_terminate(fmu);

	fmi1_import_free_model_instance(fmu);
}


int test_simulate_cs(fmi1_import_t* fmu)
{
	return 0;
}

int main(int argc, char *argv[])
{
	fmi1_callback_functions_t callBackFunctions;
	const char* FMUPath;
	const char* tmpPath;
	const char* dllPath;
	const char* modelIdentifier;
	const char* modelName;
	const char* model_description_path;
	const char* instanceName;
	const char*  GUID;
	jm_callbacks callbacks;
	fmi_import_context_t* context;
	fmi_version_enu_t version;
	jm_status_enu_t status;
	fmi1_fmu_kind_enu_t fmi_standard = fmi1_fmu_kind_enu_me;

	fmi1_import_t* fmu;

	if(argc < 3) {
		printf("Usage: %s <fmu_file> <temporary_dir>\n", argv[0]);
		do_exit(1);
	}

	FMUPath = argv[1];
	tmpPath = argv[2];


	callbacks.malloc = malloc;
    callbacks.calloc = calloc;
    callbacks.realloc = realloc;
    callbacks.free = free;
    callbacks.logger = mylogger;
    callbacks.context = 0;

	callBackFunctions.logger = mylogger;
	callBackFunctions.allocateMemory = calloc;
	callBackFunctions.freeMemory = free;


	context = fmi_import_allocate_context(&callbacks);

	version = fmi_import_get_fmi_version(context, FMUPath, tmpPath);

	if(version != fmi_version_1_enu) {
		printf("Only version 1.0 is supported so far\n");
		do_exit(1);
	}

	fmu = fmi1_import_parse_xml(context, tmpPath);

	if(!fmu) {
		printf("Error parsing XML, exiting\n");
		do_exit(1);
	}
	modelIdentifier = fmi1_import_get_model_identifier(fmu);
	modelName = fmi1_import_get_model_name(fmu);
	GUID = fmi1_import_get_GUID(fmu);

	printf("Model name: %s\n", modelName);
    printf("Model identifier: %s\n", modelIdentifier);
    printf("Model GUID: %s\n", GUID);

	status = fmi1_import_create_dllfmu(fmu, callBackFunctions, fmi_standard, tmpPath);
	if (status == jm_status_error) {
		printf("Could not create the DLL loading mechanism(C-API).\n");
		do_exit(1);
	}

	status = fmi1_import_load_dll(fmu);
	if (status == jm_status_error) {
		printf("Could not load the dll handle\n");
		do_exit(1);
	}

	status = fmi1_import_load_fcn(fmu);  
	if (status == jm_status_error) {
		printf("Could not load the dll functions\n");
		do_exit(1);
	}

	if (fmi_standard == fmi1_fmu_kind_enu_me) {
		test_simulate_me(fmu);
	} else {
		test_simulate_cs(fmu);
	}	

	fmi1_import_free(fmu);
	fmi_import_free_context(context);
	
	printf("Everything seems to be OK since you got this far=)!\n");

	do_exit(0);
}


