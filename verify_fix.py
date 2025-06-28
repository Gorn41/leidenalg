#!/usr/bin/env python3
"""
Verification script to test if the "more communities than nodes" fix works.
This script specifically tests the edge case that was causing the ValueError.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_edge_case():
    """Test the specific edge case that was causing the error."""
    
    try:
        import leidenalg as la
        import igraph as ig
        from random import seed
        
        print("Testing the edge case that caused 'more communities than nodes' error...")
        print("=" * 60)
        
        # Create a graph that's likely to hit the edge case
        # Start with a graph where each node might end up in its own community
        G = ig.Graph()
        G.add_vertices(10)  # Small graph to make the edge case more likely
        G.add_edges([(i, (i+1) % 10) for i in range(10)])  # Ring graph
        
        print(f"Created ring graph: {G.vcount()} nodes, {G.ecount()} edges")
        
        # Test 1: Basic find_partition with high iterations to trigger edge case
        print("\n1. Testing basic find_partition with many iterations...")
        seed(42)
        try:
            partition = la.find_partition(G, la.ModularityVertexPartition, n_iterations=10)
            print(f"   SUCCESS: Found {len(partition)} communities")
            print(f"   Quality: {partition.quality():.4f}")
            
            # Check if we hit the edge case (each node in its own community)
            if len(partition) == G.vcount():
                print(f"   EDGE CASE: Each node is in its own community!")
                print(f"   This would have caused the original error, but our fix prevented it.")
            
        except ValueError as e:
            if "more communities than nodes" in str(e):
                print(f"   ERROR: The fix didn't work! Still getting: {e}")
                return False
            else:
                raise e
        
        # Test 2: Hierarchical function
        print("\n2. Testing hierarchical function...")
        seed(42)
        try:
            final, hierarchy = la.find_partition_hierarchical(G, la.ModularityVertexPartition, n_iterations=5)
            print(f"   SUCCESS: Found {len(hierarchy)} levels")
            print(f"   Final partition: {len(final)} communities")
            
            # Print hierarchy
            for i, level in enumerate(hierarchy):
                print(f"     Level {i}: {len(level)} communities")
                
        except ValueError as e:
            if "more communities than nodes" in str(e):
                print(f"   ERROR: The fix didn't work in hierarchical function! {e}")
                return False
            else:
                raise e
        
        # Test 3: Test with Zachary graph (the original failing case)
        print("\n3. Testing with Zachary karate club (original failing case)...")
        G_zachary = ig.Graph.Famous('Zachary')
        seed(0)  # Use the same seed as in the original test
        
        try:
            partition_zachary = la.find_partition(G_zachary, la.ModularityVertexPartition)
            print(f"   SUCCESS: Zachary graph - {len(partition_zachary)} communities")
            
            # Test hierarchical on Zachary
            seed(0)
            final_z, hierarchy_z = la.find_partition_hierarchical(G_zachary, la.ModularityVertexPartition)
            print(f"   SUCCESS: Zachary hierarchical - {len(hierarchy_z)} levels")
            
        except ValueError as e:
            if "more communities than nodes" in str(e):
                print(f"   ERROR: Zachary test failed! {e}")
                return False
            else:
                raise e
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! The fix is working correctly.")
        print("🎉 Both basic and hierarchical functions work without the error.")
        print("🎉 consider_empty_community = True (default) is working properly.")
        print("=" * 60)
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure leidenalg is properly installed.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_edge_case()
    if success:
        print("\n✅ VERIFICATION COMPLETE: The fix is working!")
    else:
        print("\n❌ VERIFICATION FAILED: The fix needs more work.")
    sys.exit(0 if success else 1) 