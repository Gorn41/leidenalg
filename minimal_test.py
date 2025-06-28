#!/usr/bin/env python3

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

print("Testing leidenalg hierarchical functionality...")

try:
    import igraph as ig
    print("✓ igraph imported successfully")
except ImportError as e:
    print(f"✗ Failed to import igraph: {e}")
    sys.exit(1)

try:
    import leidenalg as la
    print("✓ leidenalg imported successfully")
except ImportError as e:
    print(f"✗ Failed to import leidenalg: {e}")
    sys.exit(1)

# Test 1: Basic functionality test
print("\n=== Test 1: Basic find_partition ===")
try:
    G = ig.Graph.Famous('Zachary')
    partition = la.find_partition(G, la.ModularityVertexPartition)
    print(f"✓ Basic find_partition works: {len(partition)} communities found")
except Exception as e:
    print(f"✗ Basic find_partition failed: {e}")
    sys.exit(1)

# Test 2: Hierarchical functionality test
print("\n=== Test 2: Hierarchical find_partition ===")
try:
    G = ig.Graph.Famous('Zachary')
    final_partition, hierarchy = la.find_partition_hierarchical(G, la.ModularityVertexPartition)
    print(f"✓ Hierarchical find_partition works!")
    print(f"  - Final partition: {len(final_partition)} communities")
    print(f"  - Hierarchy levels: {len(hierarchy)}")
    print(f"  - Community counts per level: {[len(h) for h in hierarchy]}")
    
    # Verify hierarchy properties
    for i in range(len(hierarchy) - 1):
        curr_communities = len(hierarchy[i])
        next_communities = len(hierarchy[i + 1])
        if curr_communities < next_communities:
            print(f"✗ Hierarchy violation: level {i} has {curr_communities} communities, level {i+1} has {next_communities}")
            sys.exit(1)
    
    print("✓ Hierarchy properties verified")
    
except Exception as e:
    print(f"✗ Hierarchical find_partition failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🎉 All tests passed! The fix is working correctly.") 