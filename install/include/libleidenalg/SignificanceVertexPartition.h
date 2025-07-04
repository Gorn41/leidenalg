#ifndef SIGNIFICANCEVERTEXPARTITION_H
#define SIGNIFICANCEVERTEXPARTITION_H

#include "MutableVertexPartition.h"


class LIBLEIDENALG_EXPORT SignificanceVertexPartition : public MutableVertexPartition
{
  public:
    SignificanceVertexPartition(Graph* graph, vector<size_t> const& membership);
    SignificanceVertexPartition(Graph* graph);
    virtual ~SignificanceVertexPartition();
    virtual SignificanceVertexPartition* create(Graph* graph);
    virtual SignificanceVertexPartition* create(Graph* graph, vector<size_t> const& membership);

    virtual SignificanceVertexPartition* clone();

    virtual double diff_move(size_t v, size_t new_comm);
    virtual double quality();
  protected:
  private:
};

#endif // SIGNIFICANCEVERTEXPARTITION_H
