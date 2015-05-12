CXX=g++
OPT = -O3

CXXFLAGS = $(INCLUDE_FLAG) $(OPT)

all: project

project: arap.cpp
	$(CXX) -c -o arap.o $<
	$(CXX) -shared -o libarap.dll arap.o $(LIB_FLAGS)

