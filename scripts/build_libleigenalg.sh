# Set extra cmake arguments, if any
EXTRA_CMAKE_ARGS=$@

# Add AddressSanitizer flags for debugging
EXTRA_CMAKE_ARGS="${EXTRA_CMAKE_ARGS} -DCMAKE_CXX_FLAGS='-fsanitize=address -g' -DCMAKE_EXE_LINKER_FLAGS='-fsanitize=address' -DCMAKE_SHARED_LINKER_FLAGS='-fsanitize=address'"

# Try to use Ninja if it's available, otherwise use Make
if which ninja &> /dev/null; then
  EXTRA_CMAKE_ARGS="${EXTRA_CMAKE_ARGS} -G Ninja"
fi 