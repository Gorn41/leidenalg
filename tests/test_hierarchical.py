import unittest
import igraph as ig
import leidenalg as la
from random import seed

class HierarchicalTest(unittest.TestCase):
    def setUp(self):
        self.G = ig.Graph.Famous('Zachary')
        # We seed the RNG to make sure we can reproduce the tests
        seed(0)

    def _test_hierarchy_properties(self, G, partition_type, **kwargs):
        # 1. Compare with the standard find_partition function
        # We re-seed the RNG before each call to ensure they are comparable
        seed(0)
        final_partition_standard = la.find_partition(G, partition_type, **kwargs)
        seed(0)
        final_partition_hier, hierarchy = la.find_partition_hierarchical(G, partition_type, **kwargs)

        # 2. Check that the final partitions are identical
        #    NOTE: This is commented out because the Python-based loop in the
        #    hierarchical function will not be perfectly identical to the
        #    internal C++ loop, even when seeded. The structural tests
        #    below are more important.
        self.assertEqual(final_partition_standard.membership, final_partition_hier.membership)
        self.assertEqual(final_partition_hier.membership, hierarchy[-1].membership)

        # 3. Check properties of the hierarchy
        for i, partition in enumerate(hierarchy):
            # 3a. Mapping to Original Nodes: Check that all partitions are for the original graph
            self.assertEqual(partition.graph.vcount(), G.vcount(), "Partition graph should be the original graph.")
            self.assertEqual(len(partition.membership), G.vcount(), "Partition membership should be for the original graph.")

            if i > 0:
                prev_partition = hierarchy[i-1]
                # 3b. Nested Structure: Check that the hierarchy is properly nested
                # If two nodes are in the same community at a previous (finer) level,
                # they must be in the same community at the current (coarser) level.
                for v1 in range(G.vcount()):
                    for v2 in range(v1 + 1, G.vcount()):
                        if prev_partition.membership[v1] == prev_partition.membership[v2]:
                            self.assertEqual(partition.membership[v1], partition.membership[v2],
                                             "Hierarchy is not properly nested.")

                # 3c. Number of Communities: Check that it is non-increasing
                self.assertLessEqual(len(partition), len(prev_partition),
                                     "Number of communities should be non-increasing.")

    def test_find_partition_hierarchical_undirected(self):
        self._test_hierarchy_properties(self.G, la.ModularityVertexPartition)

    def test_find_partition_hierarchical_directed(self):
        # Create a small directed graph
        G_dir = ig.Graph(directed=True)
        G_dir.add_vertices(6)
        G_dir.add_edges([(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3)])
        self._test_hierarchy_properties(G_dir, la.RBConfigurationVertexPartition)

if __name__ == '__main__':
    unittest.main()