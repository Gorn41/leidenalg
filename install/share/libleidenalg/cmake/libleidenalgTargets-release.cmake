#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "libleidenalg" for configuration "Release"
set_property(TARGET libleidenalg APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(libleidenalg PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/liblibleidenalg.so.0.11.0"
  IMPORTED_SONAME_RELEASE "liblibleidenalg.so.1"
  )

list(APPEND _cmake_import_check_targets libleidenalg )
list(APPEND _cmake_import_check_files_for_libleidenalg "${_IMPORT_PREFIX}/lib/liblibleidenalg.so.0.11.0" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
