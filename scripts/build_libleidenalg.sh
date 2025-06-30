#!/bin/bash

# Build script for libleidenalg library
# This script builds the C++ library that leidenalg depends on

set -e  # Exit on any error

# Get the root directory of the project
if [ -n "$LEIDENALG_ROOT" ]; then
    ROOT_DIR="$LEIDENALG_ROOT"
else
    ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

echo "Using root dir $ROOT_DIR"

# Paths for source and installation
SRC_DIR="$ROOT_DIR/build-deps/src/libleidenalg"
BUILD_DIR="$ROOT_DIR/build-deps/build/libleidenalg"
INSTALL_DIR="$ROOT_DIR/build-deps/install"

# Clone the repository if it doesn't exist
if [ ! -d "$SRC_DIR" ]; then
    echo "Cloning libleidenalg..."
    mkdir -p "$(dirname "$SRC_DIR")"
    git clone https://github.com/vtraag/libleidenalg.git "$SRC_DIR"
fi

cd "$SRC_DIR"

# Checkout the specific version we want
echo "Checking out 0.11.0 in $SRC_DIR"
git fetch --tags
git checkout 0.11.0

# Configure the build
echo "Configure libleidenalg build"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Use a clean release build without AddressSanitizer
cmake "$SRC_DIR" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR" \
    -DCMAKE_C_FLAGS_RELEASE="-O3 -DNDEBUG" \
    -DCMAKE_CXX_FLAGS_RELEASE="-O3 -DNDEBUG" \
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON

# Build the library
echo "Build libleidenalg"
make -j$(nproc)

# Install the library
echo "Install libleidenalg to $INSTALL_DIR/"
make install

echo "libleidenalg build completed successfully"
