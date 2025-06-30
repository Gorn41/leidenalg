#!/bin/bash

# Installation script for leidenalg with hierarchical community detection
# This script will build all dependencies and install the package so it works
# without requiring LD_LIBRARY_PATH to be set manually.

set -e  # Exit on any error

echo "=== Installing leidenalg with hierarchical community detection ==="

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "WARNING: Not in a virtual environment. Consider using 'python -m venv venv && source venv/bin/activate'"
    echo "Continuing with system Python..."
fi

# Build C++ dependencies
echo "Building C++ dependencies..."
bash scripts/build_libleidenalg.sh
bash scripts/build_igraph.sh

# Install Python package with embedded library paths
echo "Installing Python package..."
pip install -e .

# Test the installation
echo "Testing installation..."
python -c "
import leidenalg as la
import igraph as ig
print('✓ Basic import successful')

# Test hierarchical function
G = ig.Graph.Famous('Zachary')
final_partition, hierarchy = la.find_partition_hierarchical(G, la.ModularityVertexPartition)
print(f'✓ Hierarchical function works: {len(hierarchy)} levels, {len(final_partition)} communities')
"

echo ""
echo "=== Installation Complete! ==="
echo ""
echo "The package is now installed and ready to use."
echo "No need to set LD_LIBRARY_PATH - the library paths are embedded."
echo ""
echo "For optimal performance (especially with multiprocessing), run:"
echo "  source scripts/setup_leidenalg_env.sh"
echo "  python your_script.py"
echo ""
echo "Or use the wrapper script:"
echo "  python scripts/run_with_leidenalg.py your_script.py"
echo ""
echo "Usage example:"
echo "  import leidenalg as la"
echo "  import igraph as ig"
echo "  G = ig.Graph.Famous('Zachary')"
echo "  final_partition, hierarchy = la.find_partition_hierarchical(G, la.ModularityVertexPartition)"
echo "" 