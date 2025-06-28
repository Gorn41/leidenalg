#!/usr/bin/env python3

import sys
import os

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import leidenalg as la
import igraph as ig
from random import seed

def test_hierarchical_community_detection():
    """Test the hierarchical community detection feature."""
    
    print("=" * 60)
    print("Testing Hierarchical Community Detection")
    print("=" * 60)
    
    # Create a test graph - using Zachary's karate club
    G = ig.Graph.Famous('Zachary')
    print(f"Graph: {G.vcount()} nodes, {G.ecount()} edges")
    
    # Set seed for reproducibility
    seed(42)
    
    # Test 1: Basic find_partition (should work with our fix)
    print("\n1. Testing basic find_partition...")
    try:
        partition_basic = la.find_partition(G, la.ModularityVertexPartition, n_iterations=2)
        print(f"   SUCCESS: Found {len(partition_basic)} communities")
        print(f"   Quality: {partition_basic.quality():.4f}")
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    # Test 2: Hierarchical community detection
    print("\n2. Testing find_partition_hierarchical...")
    try:
        seed(42)  # Reset seed
        final_partition, hierarchy = la.find_partition_hierarchical(
            G, la.ModularityVertexPartition, n_iterations=-1
        )
        print(f"   SUCCESS: Hierarchy with {len(hierarchy)} levels")
        print(f"   Final partition: {len(final_partition)} communities")
        print(f"   Final quality: {final_partition.quality():.4f}")
        
        # Print hierarchy structure
        print("   Hierarchy structure:")
        for i, level in enumerate(hierarchy):
            print(f"     Level {i}: {len(level)} communities, sizes: {level.sizes()}")
            
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Hierarchy properties validation
    print("\n3. Validating hierarchy properties...")
    try:
        # Check that hierarchy is properly nested
        for i in range(1, len(hierarchy)):
            prev_level = hierarchy[i-1]
            curr_level = hierarchy[i]
            
            # Check nested structure
            for v1 in range(G.vcount()):
                for v2 in range(v1 + 1, G.vcount()):
                    if prev_level.membership[v1] == prev_level.membership[v2]:
                        if curr_level.membership[v1] != curr_level.membership[v2]:
                            raise ValueError(f"Hierarchy not properly nested at level {i}")
            
            # Check non-increasing number of communities
            if len(curr_level) > len(prev_level):
                raise ValueError(f"Number of communities should be non-increasing: level {i}")
        
        print("   SUCCESS: All hierarchy properties validated")
        
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    # Test 4: Compare with directed graph
    print("\n4. Testing with directed graph...")
    try:
        G_dir = ig.Graph(directed=True)
        G_dir.add_vertices(6)
        G_dir.add_edges([(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3)])
        
        seed(42)
        final_dir, hierarchy_dir = la.find_partition_hierarchical(
            G_dir, la.RBConfigurationVertexPartition, n_iterations=-1
        )
        print(f"   SUCCESS: Directed graph - {len(hierarchy_dir)} levels")
        print(f"   Final: {len(final_dir)} communities")
        
    except Exception as e:
        print(f"   ERROR: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("All tests PASSED! Hierarchical community detection is working correctly.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_hierarchical_community_detection()
    sys.exit(0 if success else 1) 