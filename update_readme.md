# Hierarchical Community Detection

This enhanced version of `leidenalg` includes a powerful new feature for discovering the hierarchical structure of communities within a single, consistent optimization run. This is particularly valuable for analyzing complex systems where structure exists at multiple scales, such as:

- **Biological Networks**: Identifying local motifs, functional domains, and global architecture in protein interaction networks
- **Social Networks**: Discovering friend groups, communities, and broader social structures
- **Brain Networks**: Analyzing neural circuits, brain regions, and global connectivity patterns
- **Economic Networks**: Understanding local markets, sectors, and global economic relationships

## Key Advantages

✅ **True Hierarchical Structure**: Returns the *actual* hierarchy that emerges from the Leiden algorithm's internal aggregation process, not artificial multi-resolution results

✅ **Single Optimization Run**: Maintains consistency by capturing hierarchy from one optimization trajectory, avoiding the pitfalls of recursive clustering

✅ **Easy Installation**: Automated build process with embedded library paths - no manual environment configuration required

✅ **Backward Compatible**: Works with all existing `leidenalg` functionality while adding the new hierarchical capabilities

This method avoids common but incorrect approaches like using multiple resolution parameters or recursively clustering subgraphs, which do not preserve a single optimization trajectory. The returned hierarchy represents the genuine multi-scale community structure discovered during the algorithm's natural aggregation process.

## Quick Start

Want to try it right away? Here's a minimal example:

```bash
# Install (one-time setup)
git clone <repository-url> && cd leidenalg
python -m venv venv && source venv/bin/activate
./install.sh

# Use the hierarchical function
python -c "
import leidenalg as la
import igraph as ig

# Load a sample network
G = ig.Graph.Famous('Zachary')

# Find hierarchical communities
final_partition, hierarchy = la.find_partition_hierarchical(G, la.ModularityVertexPartition)

# Analyze results
print(f'Found {len(hierarchy)} hierarchical levels')
for i, level in enumerate(hierarchy):
    print(f'Level {i}: {len(level)} communities')
"
```

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

This version includes an enhanced installation process that automatically handles all dependencies and library paths. **No manual environment variable configuration is required!**

### Quick Installation (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd leidenalg

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the automated installation script
./install.sh
```

The installation script will automatically:
1. ✅ Build all required C++ dependencies (`libleidenalg` and `igraph`)
2. ✅ Compile the Python extension with embedded library paths (RPATH)
3. ✅ Install the package using `pip install -e .`
4. ✅ Run tests to verify the installation works correctly

### Manual Installation (Advanced Users)

If you prefer to install manually or need to customize the build process:

```bash
# 1. Clone and set up environment
git clone <repository-url>
cd leidenalg
python -m venv venv
source venv/bin/activate

# 2. Build C++ dependencies
bash scripts/build_libleidenalg.sh
bash scripts/build_igraph.sh

# 3. Install Python package (with embedded library paths)
pip install -e .

# 4. Test the installation
python -c "
import leidenalg as la
import igraph as ig
G = ig.Graph.Famous('Zachary')
final_partition, hierarchy = la.find_partition_hierarchical(G, la.ModularityVertexPartition)
print(f'✅ Success! Found {len(hierarchy)} levels with {len(final_partition)} communities')
"
```

### System Requirements

- **Python**: 3.7 or higher
- **C++ Compiler**: GCC 8+ or Clang 3.2+ (for building dependencies)
- **CMake**: Required for building C++ libraries
- **Git**: For cloning the repository

### What's Different About This Installation?

Unlike typical installations that require users to manually set `LD_LIBRARY_PATH`, this version:

- **Embeds Library Paths**: Uses RPATH/RUNPATH to embed library search paths directly in the compiled extension
- **No Environment Variables**: Works immediately after installation without any manual configuration
- **Cross-Platform**: Automatically detects the platform and applies appropriate linking settings
- **User-Friendly**: Provides clear error messages and automated testing

### Troubleshooting

**Import Error**: If you encounter import errors, ensure you're in the correct virtual environment:
```bash
source venv/bin/activate  # Activate the environment
python -c "import leidenalg"  # Should work without errors
```

**Build Errors**: Make sure you have the required build tools:
```bash
# Ubuntu/Debian
sudo apt-get install build-essential cmake git

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install cmake git

# macOS
xcode-select --install
brew install cmake
```

**Verification**: To verify the installation is working correctly:
```bash
python -c "
import leidenalg as la
print('✅ leidenalg imported successfully')
print('✅ Hierarchical function available:', hasattr(la, 'find_partition_hierarchical'))
"
```

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