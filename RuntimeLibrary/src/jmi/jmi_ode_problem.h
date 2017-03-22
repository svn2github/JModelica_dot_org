 /*
    Copyright (C) 2009 Modelon AB

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License version 3 as published
    by the Free Software Foundation, or optionally, under the terms of the
    Common Public License version 1.0 as published by IBM.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License, or the Common Public License, for more details.

    You should have received copies of the GNU General Public License
    and the Common Public License along with this program.  If not,
    see <http://www.gnu.org/licenses/> or
    <http://www.ibm.com/developerworks/library/os-cpl.html/> respectively.
*/


/** \file jmi_ode_problem.h
 *  \brief Structures and functions for handling an ODE problem.
 */

#ifndef _JMI_ODE_PROBLEM_H
#define _JMI_ODE_PROBLEM_H

#include "jmi_log.h"
#include "jmi_ode_solver.h"


/**
 * \brief An ode right-hand-side signature.
 *
 * @param ode_problem A jmi_ode_problem_t struct.
 * @param t The ODE time.
 * @param y A pointer to the states of the ODE.
 * @param rhs A pointer to the state derivatives of the ODE.
 * @return Error code.
  */
typedef int (*rhs_func_t)(jmi_ode_problem_t* ode_problem, jmi_real_t t, jmi_real_t* y, jmi_real_t* rhs);

/**
 * \brief An ode root-function signature.
 *
 * @param ode_problem A jmi_ode_problem_t struct.
 * @param t The ODE time.
 * @param y A pointer to the states of the ODE.
 * @param root A pointer to an evaluation of the event indicator of the ODE.
 * @return Error code.
  */
typedef int (*root_func_t)(jmi_ode_problem_t* ode_problem, jmi_real_t t, jmi_real_t *y, jmi_real_t *root);

/**
 * \brief An ode complete-step-function signature.
 *
 * @param ode_problem A jmi_ode_problem_t struct.
 * @param step_event An indicator of whether a step event has occured or not.
 * @return Error code.
  */
typedef int (*complete_step_func_t)(jmi_ode_problem_t* ode_problem, char* step_event);

typedef struct {
    rhs_func_t            rhs_func;             /**< \brief A callback function for the rhs of the ODE problem. */
    root_func_t           root_func;            /**< \brief A callback function for the root of the ODE problem. */
    complete_step_func_t  complete_step_func;   /**< \brief A callback function for completing the step. */
} jmi_ode_callbacks_t;

typedef struct {
    size_t states;
    size_t root_fnc;
} jmi_ode_sizes_t;

struct jmi_ode_problem_t {
    jmi_callbacks_t*      jmi_callbacks;        /**< \brief A pointer to the jmi_callbacks_t struct */
    void*                 problem_data;         /**< \brief Reference to opaque callback data. */
    jmi_ode_solver_t*     ode_solver;           /**< \brief Struct containing the ODE solver. */
    jmi_log_t*            log;                  /**< \brief A pointer to the jmi_log_t struct */
    
    jmi_ode_callbacks_t   ode_callbacks;        /**< \brief Struct with all ODE callback functions. */
    
    jmi_ode_sizes_t       sizes;                /**< \brief The dimensions of the ODE problem. */
    jmi_real_t            time;                 /**< \brief The time, independent variable of the ODE. */
    jmi_real_t*           states;               /**< \brief The states of the ODE. */
    jmi_real_t*           nominals;             /**< \brief The nominals for the states. */
};

/**
 * \brief Creates a ode_callback_funcs_t struct with default values.
 *
 * @return A ode_callback_funcs_t struct with default callbacks.
  */
jmi_ode_callbacks_t jmi_ode_problem_default_callbacks();

/**
 * \brief Creates a new jmi_ode_problem_t instance.
 *
 * @param cb A jmi_callbacks_t pointer.
 * @param problem_data An opace pointer for the problem definition. 
 * @param ode_callbacks A ode_callback_funcs_t struct with all callbacks for the ODE problem.
 * @param dims A ode_dims_t struct with the sizes of the ODE problem.
 * @param log A pointer to a jmi_log_t struct.
 * @return A pointer to a jmi_ode_problem_t struct, NULL on failure.
  */
jmi_ode_problem_t* jmi_new_ode_problem(jmi_callbacks_t*     cb,
                                       void*                problem_data,
                                       jmi_ode_callbacks_t  ode_callbacks,
                                       jmi_ode_sizes_t      dims,
                                       jmi_log_t*           log);

/**
 * \brief Deletes the jmi_ode_problem_t instance.
 *
 * @param ode_problem A jmi_ode_problem_t struct.
  */
void jmi_free_ode_problem(jmi_ode_problem_t* problem);

/**
 * \brief Resets the jmi_ode_problem_t instance. The struct will be in the state
 * it was after jmi_new_ode_problem. NOTE that this does not mean that the
 * structs jmi_callbacks_t and jmi_log_t are reset. So jmi_ode_problem_t don't
 * own them but only holds a reference to and use them.
 *
 * @param ode_problem A jmi_ode_problem_t struct.
  */
void jmi_reset_ode_problem(jmi_ode_problem_t* problem);

#endif
