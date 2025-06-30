#!/bin/bash

# Clean installation script for leidenalg with hierarchical community detection
# This script builds everything from scratch without AddressSanitizer

set -e  # Exit on any error

echo "🧹 Clean installation of leidenalg (without AddressSanitizer)"
echo "=================================================="

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: You are not in a virtual environment."
    echo "   Recommendation: Create and activate a virtual environment first:"
    echo "   python -m venv venv && source venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted. Create a virtual environment first."
        exit 1
    fi
fi

# Clean any previous builds
echo "🗑️  Removing previous build artifacts..."
rm -rf build-deps/build build-deps/install
rm -rf build dist *.egg-info

# Build dependencies from scratch
echo ""
echo "🔨 Building igraph (clean release build)..."
bash scripts/build_igraph.sh

echo ""
echo "🔨 Building libleidenalg (clean release build)..."
bash scripts/build_libleidenalg.sh

# Install the Python package
echo ""
echo "🐍 Installing Python package..."
pip install -e .

# Test the installation
echo ""
echo "✅ Testing installation..."
python -c "
import leidenalg as la
import igraph as ig
print('✅ leidenalg imported successfully')

# Test basic functionality
G = ig.Graph.Famous('Zachary')
partition = la.find_partition(G, la.ModularityVertexPartition)
print(f'✅ Standard find_partition works: {len(partition)} communities')

# Test hierarchical functionality
final_partition, hierarchy = la.find_partition_hierarchical(G, la.ModularityVertexPartition)
print(f'✅ Hierarchical function works: {len(hierarchy)} levels')
print(f'✅ Final partition: {len(final_partition)} communities')

print('')
print('🎉 Installation completed successfully!')
print('🎉 No AddressSanitizer configuration needed!')
"

echo ""
echo "=================================================="
echo "✅ Clean installation completed successfully!"
echo ""
echo "Key improvements:"
echo "  ✅ No AddressSanitizer warnings"
echo "  ✅ No manual environment variable configuration needed"
echo "  ✅ Clean release build optimized for performance"
echo "  ✅ Both standard and hierarchical functions working"
echo ""
echo "You can now use leidenalg normally without any special setup:"
echo ""
echo "  import leidenalg as la"
echo "  import igraph as ig"
echo "  final_partition, hierarchy = la.find_partition_hierarchical(G, la.ModularityVertexPartition)"
echo "" 