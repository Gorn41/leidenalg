#ifndef MODULARITYVERTEXPARTITION_H
#define MODULARITYVERTEXPARTITION_H

#include "MutableVertexPartition.h"

class LIBLEIDENALG_EXPORT ModularityVertexPartition : public MutableVertexPartition
{
  public:
    ModularityVertexPartition(Graph* graph,
        vector<size_t> const& membership);
    ModularityVertexPartition(Graph* graph);
    virtual ~ModularityVertexPartition();
    virtual ModularityVertexPartition* create(Graph* graph);
    virtual ModularityVertexPartition* create(Graph* graph, vector<size_t> const& membership);

    virtual double diff_move(size_t v, size_t new_comm);
    virtual double quality();
    virtual ModularityVertexPartition* clone();

  protected:
  private:
};

#endif // MODULARITYVERTEXPARTITION_H
