#!/bin/bash

# Build script for igraph library
# This script builds the igraph C library that libleidenalg depends on

set -e  # Exit on any error

# Get the root directory of the project
if [ -n "$LEIDENALG_ROOT" ]; then
    ROOT_DIR="$LEIDENALG_ROOT"
else
    ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

echo "Using root dir $ROOT_DIR"

# Paths for source and installation
SRC_DIR="$ROOT_DIR/build-deps/src/igraph"
BUILD_DIR="$ROOT_DIR/build-deps/build/igraph"
INSTALL_DIR="$ROOT_DIR/build-deps/install"

# Clone the repository if it doesn't exist
if [ ! -d "$SRC_DIR" ]; then
    echo "Cloning igraph..."
    mkdir -p "$(dirname "$SRC_DIR")"
    git clone https://github.com/igraph/igraph.git "$SRC_DIR"
fi

cd "$SRC_DIR"

# Checkout the specific version we want
echo "Checking out 0.10.13 in $SRC_DIR"
git fetch --tags
git checkout 0.10.13

# Configure the build
echo "Configure igraph build"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Use a clean release build without AddressSanitizer
cmake "$SRC_DIR" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR" \
    -DCMAKE_C_FLAGS_RELEASE="-O3 -DNDEBUG" \
    -DCMAKE_CXX_FLAGS_RELEASE="-O3 -DNDEBUG" \
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
    -DBUILD_SHARED_LIBS=ON

# Build the library
echo "Build igraph"
make -j$(nproc)

# Install the library
echo "Install igraph to $INSTALL_DIR/"
make install

echo "igraph build completed successfully"
