#ifndef PYNTERFACE_OPTIMISER_H_INCLUDED
#define PYNTERFACE_OPTIMISER_H_INCLUDED

#include <Python.h>
#include <igraph/igraph.h>
#include <libleidenalg/GraphHelper.h>
#include <libleidenalg/ModularityVertexPartition.h>
#include <libleidenalg/SignificanceVertexPartition.h>
#include <libleidenalg/SurpriseVertexPartition.h>
#include <libleidenalg/RBConfigurationVertexPartition.h>
#include <libleidenalg/RBERVertexPartition.h>
#include <libleidenalg/CPMVertexPartition.h>
#include <libleidenalg/Optimiser.h>

#include "python_partition_interface.h"

#ifdef DEBUG
#include <iostream>
  using std::cerr;
  using std::endl;
#endif

PyObject* capsule_Optimiser(Optimiser* optimiser);
Optimiser* decapsule_Optimiser(PyObject* py_optimiser);
void del_Optimiser(PyObject* py_optimiser);

#ifdef __cplusplus
extern "C"
{
#endif
  PyObject* _new_Optimiser(PyObject *self, PyObject *args);
  PyObject* _Optimiser_optimise_partition(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_optimise_partition_multiplex(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_optimise_partition_hierarchical(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_move_nodes(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_move_nodes_constrained(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_merge_nodes(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_merge_nodes_constrained(PyObject *self, PyObject *args, PyObject *keywds);

  PyObject* _Optimiser_set_consider_comms(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_set_refine_consider_comms(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_set_optimise_routine(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_set_refine_routine(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_set_consider_empty_community(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_set_refine_partition(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_set_max_comm_size(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_set_rng_seed(PyObject *self, PyObject *args, PyObject *keywds);

  PyObject* _Optimiser_get_consider_comms(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_get_refine_consider_comms(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_get_optimise_routine(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_get_refine_routine(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_get_consider_empty_community(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_get_refine_partition(PyObject *self, PyObject *args, PyObject *keywds);
  PyObject* _Optimiser_get_max_comm_size(PyObject *self, PyObject *args, PyObject *keywds);

#ifdef __cplusplus
}
#endif
#endif // PYNTERFACE_OPTIMISER_H_INCLUDED
