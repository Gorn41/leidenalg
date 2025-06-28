# Hierarchical Community Detection

This version of `leidenalg` includes a new feature for discovering the hierarchical structure of communities within a single, consistent optimization run. This is particularly useful for analyzing systems where structure exists at multiple scales, such as identifying local motifs, functional domains, and global architecture in protein interaction networks.

This method avoids common but incorrect approaches like using multiple resolution parameters or recursively clustering subgraphs, which do not preserve a single optimization trajectory. The returned hierarchy is the *true* hierarchy that emerges from the Leiden algorithm's internal aggregation process.

## New Function: `find_partition_hierarchical()`

To capture the hierarchical community structure, use the new `leidenalg.find_partition_hierarchical()` function. It works similarly to the standard `find_partition()` but returns both the final, optimized partition and a list of all intermediate partitions discovered during the aggregation process.

**Function Signature:**

```python
find_partition_hierarchical(graph, partition_type, n_iterations=-1, **kwargs)
```

-   **`graph`**: The `igraph.Graph` object to analyze.
-   **`partition_type`**: The partition class to use (e.g., `leidenalg.RBConfigurationVertexPartition`).
-   **`n_iterations`**: The number of aggregation levels to perform. The default value of **-1** is highly recommended, as it runs the algorithm until it converges naturally, revealing the true depth of the hierarchy.
-   **`**kwargs`**: Other keyword arguments are passed to the partition constructor (e.g., `resolution_parameter`, `weights`).

**Return Value:**

A tuple containing:
1.  **`final_partition`**: The fully optimized `VertexPartition` object. This result is equivalent to what the original `find_partition()` function would return.
2.  **`hierarchy`**: A list of `VertexPartition` objects. Each element represents a single level of the hierarchy, from a fine-grained partition at `hierarchy[0]` to the final, coarse-grained partition at `hierarchy[-1]`.

## Installation

To install this version with hierarchical community detection support:

```bash
# Clone the repository
git clone <repository-url>
cd leidenalg

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the installation script
./install.sh
```

The installation script will:
1. Build all required C++ dependencies
2. Install the Python package with embedded library paths
3. Test the installation to ensure everything works

**No manual `LD_LIBRARY_PATH` configuration needed!** The library paths are automatically embedded during installation.

### Example Usage

Here is how you can use the new function to analyze a network and extract its hierarchical community structure:

```python
import leidenalg as la
import igraph as ig
import numpy as np

# Example: Create a weighted, directed graph from a random matrix
attention_matrix = np.random.rand(100, 100)
G = ig.Graph.Weighted_Adjacency(attention_matrix.tolist(), mode="directed", attr="weight", loops=False)

# Use the new hierarchical function to find communities at all levels
# Using RBConfigurationVertexPartition as it's suitable for directed, weighted graphs.
print("Finding hierarchical communities...")
final_partition, hierarchy = la.find_partition_hierarchical(
    G,
    la.RBConfigurationVertexPartition,
    resolution_parameter=1.0
)

# --- Analyze the Results ---
print(f"\nAnalysis Complete.")
print(f"The algorithm converged in {len(hierarchy)} levels.")
print(f"The final partition has {len(final_partition)} communities.")

# The `hierarchy` list contains the full, nested hierarchical structure.
# Level 0 (hierarchy[0]) -> Most fine-grained communities
# Intermediate levels -> Intermediate structures
# Final level (hierarchy[-1]) -> Most coarse-grained, global structure

for i, partition_level in enumerate(hierarchy):
    print(f"\n--- Hierarchy Level {i} ---")
    print(f"Number of communities: {len(partition_level)}")
    # You can inspect the membership of each level:
    # print(partition_level.membership)
    # Or get the sizes of the communities:
    print(f"Community sizes: {partition_level.sizes()}")

# You can validate that the final partition is the same as the last level of the hierarchy
assert final_partition.membership == hierarchy[-1].membership
print("\nValidation successful: Final partition matches the last level of the hierarchy.")
``` 