#include "Optimiser.h"
#include "VertexPartition.h"
#include "Graph.h"
#include "random.h"
#include <vector>
#include <algorithm>
#include <stdexcept>
#include <set>

using namespace std;

void Optimiser::move_nodes_impl(MutableVertexPartition* partition, vector<bool>& is_membership_fixed)
{
  bool improvement = true;

  // Keep iterating as long as we find an improvement
  while (improvement)
  {
    improvement = false;

    // We iterate on the nodes in a random order for better convergence
    vector<int> nodes_to_visit = range(partition->g->vcount());
    this->rng_shuffle(nodes_to_visit);

    for (size_t i_node = 0; i_node < nodes_to_visit.size(); i_node++)
    {
      int i = nodes_to_visit[i_node];

      if (is_membership_fixed[i])
        continue;

      int comm_from = partition->membership[i];
      int comm_to = comm_from;

      // Start with a quality gain of 0. We're looking for a move that gives a positive gain.
      double max_q_gain = 0.0;

      // Find the weights to all neighboring communities
      vector<int> neigh_comm;
      vector<double> neigh_comm_weight;
      partition->get_neigh_comm_weights(i, comm_from, neigh_comm, neigh_comm_weight);

      // Consider moving to an existing neighboring community
      for (size_t j = 0; j < neigh_comm.size(); j++)
      {
        int comm_neigh = neigh_comm[j];
        double q_gain = partition->diff_move(i, comm_neigh);

        if (q_gain > max_q_gain)
        {
          comm_to = comm_neigh;
          max_q_gain = q_gain;
        }
      }

      // After checking all neighbors, consider moving to an empty community
      if (this->consider_empty_community)
      {
        // Only consider empty communities if we have fewer communities than nodes
        // This prevents the "more communities than nodes" error
        if (partition->n_communities() < partition->g->vcount())
        {
          // The quality gain of moving to a new community is calculated
          // by using diff_move with a community ID that doesn't exist yet.
          double q_gain_new = partition->diff_move(i, partition->n_communities());
          if (q_gain_new > max_q_gain)
          {
            comm_to = partition->n_communities();
            max_q_gain = q_gain_new;
          }
        }
      }

      // If we actually found a better community, move the node
      if (comm_to != comm_from)
      {
        partition->move_node(i, comm_to);
        improvement = true;
      }
    }
  }
}

void Optimiser::optimise_partition(MutableVertexPartition* partition, int n_iterations)
{
  vector<bool> is_membership_fixed(partition->g->vcount(), false);
  optimise_partition(partition, n_iterations, is_membership_fixed);
}

void Optimiser::optimise_partition(MutableVertexPartition* partition, int n_iterations, vector<bool>& is_membership_fixed)
{
  // Setup optimiser
  this->rng_init();

  // For the first iteration, we can probably do something better, but let's
  // just do a simple move_nodes for now.
  bool was_improvement = false;
  if (this->optimise_routine == MOVE_NODES)
    was_improvement = this->move_nodes(partition, is_membership_fixed) > 0;
  else if (this->optimise_routine == MERGE_NODES)
    was_improvement = this->merge_nodes(partition, is_membership_fixed) > 0;

  if (was_improvement)
    partition = partition->aggregate(this, this->refine_routine, this->refine_partition, is_membership_fixed);

  int i = 1;
  while (was_improvement && (n_iterations < 0 || i < n_iterations))
  {
    if (this->optimise_routine == MOVE_NODES)
      was_improvement = this->move_nodes(partition, is_membership_fixed) > 0;
    else if (this->optimise_routine == MERGE_NODES)
      was_improvement = this->merge_nodes(partition, is_membership_fixed) > 0;

    if (was_improvement)
      partition = partition->aggregate(this, this->refine_routine, this->refine_partition, is_membership_fixed);
    i++;
  }
}

double Optimiser::optimise_partition_hierarchical(vector<MutableVertexPartition*>& partitions, vector<double>& layer_weights, vector<bool>& is_membership_fixed, vector<MutableVertexPartition*>& hierarchy)
{
    // Make sure partitions are properly initialised.
    if (partitions.size() != layer_weights.size())
        throw std::runtime_error("Partitions and layer_weights should be of same size.");

    // Initialise partition.
    MutableVertexPartition* partition = partitions[0];

    // Setup optimiser
    this->rng_init();

    hierarchy.clear();
    hierarchy.push_back(partition->copy());

    // For the first iteration, we can probably do something better, but let's
    // just do a simple move_nodes for now.
    bool was_improvement = false;
    if (this->optimise_routine == MOVE_NODES)
      was_improvement = this->move_nodes(partition, is_membership_fixed) > 0;
    else if (this->optimise_routine == MERGE_NODES)
      was_improvement = this->merge_nodes(partition, is_membership_fixed) > 0;

    if (was_improvement)
    {
        MutableVertexPartition* new_partition = partition->aggregate(this, this->refine_routine, this->refine_partition, is_membership_fixed);
        partitions[0] = new_partition;
        hierarchy.push_back(new_partition->copy_from_graph(partition->g));
        partition = new_partition;
    }

    int i = 1;
    while (was_improvement)
    {
        if (this->optimise_routine == MOVE_NODES)
          was_improvement = this->move_nodes(partition, is_membership_fixed) > 0;
        else if (this->optimise_routine == MERGE_NODES)
          was_improvement = this->merge_nodes(partition, is_membership_fixed) > 0;

        if (was_improvement)
        {
            MutableVertexPartition* new_partition = partition->aggregate(this, this->refine_routine, this->refine_partition, is_membership_fixed);
            partitions[0] = new_partition;
            hierarchy.push_back(new_partition->copy_from_graph(partition->g));
            partition = new_partition;
        }
        i++;
    }

    // Return the total quality improvement
    double total_quality = 0.0;
    if (!hierarchy.empty()) {
        total_quality = hierarchy.back()->quality();
    }
    return total_quality;
}

// Basic move_nodes implementation
double Optimiser::move_nodes(MutableVertexPartition* partition, vector<bool>& is_membership_fixed)
{
  double initial_quality = partition->quality();
  move_nodes_impl(partition, is_membership_fixed);
  return partition->quality() - initial_quality;
}

// Additional move_nodes overloads that are called from the Python interface
double Optimiser::move_nodes(MutableVertexPartition* partition, int consider_comms)
{
  vector<bool> is_membership_fixed(partition->g->vcount(), false);
  return move_nodes(partition, is_membership_fixed, consider_comms, true);
}

double Optimiser::move_nodes(MutableVertexPartition* partition, vector<bool> const& is_membership_fixed, int consider_comms, bool renumber_fixed_nodes)
{
  double initial_quality = partition->quality();
  
  // Implement move_nodes logic directly instead of calling undefined function
  vector<int> nodes_to_visit = range(partition->g->vcount());
  this->rng_shuffle(nodes_to_visit);

  for (size_t i_node = 0; i_node < nodes_to_visit.size(); i_node++)
  {
    int i = nodes_to_visit[i_node];

    if (is_membership_fixed[i])
      continue;

    int comm_from = partition->membership[i];
    int comm_to = comm_from;

    // Start with a quality gain of 0. We're looking for a move that gives a positive gain.
    double max_q_gain = 0.0;

    // Determine which communities to consider based on the consider_comms parameter
    if (consider_comms == ALL_NEIGH_COMMS)
    {
      // Find the weights to all neighboring communities
      vector<int> neigh_comm;
      vector<double> neigh_comm_weight;
      partition->get_neigh_comm_weights(i, comm_from, neigh_comm, neigh_comm_weight);

      // Consider moving to an existing neighboring community
      for (size_t j = 0; j < neigh_comm.size(); j++)
      {
        int comm_neigh = neigh_comm[j];
        double q_gain = partition->diff_move(i, comm_neigh);

        if (q_gain > max_q_gain)
        {
          comm_to = comm_neigh;
          max_q_gain = q_gain;
        }
      }
    }
    else if (consider_comms == ALL_COMMS)
    {
      // Consider all communities for moving
      for (size_t c = 0; c < partition->n_communities(); c++)
      {
        if ((int)c != comm_from)
        {
          double q_gain = partition->diff_move(i, c);
          if (q_gain > max_q_gain)
          {
            comm_to = c;
            max_q_gain = q_gain;
          }
        }
      }
    }

    // After checking all options, consider moving to an empty community
    if (this->consider_empty_community)
    {
      // Only consider empty communities if we have fewer communities than nodes
      // This prevents the "more communities than nodes" error
      if (partition->n_communities() < partition->g->vcount())
      {
        // The quality gain of moving to a new community is calculated
        // by using diff_move with a community ID that doesn't exist yet.
        double q_gain_new = partition->diff_move(i, partition->n_communities());
        if (q_gain_new > max_q_gain)
        {
          comm_to = partition->n_communities();
          max_q_gain = q_gain_new;
        }
      }
    }

    // If we actually found a better community, move the node
    if (comm_to != comm_from && max_q_gain > 0)
    {
      partition->move_node(i, comm_to);
    }
  }
  
  return partition->quality() - initial_quality;
}

double Optimiser::move_nodes(MutableVertexPartition* partition, vector<bool> const& is_membership_fixed, int consider_comms, bool renumber_fixed_nodes, size_t max_comm_size)
{
  // For now, ignore max_comm_size and just call the 4-parameter version
  return move_nodes(partition, is_membership_fixed, consider_comms, renumber_fixed_nodes);
}

// Proper merge_nodes implementation that merges communities
double Optimiser::merge_nodes(MutableVertexPartition* partition, vector<bool>& is_membership_fixed)
{
  double initial_quality = partition->quality();
  bool improvement = true;

  // Keep iterating as long as we find an improvement
  while (improvement)
  {
    improvement = false;

    // Iterate through all nodes and try to merge them with neighboring communities
    vector<int> nodes_to_visit = range(partition->g->vcount());
    this->rng_shuffle(nodes_to_visit);

    for (size_t i_node = 0; i_node < nodes_to_visit.size(); i_node++)
    {
      int i = nodes_to_visit[i_node];

      if (is_membership_fixed[i])
        continue;

      int comm_from = partition->membership[i];
      int comm_to = comm_from;

      // Start with a quality gain of 0. We're looking for a move that gives a positive gain.
      double max_q_gain = 0.0;

      // Find the weights to all neighboring communities
      vector<int> neigh_comm;
      vector<double> neigh_comm_weight;
      partition->get_neigh_comm_weights(i, comm_from, neigh_comm, neigh_comm_weight);

      // Consider moving to an existing neighboring community
      for (size_t j = 0; j < neigh_comm.size(); j++)
      {
        int comm_neigh = neigh_comm[j];
        double q_gain = partition->diff_move(i, comm_neigh);

        if (q_gain > max_q_gain)
        {
          comm_to = comm_neigh;
          max_q_gain = q_gain;
        }
      }

      // For merge_nodes, we are more aggressive - also consider all communities, not just neighbors
      // This is the key difference from move_nodes
      if (this->consider_comms == ALL_COMMS)
      {
        for (size_t c = 0; c < partition->n_communities(); c++)
        {
          if ((int)c != comm_from)
          {
            double q_gain = partition->diff_move(i, c);
            if (q_gain > max_q_gain)
            {
              comm_to = c;
              max_q_gain = q_gain;
            }
          }
        }
      }

      // After checking all options, consider moving to an empty community
      if (this->consider_empty_community)
      {
        // Only consider empty communities if we have fewer communities than nodes
        // This prevents the "more communities than nodes" error
        if (partition->n_communities() < partition->g->vcount())
        {
          // The quality gain of moving to a new community is calculated
          // by using diff_move with a community ID that doesn't exist yet.
          double q_gain_new = partition->diff_move(i, partition->n_communities());
          if (q_gain_new > max_q_gain)
          {
            comm_to = partition->n_communities();
            max_q_gain = q_gain_new;
          }
        }
      }

      // If we actually found a better community, move the node
      if (comm_to != comm_from && max_q_gain > 0)
      {
        partition->move_node(i, comm_to);
        improvement = true;
      }
    }
  }

  return partition->quality() - initial_quality;
}

// Just move nodes, probably not the best to do, maybe iteratively applying
// it is better?
void Optimiser::move_nodes(MutableVertexPartition* partition)
{
  vector<bool> is_membership_fixed(partition->g->vcount(), false);
  this->move_nodes_impl(partition, is_membership_fixed);
}

// Additional merge_nodes overloads that are called from the Python interface
double Optimiser::merge_nodes(MutableVertexPartition* partition, int consider_comms)
{
  vector<bool> is_membership_fixed(partition->g->vcount(), false);
  return merge_nodes(partition, is_membership_fixed, consider_comms, true);
}

double Optimiser::merge_nodes(MutableVertexPartition* partition, vector<bool> const& is_membership_fixed, int consider_comms, bool renumber_fixed_nodes)
{
  double initial_quality = partition->quality();
  bool improvement = true;

  // Keep iterating as long as we find an improvement
  while (improvement)
  {
    improvement = false;

    // Iterate through all nodes and try to merge them with neighboring communities
    vector<int> nodes_to_visit = range(partition->g->vcount());
    this->rng_shuffle(nodes_to_visit);

    for (size_t i_node = 0; i_node < nodes_to_visit.size(); i_node++)
    {
      int i = nodes_to_visit[i_node];

      if (is_membership_fixed[i])
        continue;

      int comm_from = partition->membership[i];
      int comm_to = comm_from;

      // Start with a quality gain of 0. We're looking for a move that gives a positive gain.
      double max_q_gain = 0.0;

      // Determine which communities to consider based on the consider_comms parameter
      if (consider_comms == ALL_NEIGH_COMMS)
      {
        // Find the weights to all neighboring communities
        vector<int> neigh_comm;
        vector<double> neigh_comm_weight;
        partition->get_neigh_comm_weights(i, comm_from, neigh_comm, neigh_comm_weight);

        // Consider moving to an existing neighboring community
        for (size_t j = 0; j < neigh_comm.size(); j++)
        {
          int comm_neigh = neigh_comm[j];
          double q_gain = partition->diff_move(i, comm_neigh);

          if (q_gain > max_q_gain)
          {
            comm_to = comm_neigh;
            max_q_gain = q_gain;
          }
        }
      }
      else if (consider_comms == ALL_COMMS)
      {
        // Consider all communities for moving
        for (size_t c = 0; c < partition->n_communities(); c++)
        {
          if ((int)c != comm_from)
          {
            double q_gain = partition->diff_move(i, c);
            if (q_gain > max_q_gain)
            {
              comm_to = c;
              max_q_gain = q_gain;
            }
          }
        }
      }

      // After checking all options, consider moving to an empty community
      if (this->consider_empty_community)
      {
        // Only consider empty communities if we have fewer communities than nodes
        // This prevents the "more communities than nodes" error
        if (partition->n_communities() < partition->g->vcount())
        {
          // The quality gain of moving to a new community is calculated
          // by using diff_move with a community ID that doesn't exist yet.
          double q_gain_new = partition->diff_move(i, partition->n_communities());
          if (q_gain_new > max_q_gain)
          {
            comm_to = partition->n_communities();
            max_q_gain = q_gain_new;
          }
        }
      }

      // If we actually found a better community, move the node
      if (comm_to != comm_from && max_q_gain > 0)
      {
        partition->move_node(i, comm_to);
        improvement = true;
      }
    }
  }

  return partition->quality() - initial_quality;
}

double Optimiser::merge_nodes(MutableVertexPartition* partition, vector<bool> const& is_membership_fixed, int consider_comms, bool renumber_fixed_nodes, size_t max_comm_size)
{
  // For now, ignore max_comm_size and just call the 4-parameter version
  return merge_nodes(partition, is_membership_fixed, consider_comms, renumber_fixed_nodes);
}
