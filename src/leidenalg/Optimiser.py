from . import _c_leiden
from .VertexPartition import LinearResolutionParameterVertexPartition
from collections import namedtuple
from math import log, sqrt

class Optimiser(object):
  r""" Class for doing community detection using the Leiden algorithm.
  The Leiden algorithm [1] derives from the Louvain algorithm [2]. The Louvain
  algorithm has an elegant formulation. It consists of two phases: (1) move
  nodes between communities; (2) aggregate the graph. It then repeats these
  phases on the aggregate graph. The Leiden algorithm consists of three phases:
  (1) move nodes; (2) refine communities; (3) aggregate the graph based on the
  refinement. The Louvain algorithm can lead to arbitrarily badly connected
  communities, whereas the Leiden algorithm guarantees communities are
  well-connected. In fact, it converges towards a partition in which all
  subsets of all communities are locally optimally assigned. Finally, the
  Leiden algorithm is also much faster, because it relies on a fast local move
  routine.
  There is one, rather technical, difference with the original Leiden
  algorithm. This implementation provides a general optimisation
  routine for any quality function. There is one aspect of the original Leiden
  algorithm that cannot be translated well in this framework: when merging
  subcommunities in the refinement procedure, it does not consider whether they
  are sufficiently well connected to the rest of the community. This
  implementation therefore does not guarantee subpartition :math:`\gamma`-density.
  However, all other guarantees still hold:
  After each iteration
    1. :math:`\gamma`-separation
    2. :math:`\gamma`-connectivity
  After a stable iteration
    3. Node optimality
    4. Some subsets are locally optimally assigned
  Asymptotically
    5. Uniform :math:`\gamma`-density
    6. Subset optimality
  The optimiser class provides a number of different methods for optimising a
  given partition. The overall optimisation procedure
  :func:`optimise_partition` calls either :func:`move_nodes` or
  :func:`merge_nodes` (which is controlled by :attr:`optimise_routine`) then
  aggregates the graph and repeats the same procedure. Possible, indicated by
  :attr:`refine_partition`, the partition is refined before aggregating, meaning
  that subsets of communities are considered for moving around. Which routine
  is used for the refinement is indicated by :attr:`refine_routine`. For
  calculating the actual improvement of moving a node (corresponding a subset
  of nodes in the aggregate graph), the code relies on
  :func:`~VertexPartition.MutableVertexPartition.diff_move` which provides
  different values for different methods (e.g. modularity or CPM). The default
  settings are consistent with the Leiden algorithm. By not doing the
  refinement, you essentially get the Louvain algorithm with a fast local move.
  Finally, the Optimiser class provides a routine to construct a
  :func:`resolution_profile` on a resolution parameter.
  References
  ----------
  .. [1] Traag, V.A., Waltman. L., Van Eck, N.-J. (2018). From Louvain to
         Leiden: guaranteeing well-connected communities.
         `arXiv:1810.08473 <https://arxiv.org/abs/1810.08473>`_
  .. [2] Blondel, V. D., Guillaume, J.-L., Lambiotte, R., & Lefebvre, E.
         (2008). Fast unfolding of communities in large networks. Journal of
         Statistical Mechanics: Theory and Experiment, 10008(10), 6.
         `10.1088/1742-5468/2008/10/P10008 <https://doi.org/10.1088/1742-5468/2008/10/P10008>`_
  """
  def __init__(self):
    """ Create a new Optimiser object """
    self._optimiser = _c_leiden._new_Optimiser()
  #########################################################3
  # consider_comms
  @property
  def consider_comms(self):
    """ Determine how alternative communities are considered for moving
    a node for *optimising* a partition.
    Nodes will only move to alternative communities that improve the given
    quality function.
    The default is :attr:`leidenalg.ALL_NEIGH_COMMS`.
    Notes
    -------
    This attribute should be set to one of the following values
    * :attr:`leidenalg.ALL_NEIGH_COMMS`
      Consider all neighbouring communities for moving.
    * :attr:`leidenalg.ALL_COMMS`
      Consider all communities for moving. This is especially useful in the
      case of negative links, in which case it may be better to move a node to
      a non-neighbouring community.
    * :attr:`leidenalg.RAND_NEIGH_COMM`
      Consider a random neighbour community for moving. The probability to
      choose a community is proportional to the number of neighbours a node has
      in that community.
    * :attr:`leidenalg.RAND_COMM`
      Consider a random community for moving. The probability to choose a
      community is proportional to the number of nodes in that community.
    """
    return _c_leiden._Optimiser_get_consider_comms(self._optimiser)
  @consider_comms.setter
  def consider_comms(self, value):
    _c_leiden._Optimiser_set_consider_comms(self._optimiser, value)
  #########################################################3
  # refine consider_comms
  @property
  def refine_consider_comms(self):
    """ Determine how alternative communities are considered for moving
    a node when *refining* a partition.
    Nodes will only move to alternative communities that improve the given
    quality function.
    The default is :attr:`leidenalg.ALL_NEIGH_COMMS`.
    Notes
    -------
    This attribute should be set to one of the following values
    * :attr:`leidenalg.ALL_NEIGH_COMMS`
      Consider all neighbouring communities for moving.
    * :attr:`leidenalg.ALL_COMMS`
      Consider all communities for moving. This is especially useful in the
      case of negative links, in which case it may be better to move a node to
      a non-neighbouring community.
    * :attr:`leidenalg.RAND_NEIGH_COMM`
      Consider a random neighbour community for moving. The probability to
      choose a community is proportional to the number of neighbours a node has
      in that community.
    * :attr:`leidenalg.RAND_COMM`
      Consider a random community for moving. The probability to choose a
      community is proportional to the number of nodes in that community.
    """
    return _c_leiden._Optimiser_get_refine_consider_comms(self._optimiser)
  @refine_consider_comms.setter
  def refine_consider_comms(self, value):
    _c_leiden._Optimiser_set_refine_consider_comms(self._optimiser, value)
  #########################################################3
  # optimise routine
  @property
  def optimise_routine(self):
    """ Determine the routine to use for *optimising* a partition.
    The default is :attr:`leidenalg.MOVE_NODES`.
    Notes
    -------
    This attribute should be set to one of the following values
    * :attr:`leidenalg.MOVE_NODES`
      Use :func:`move_nodes`.
    * :attr:`leidenalg.MERGE_NODES`
      Use :func:`merge_nodes`.
    """
    return _c_leiden._Optimiser_get_optimise_routine(self._optimiser)
  @optimise_routine.setter
  def optimise_routine(self, value):
    _c_leiden._Optimiser_set_optimise_routine(self._optimiser, value)
  #########################################################3
  # optimise routine
  @property
  def refine_routine(self):
    """ Determine the routine to use for *refining* a partition.
    The default is :attr:`leidenalg.MERGE_NODES`.
    Notes
    -------
    This attribute should be set to one of the following values
    * :attr:`leidenalg.MOVE_NODES`
      Use :func:`move_nodes_constrained`.
    * :attr:`leidenalg.MERGE_NODES`
      Use :func:`merge_nodes_constrained`.
    """
    return _c_leiden._Optimiser_get_refine_routine(self._optimiser)
  @refine_routine.setter
  def refine_routine(self, value):
    _c_leiden._Optimiser_set_refine_routine(self._optimiser, value)
  #########################################################3
  # refine_partition
  @property
  def refine_partition(self):
    """ boolean: if ``True`` refine partition before aggregation. """
    return _c_leiden._Optimiser_get_refine_partition(self._optimiser)
  @refine_partition.setter
  def refine_partition(self, value):
    _c_leiden._Optimiser_set_refine_partition(self._optimiser, value)
  #########################################################3
  # consider_empty_community
  @property
  def consider_empty_community(self):
    """ boolean: if ``True`` consider also moving nodes to an empty community
    (default). """
    return _c_leiden._Optimiser_get_consider_empty_community(self._optimiser)
  @consider_empty_community.setter
  def consider_empty_community(self, value):
    _c_leiden._Optimiser_set_consider_empty_community(self._optimiser, value)
  #########################################################3
  # max_comm_size
  @property
  def max_comm_size(self):
    """ Constrain the maximal community size.
    By default (zero), communities can be of any size. If this is set to a
    positive integer value, then communities will be constrained to be at most
    this total size.
    """
    return _c_leiden._Optimiser_get_max_comm_size(self._optimiser)
  @max_comm_size.setter
  def max_comm_size(self, value):
    if value < 0:
        raise ValueError("negative max_comm_size: %s" % value)
    _c_leiden._Optimiser_set_max_comm_size(self._optimiser, value)
  ##########################################################
  # Set rng seed
  def set_rng_seed(self, value):
    """ Set the random seed for the random number generator.
    Parameters
    ----------
    value
      The integer seed used in the random number generator
    """
    _c_leiden._Optimiser_set_rng_seed(self._optimiser, value)

  def optimise_partition_hierarchical(self, partition, n_iterations=-1):
    """
    Optimise partition and return all intermediate partitions.
    This function is similar to :func:`optimise_partition` but returns all
    intermediate partitions. The optimisation proceeds in an iterative manner,
    in which we first move nodes, and then aggregate the partition. Each of
    these aggregated partitions is returned in a list. The last partition is
    the same as the one that would be returned by :func:`optimise_partition`.
    Parameters
    ----------
    partition : :class:`VertexPartition`
      The partition to optimise.
    n_iterations : int
      Number of iterations to run the Leiden algorithm. By default, -1 iterations
      are run, which means the Leiden algorithm is run until an iteration in
      which there was no improvement.
    Returns
    -------
    list of :class:`VertexPartition`
      A list of all intermediate partitions, where the last one is the final
      optimised partition.
    """
    # For now, n_iterations is handled entirely by the C++ implementation,
    # which runs until no further improvement is possible.
    # The argument is kept for API consistency.
    partitions = [partition]
    layer_weights = [1.0]
    is_membership_fixed = [False] * partition.graph.vcount()

    _, hierarchy = _c_leiden._Optimiser_optimise_partition_hierarchical(
        self._optimiser,
        [p._partition for p in partitions],
        layer_weights,
        is_membership_fixed
    )
    
    # The returned hierarchy is a list of C++ partition objects.
    # We need to convert them back to Python objects.
    from .VertexPartition import MutableVertexPartition
    py_hierarchy = [MutableVertexPartition._FromCPartition(p) for p in hierarchy]

    return py_hierarchy

  def optimise_partition(self, partition, n_iterations=2, is_membership_fixed=None):
    """ Optimise the given partition.
    This function optimises the partition using the Leiden algorithm. It is the
    main function that repeatedly calls the subroutines for moving nodes and
    aggregating the graph.
    Parameters
    ----------
    partition : :class:`VertexPartition`
      The partition to optimise.
    n_iterations : int
      Number of iterations to run the Leiden algorithm. By default, 2 iterations
      are run. If the number of iterations is negative, the Leiden algorithm is
      run until an iteration in which there was no improvement.
    is_membership_fixed: list of boolean
      For each node a boolean indicating if its membership is fixed. If it is
      fixed, it can no longer be changed.
    Returns
    -------
    double
      The difference in quality function.
    """
    itr = 0
    diff = 0
    continue_iteration = itr < n_iterations or n_iterations < 0
    while continue_iteration:
      diff_inc = _c_leiden._Optimiser_optimise_partition(
              self._optimiser,
              partition._partition,
              is_membership_fixed=is_membership_fixed,
              )
      diff += diff_inc
      itr += 1
      if n_iterations < 0:
        continue_iteration = (diff_inc > 0)
      else:
        continue_iteration = itr < n_iterations

    partition._update_internal_membership()
    return diff

  def optimise_partition_multiplex(self, partitions, layer_weights=None, n_iterations=2, is_membership_fixed=None):
    """ Optimise a multiplex partition.
    This function optimises the multiplex partition using the Leiden algorithm. It
    is the main function that repeatedly calls the subroutines for moving nodes
    and aggregating the graph. This function is for multiplex graphs, where
    each layer is defined on the same set of nodes.
    Parameters
    ----------
    partitions : list of :class:`VertexPartition`
      The partitions to optimise, one for each layer.
    layer_weights : list of double
      The weight of each layer.
    n_iterations : int
      Number of iterations to run the Leiden algorithm. By default, 2 iterations
      are run. If the number of iterations is negative, the Leiden algorithm is
      run until an iteration in which there was no improvement.
    is_membership_fixed: list of boolean
      For each node a boolean indicating if its membership is fixed. If it is
      fixed, it can no longer be changed.
    Returns
    -------
    double
      The difference in quality function.
    """
    if layer_weights is None:
      n_layers = len(partitions)
      layer_weights = [1]*n_layers

    itr = 0
    diff = 0
    continue_iteration = itr < n_iterations or n_iterations < 0
    while continue_iteration:
      diff_inc = _c_leiden._Optimiser_optimise_partition_multiplex(
        self._optimiser,
        [p._partition for p in partitions],
        layer_weights,
        is_membership_fixed)
      diff += diff_inc
      itr += 1
      if n_iterations < 0:
        continue_iteration = (diff_inc > 0)
      else:
        continue_iteration = itr < n_iterations

    for partition in partitions:
      partition._update_internal_membership()
    return diff

  def move_nodes(self, partition, is_membership_fixed=None, consider_comms=None):
    """ Greedily move nodes to other communities to improve the partition.
    This function moves nodes to the community that gives the highest
    improvement in the quality function. It will only move a node if the
    quality function improves. The order of the nodes is randomised.
    Parameters
    ----------
    partition : :class:`VertexPartition`
      The partition to optimise.
    is_membership_fixed: list of boolean
      For each node a boolean indicating if its membership is fixed. If it is
      fixed, it can no longer be changed.
    consider_comms: int
      How to consider communities, see :attr:`consider_comms`. If None,
      it will use the setting of the optimiser.
    Returns
    -------
    double
      The difference in quality function.
    """
    if consider_comms is None:
      return _c_leiden._Optimiser_move_nodes(self._optimiser, partition._partition, is_membership_fixed)
    else:
      return _c_leiden._Optimiser_move_nodes(self._optimiser, partition._partition, is_membership_fixed, consider_comms)
  def move_nodes_constrained(self, partition, constrained_partition, consider_comms=None):
    """ Greedily move nodes to other communities to improve the partition within constraints.
    This function moves nodes to the community that gives the highest
    improvement in the quality function. It will only move a node if the
    quality function improves. The order of the nodes is randomised. In contrast
    to :func:`move_nodes`, this function moves nodes only within the communities
    as specified in `constrained_partition`.
    Parameters
    ----------
    partition : :class:`VertexPartition`
      The partition to optimise.
    constrained_partition : :class:`VertexPartition`
      The partition that constrains the moves.
    consider_comms: int
      How to consider communities, see :attr:`consider_comms`. If None,
      it will use the setting of the optimiser.
    Returns
    -------
    double
      The difference in quality function.
    """
    if consider_comms is None:
      return _c_leiden._Optimiser_move_nodes_constrained(self._optimiser, partition._partition, constrained_partition._partition)
    else:
      return _c_leiden._Optimiser_move__nodes_constrained(self._optimiser, partition._partition, constrained_partition._partition, consider_comms)
  def merge_nodes(self, partition, is_membership_fixed=None, consider_comms=None):
    """ Greedily merge nodes to other communities to improve the partition.
    This function moves nodes to the community that gives the highest
    improvement in the quality function. It will only move a node if the
    quality function improves. The order of the nodes is randomised. This
    function in contrast to :func:`move_nodes` merges nodes together in
    communities, which is much faster.
    Parameters
    ----------
    partition : :class:`VertexPartition`
      The partition to optimise.
    is_membership_fixed: list of boolean
      For each node a boolean indicating if its membership is fixed. If it is
      fixed, it can no longer be changed.
    consider_comms: int
      How to consider communities, see :attr:`consider_comms`. If None,
      it will use the setting of the optimiser.
    Returns
    -------
    double
      The difference in quality function.
    """
    if consider_comms is None:
      return _c_leiden._Optimiser_merge_nodes(self._optimiser, partition._partition, is_membership_fixed)
    else:
      return _c_leiden._Optimiser_merge_nodes(self._optimiser, partition._partition, is_membership_fixed, consider_comms)
  def merge_nodes_constrained(self, partition, constrained_partition, consider_comms=None):
    """ Greedily merge nodes to other communities to improve the partition within constraints.
    This function moves nodes to the community that gives the highest
    improvement in the quality function. It will only move a node if the
    quality function improves. The order of the nodes is randomised. In contrast
    to :func:`merge_nodes`, this function moves nodes only within the communities
    as specified in `constrained_partition`. This function in contrast to
    :func:`move_nodes_constrained` merges nodes together in communities, which is
    much faster.
    Parameters
    ----------
    partition : :class:`VertexPartition`
      The partition to optimise.
    constrained_partition : :class:`VertexPartition`
      The partition that constrains the moves.
    consider_comms: int
      How to consider communities, see :attr:`consider_comms`. If None,
      it will use the setting of the optimiser.
    Returns
    -------
    double
      The difference in quality function.
    """
    if consider_comms is None:
      return _c_leiden._Optimiser_merge_nodes_constrained(self._optimiser, partition._partition, constrained_partition._partition)
    else:
      return _c_leiden._Optimiser_merge_nodes_constrained(self._optimiser, partition._partition, constrained_partition._partition, consider_comms)
  def resolution_profile(self,
        graph,
        partition_type,
        resolution_range,
        weights=None,
        bisect_func=lambda p: p.bisect_value(),
        min_diff_bisect_value=1,
        min_diff_resolution=1e-3,
        linear_bisection=False,
        number_iterations=1,
        **kwargs
        ):
    if not issubclass(partition_type, LinearResolutionParameterVertexPartition):
      raise TypeError("Partition type should be a resolution parameter partition.")
    if not (isinstance(resolution_range, tuple) and len(resolution_range) == 2):
      raise TypeError("Resolution range should be a tuple of length 2.")
    Bisect = namedtuple('Bisect', ['partition', 'is_stable'])
    bisect_values = {}
    def expand_profile(resolution, min_res_diff=1e-3):
      if resolution not in bisect_values:
        kwargs_res = kwargs.copy()
        kwargs_res['resolution_parameter'] = resolution
        partition = partition_type(graph, weights=weights, **kwargs_res)
        self.optimise_partition(partition, n_iterations=number_iterations)
        is_stable = (self.optimise_partition(partition, n_iterations=1) == 0)
        bisect_values[resolution] = Bisect(partition, is_stable)
        return True
      else:
        return False
    def build_profile(min_res, max_res, min_res_diff=1e-3):
      # Are these two resolutions basically the same within machine precision?
      if (max_res - min_res) < min_res_diff:
        return
      # Did we already calculate this?
      if min_res in bisect_values and max_res in bisect_values and \
        bisect_values[min_res].partition.membership == bisect_values[max_res].partition.membership:
        return
      mid_res = (min_res + max_res)/2.
      if linear_bisection:
        min_p = bisect_values[min_res].partition
        max_p = bisect_values[max_res].partition
        mid_res = (max_p.bisect_value() - min_p.bisect_value())/(max_res - min_res)
      expand_profile(mid_res, min_res_diff)
      # Is there a sufficient difference between the bisection values?
      diff_bisect_value = abs(bisect_func(bisect_values[min_res].partition) - bisect_func(bisect_values[max_res].partition))
      if diff_bisect_value < min_diff_bisect_value:
        return
      # build profile recursively.
      build_profile(min_res, mid_res, min_res_diff)
      build_profile(mid_res, max_res, min_res_diff)
    min_res, max_res = resolution_range
    expand_profile(min_res)
    expand_profile(max_res)
    build_profile(min_res, max_res)
    # Post-processing of profile
    def clean_stepwise(bisect_values):
      # Check best partition for each resolution parameter
      for res, bisect in bisect_values.items():
        max_q = -float('inf')
        best_p = None
        for res_other, bisect_other in bisect_values.items():
          q = bisect_other.partition.quality(resolution_parameter=res)
          if q > max_q:
            max_q = q
            best_p = bisect_other.partition
        bisect_values[res] = Bisect(best_p, False)
      # Check for unique partitions
      unique_partitions = {}
      for res, bisect in sorted(bisect_values.items()):
        # Make membership hashable
        bisect.partition.renumber_communities()
        m = tuple(bisect.partition.membership)
        if m not in unique_partitions:
          unique_partitions[m] = bisect.partition
      return sorted(unique_partitions.values(), key=lambda p: p.resolution_parameter)
    def ensure_monotonicity(bisect_values, new_res):
      # First check if this partition improves on any other partition
      for res, bisect in bisect_values.items():
        if new_res.quality(res) > bisect.partition.quality(res):
          # We found a better partition, let's keep it.
          break
      else:
        # We couldn't find a better partition, so just return
        return
      # There is some resolution for which this partition is better, so let's
      # add it to the list of partitions.
      bisect_values[new_res.resolution_parameter] = Bisect(new_res, False)
    def find_partition(self, graph, partition_type, weights=None, **kwargs):
      # Store current settings of optimiser
      refine_partition = self.refine_partition
      # Set settings for finding partitions
      self.refine_partition = False
      partition = partition_type(graph, weights=weights, **kwargs)
      self.optimise_partition(partition, n_iterations=number_iterations)
      is_stable = (self.optimise_partition(partition, n_iterations=1) == 0)
      # Restore settings
      self.refine_partition = refine_partition
      return Bisect(partition, is_stable)
    # Make sure we do at least some iterations of moving nodes.
    kwargs_min = kwargs.copy()
    kwargs_min['resolution_parameter'] = min_res
    bisect_min = find_partition(self, graph, partition_type, weights, **kwargs_min)
    bisect_values[bisect_min.partition.resolution_parameter] = bisect_min.partition
    kwargs_max = kwargs.copy()
    kwargs_max['resolution_parameter'] = max_res
    bisect_max = find_partition(self, graph, partition_type, weights, **kwargs_max)
    bisect_values[bisect_max.partition.resolution_parameter] = bisect_max.partition
    min_b = bisect_func(bisect_min.partition)
    max_b = bisect_func(bisect_max.partition)
    while abs(min_b - max_b) > min_diff_bisect_value and \
          abs(bisect_min.partition.resolution_parameter - bisect_max.partition.resolution_parameter) > min_diff_resolution:
      if linear_bisection:
        mid_res = bisect_min.partition.resolution_parameter - \
          (bisect_func(bisect_min.partition) - 0.0) * \
          (bisect_max.partition.resolution_parameter - bisect_min.partition.resolution_parameter) / \
          (bisect_func(bisect_max.partition) - bisect_func(bisect_min.partition))
        if mid_res < bisect_min.partition.resolution_parameter or \
           mid_res > bisect_max.partition.resolution_parameter:
          mid_res = (bisect_min.partition.resolution_parameter + bisect_max.partition.resolution_parameter)/2.0
      else:
          mid_res = (bisect_min.partition.resolution_parameter + bisect_max.partition.resolution_parameter)/2.0
      kwargs_mid = kwargs.copy()
      kwargs_mid['resolution_parameter'] = mid_res
      bisect_mid = find_partition(self, graph, partition_type, weights, **kwargs_mid)
      ensure_monotonicity(bisect_values, bisect_mid.partition)
      mid_b = bisect_func(bisect_mid.partition)
      if mid_b > 0:
        bisect_max = bisect_mid
        max_b = mid_b
      else:
        bisect_min = bisect_mid
        min_b = mid_b
    return sorted((bisect.partition for res, bisect in
      bisect_values.items()), key=lambda x: x.resolution_parameter)