import unittest
import leidenalg as la
import igraph as ig

class HierarchicalTest(unittest.TestCase):
    def setUp(self):
        # A well-known graph with clear community structure
        self.G = ig.Graph.Famous('Zachary')

    def test_find_partition_hierarchical(self):
        # 1. Run the new hierarchical function
        final_partition, hierarchy = la.find_partition_hierarchical(self.G, la.ModularityVertexPartition)

        # 2. Validate the output types
        self.assertIsInstance(final_partition, la.VertexPartition.ModularityVertexPartition)
        self.assertIsInstance(hierarchy, list)
        
        # 3. Ensure the hierarchy is not empty and contains partition objects
        self.assertGreater(len(hierarchy), 0)
        self.assertIsInstance(hierarchy[0], la.VertexPartition.ModularityVertexPartition)

        # 4. The final partition should be the last element of the hierarchy
        self.assertEqual(final_partition.membership, hierarchy[-1].membership)

        # 5. Check that all partitions in the hierarchy are for the original graph
        for partition in hierarchy:
            self.assertEqual(partition.graph.vcount(), self.G.vcount())
            self.assertEqual(len(partition.membership), self.G.vcount())

        # 6. Check that the number of communities is non-increasing
        for i in range(len(hierarchy) - 1):
            self.assertGreaterEqual(len(hierarchy[i]), len(hierarchy[i+1]))

if __name__ == '__main__':
    unittest.main() 