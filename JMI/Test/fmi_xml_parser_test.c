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
#include <assert.h>
#include <time.h>
#include <FMI1/fmi1_xml_model_description.h>

void print_int(int i,void* data) {
    printf("%d\n", i);
}

void print_dbl(double d,void* data) {
    printf("%g\n", d);
}

void printTypeInfo(fmi1_xml_variable_typedef_t* vt) {
    const char* quan;

    if(!vt) {
        printf("No type definition\n");
        return;
    }

    quan = fmi1_xml_get_type_quantity(vt);

    printf("Type %s\n description: %s\n",  fmi1_xml_get_type_name(vt), fmi1_xml_get_type_description(vt));

    printf("Base type: %s\n", fmi1_xml_base_type2string(fmi1_xml_get_base_type(vt)));

    if(quan) {
        printf("Quantity: %s\n", quan);
    }
    switch(fmi1_xml_get_base_type(vt)) {
    case fmi1_xml_base_type_enu_real: {
        fmi1_xml_real_typedef_t* rt = fmi1_xml_ret_type_as_real(vt);
        fmi1_xml_real_t min = fmi1_xml_get_real_type_min(rt);
        fmi1_xml_real_t max = fmi1_xml_get_real_type_max(rt);
        fmi1_xml_real_t nom = fmi1_xml_get_real_type_nominal(rt);
        fmi1_xml_unit_t* u = fmi1_xml_get_real_type_unit(rt);
        fmi1_xml_display_unit_t* du = fmi1_xml_get_type_display_unit(rt);

        printf("Min %g, max %g, nominal %g\n", min, max, nom);

        if(u) {
            printf("Unit: %s\n", fmi1_xml_get_unit_name(u));
        }
        if(du) {
            printf("Display unit: %s, gain: %g, offset: %g, is relative: %s",
                   fmi1_xml_get_display_unit_name(du),
                   fmi1_xml_get_display_unit_gain(du),
                   fmi1_xml_get_display_unit_offset(du),
                   fmi1_xml_get_real_type_is_relative_quantity(rt)?"yes":"no"
                   );
        }

        break;
    }
    case fmi1_xml_base_type_enu_int:{
        fmi1_xml_integer_typedef_t* it = fmi1_xml_get_type_as_int(vt);
        int min = fmi1_xml_get_integer_type_min(it);
        int max = fmi1_xml_get_integer_type_max(it);
        printf("Min %d, max %d\n", min, max);
        break;
    }
    case fmi1_xml_base_type_enu_bool:{
        break;
    }
    case fmi1_xml_base_type_enu_str:{
        break;
    }
    case fmi1_xml_base_type_enu_enum:{
        fmi1_xml_enumeration_typedef_t* et = fmi1_xml_get_type_as_enum(vt);
        int min = fmi1_xml_get_enum_type_min(et);
        int max = fmi1_xml_get_enum_type_max(et);
        printf("Min %d, max %d\n", min, max);
        {
            size_t ni, i;
            ni = fmi1_xml_get_enum_type_size(et);
            printf("There are %d items \n",ni);
            for(i = 0; i < ni; i++) {
                printf("[%d] %s (%s) \n", i+1, fmi1_xml_get_enum_type_item_name(et, i), fmi1_xml_get_enum_type_item_description(et, i));
            }
        }
        break;
    }
    default:
        printf("Error in fmiGetBaseType()\n");
    }

}

void printVariableInfo(fmi1_xml_model_description_t* md,
                       fmi1_xml_variable_t* v) {
    fmi1_xml_base_type_enu_t bt;
    printf("Variable name: %s\n", fmi1_xml_get_variable_name(v));
    printf("Description: %s\n", fmi1_xml_get_variable_description(v));
    printf("VR: %d\n", fmi1_xml_get_variable_vr(v));
    printf("Variability: %s\n", fmi1_xml_variability_to_string(fmi1_xml_get_variability(v)));
    printf("Causality: %s\n", fmi1_xml_causality_to_string(fmi1_xml_get_causality(v)));

    bt = fmi1_xml_get_variable_base_type(v);
    printf("Base type: %s\n", fmi1_xml_base_type2string(bt));

    printTypeInfo(fmi1_xml_get_variable_declared_type(v));
    if(bt == fmi1_xml_base_type_enu_real) {
        fmi1_xml_real_variable_t *rv = fmi1_xml_get_variable_as_real(v);
        fmi1_xml_unit_t * u = fmi1_xml_get_real_variable_unit(rv);
        fmi1_xml_display_unit_t * du = fmi1_xml_get_real_variable_display_unit(rv);
        printf("Unit: %s, display unit: %s\n", u ? fmi1_xml_get_unit_name(u):0, du?fmi1_xml_get_display_unit_name(du):0);
    }

    if(fmi1_xml_get_variable_has_start(v)) {
        printf("There is a start value, fixed attribute is '%s'\n", (fmi1_xml_get_variable_is_fixed(v))?"true":"false");

        switch(fmi1_xml_get_variable_base_type(v)) {
        case fmi1_xml_base_type_enu_real: {
            fmi1_xml_real_variable_t *rv = fmi1_xml_get_variable_as_real(v);
            printf("start =%g\n", fmi1_xml_get_real_variable_start(rv));
            break;
        }
        case fmi1_xml_base_type_enu_int:{
            printf("start =%d\n", fmi1_xml_get_integer_variable_start(fmi1_xml_get_variable_as_integer(v)));
            break;
        }
        case fmi1_xml_base_type_enu_bool:{
            printf("start = %d\n", fmi1_xml_get_boolean_variable_start(fmi1_xml_get_variable_as_boolean(v)));
            break;
        }
        case fmi1_xml_base_type_enu_str:{
            printf("start = '%s'\n", fmi1_xml_get_string_variable_start(fmi1_xml_get_variable_as_string(v)));
            break;
        }
        case fmi1_xml_base_type_enu_enum:{
            printf("start = %d\n", fmi1_xml_get_enum_variable_start(fmI_xml_get_variable_as_enum(v)));
            break;
        }
        default:
            printf("Error in fmiGetBaseType()\n");
        }
    }
    if(fmi1_xml_get_variable_alias_kind(v) != fmi1_xml_variable_is_not_alias) {
        printf("The variable is aliased to %s\n",
               fmi1_xml_get_variable_name( fmi1_xml_get_variable_alias_base(md, v)));
    }
    else {
        printf("The variable is not an alias\n");
    }
    {
        fmi1_xml_variable_list_t* vl = fmi1_xml_get_variable_aliases(md, v);
        size_t i, n = fmi1_xml_get_variable_list_size(vl);
        if(n>1) {
            printf("Listing aliases: \n");
            for(i = 0;i<n;i++)
                printf("\t%s\n",fmi1_xml_get_variable_name(fmi1_xml_get_variable(vl, i)));
        }
        fmi1_xml_free_variable_list(vl);
    }
}

void printCapabilitiesInfo(fmi1_xml_capabilities_t* capabilities) {
    printf("canHandleVariableCommunicationStepSize = %u\n", fmi1_xml_get_canHandleVariableCommunicationStepSize(capabilities ));
    printf("canHandleEvents = %u\n", fmi1_xml_get_canHandleEvents(capabilities ));
    printf("canRejectSteps = %u\n", fmi1_xml_get_canRejectSteps(capabilities ));
    printf("canInterpolateInputs = %u\n", fmi1_xml_get_canInterpolateInputs(capabilities ));
    printf("maxOutputDerivativeOrder = %u\n", fmi1_xml_get_maxOutputDerivativeOrder(capabilities ));
    printf("canRunAsynchronuously = %u\n", fmi1_xml_get_canRunAsynchronuously(capabilities ));
    printf("canSignalEvents = %u\n", fmi1_xml_get_canSignalEvents(capabilities ));
    printf("canBeInstantiatedOnlyOncePerProcess = %u\n", fmi1_xml_get_canBeInstantiatedOnlyOncePerProcess(capabilities ));
    printf("canNotUseMemoryManagementFunctions = %u\n", fmi1_xml_get_canNotUseMemoryManagementFunctions(capabilities ));
}

int main(int argc, char* argv[]) {
    clock_t start = clock(), stop;
    double t = 0.0;
    fmi1_xml_model_description_t* md = fmi1_xml_allocate_model_description( 0 );
    /* Start timer */
    assert(start!=-1);

    if(!md) abort();

	if(argc != 2) {
		printf("Expecting a single parameter (XML file name)\n");
        fmi1_xml_free_model_description(md);
        abort();
	}

    if(fmi1_xml_parse(md, argv[1])) {
        printf("Error parsing XML file %s:%s\n", argv[1], fmi1_xml_get_last_error(md));
        fmi1_xml_free_model_description(md);
        abort();
    }

    /* Stop timer */
    stop = clock();
    t = (double) (stop-start)/CLOCKS_PER_SEC;

    printf("Parsing took %g seconds\n", t);
    printf("Model name: %s\n", fmi1_xml_get_model_name(md));
    printf("Model identifier: %s\n", fmi1_xml_get_model_identifier(md));
    printf("Model GUID: %s\n", fmi1_xml_get_GUID(md));
    printf("FMU kind: %s\n", fmi1_xml_fmu_kind2string(fmi1_xml_get_fmu_kind(md)));
    printf("Description: %s\n", fmi1_xml_get_description(md));
    printf("Author: %s\n", fmi1_xml_get_author(md));
    printf("FMI Version: %s\n", fmi1_xml_get_model_standard_version(md));
    printf("Generation tool: %s\n", fmi1_xml_get_generation_tool(md));
    printf("Generation date and time: %s\n", fmi1_xml_get_generation_date_and_time(md));
    printf("Version: %s\n", fmi1_xml_get_model_version(md));
    printf("Naming : %s\n", fmi1_xml_naming_convention2string(fmi1_xml_get_naming_convention(md)));

    if(fmi1_xml_get_fmu_kind(md) != fmi1_xml_fmu_kind_enu_me)
        printCapabilitiesInfo(fmi1_xml_get_capabilities(md));

    printf("NumberOfContinuousStates = %d\n", fmi1_xml_get_number_of_continuous_states(md));
    printf("NumberOfEventIndicators = %d\n", fmi1_xml_get_number_of_event_indicators(md));

    printf("Default experiment start = %g, end = %g, tolerance = %g\n",
           fmi1_xml_get_default_experiment_start(md),
           fmi1_xml_get_default_experiment_stop(md),
           fmi1_xml_get_default_experiment_tolerance(md));
    {
        fmi1_xml_vendor_list_t* vl = fmi1_xml_get_vendor_list(md);
        size_t i, nv = fmi1_xml_get_number_of_vendors(vl);
        printf("There are %d tool annotation records \n", nv);
        for( i = 0; i < nv; i++) {
            fmi1_xml_vendor_t* vendor = fmi1_xml_get_vendor(vl, i);
            if(!vendor) {
                printf("Error getting vendor for index %d\n", i);
                break;
            }
            printf("Vendor name [%d] %s", i, fmi1_xml_get_vendor_name(vendor));
            {
                size_t j, na = fmi1_xml_get_number_of_vendor_annotations(vendor);

                for(j = 0; j< na; j++) {
                    fmi1_xml_annotation_t* a = fmi1_xml_get_vendor_annotation(vendor, j);
                    if(!a) {
                        printf("Error getting vendor for index %d (%s)\n", j, fmi1_xml_get_last_error(md));
                        break;
                    }

                    printf("Annotation: %s = %s", fmi1_xml_get_annotation_name(a), fmi1_xml_get_annotation_value(a));
                }
            }
        }
    }
    {
        fmi1_xml_unit_definitions_t* ud = fmi1_xml_get_unit_definitions(md);
        if(ud) {
            size_t  i, nu = fmi1_xml_get_unit_definitions_number(ud);
            printf("There are %d different units used \n", nu);

            for(i = 0; i < nu; i++) {
                fmi1_xml_unit_t* u = fmi1_xml_get_unit(ud, i);
                if(!u) {
                    printf("Error getting unit for index %d (%s)\n", i, fmi1_xml_get_last_error(md));
                    break;
                }
                printf("Unit [%d] is %s, it has %d display units\n", i, fmi1_xml_get_unit_name(u), fmi1_xml_get_unit_display_unit_number(u));
            }
        }
        else
            printf("Error getting unit definitions (%s)\n", fmi1_xml_get_last_error(md));
    }
    {
        fmi1_xml_type_definitions_t* td = fmi1_xml_get_type_definitions(md);
        if(td) {
            {
                size_t i, ntd = fmi1_xml_get_type_definition_number(td);
                printf("There are %d defs\n", ntd);
                for(i = 0; i < ntd; i++) {
                    fmi1_xml_variable_typedef_t* vt = fmi1_xml_get_typedef(td, i);
                    if(!vt) {
                        printf("Error getting vartype for index %d (%s)\n", i, fmi1_xml_get_last_error(md));
                        break;
                    }
                    printTypeInfo(vt);
                }
            }
        }
        else
            printf("Error getting type definitions (%s)\n", fmi1_xml_get_last_error(md));
    }
    {
        size_t nv, i;
        fmi1_xml_variable_list_t* vl = fmi1_xml_get_variable_list(md);
        assert(vl);
        nv = fmi1_xml_get_variable_list_size(vl);
        printf("There are %d variables in total \n",nv);
        for(i = 0; i < nv; i++) {
            fmi1_xml_variable_t* var = fmi1_xml_get_variable(vl, i);
            if(!var) printf("Something wrong with variable %d \n",i);
            else
                printVariableInfo(md, var);
        }
        fmi1_xml_free_variable_list(vl);
    }
    fmi1_xml_free_model_description(md);
    return 0;
}
