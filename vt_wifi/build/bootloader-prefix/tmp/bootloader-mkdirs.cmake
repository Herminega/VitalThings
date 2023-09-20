# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "/Users/herminealfsen/esp-idf/components/bootloader/subproject"
  "/Users/herminealfsen/vt_wifi_test/vt_wifi/build/bootloader"
  "/Users/herminealfsen/vt_wifi_test/vt_wifi/build/bootloader-prefix"
  "/Users/herminealfsen/vt_wifi_test/vt_wifi/build/bootloader-prefix/tmp"
  "/Users/herminealfsen/vt_wifi_test/vt_wifi/build/bootloader-prefix/src/bootloader-stamp"
  "/Users/herminealfsen/vt_wifi_test/vt_wifi/build/bootloader-prefix/src"
  "/Users/herminealfsen/vt_wifi_test/vt_wifi/build/bootloader-prefix/src/bootloader-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/Users/herminealfsen/vt_wifi_test/vt_wifi/build/bootloader-prefix/src/bootloader-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "/Users/herminealfsen/vt_wifi_test/vt_wifi/build/bootloader-prefix/src/bootloader-stamp${cfgdir}") # cfgdir has leading slash
endif()
