cmake_minimum_required(VERSION 3.13)
project(ComplexityPass)

find_package(LLVM REQUIRED CONFIG)

include_directories(${LLVM_INCLUDE_DIRS})
add_definitions(${LLVM_DEFINITIONS})

add_library(ComplexityPass MODULE ComplexityPass.cpp)

target_link_libraries(ComplexityPass LLVM)
