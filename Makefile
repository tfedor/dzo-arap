CXX=g++
INCLUDE_FLAG = -I lib/eigen
LIB_FLAGS = 
OPT = -O2

CXXFLAGS = $(INCLUDE_FLAG) $(OPT)

all: project

project: project.cpp
	$(CXX) -c -o project.o $(INCLUDE_FLAG) $(LIB_FLAGS) $<
	$(CXX) -shared -o libproject.dll project.o $(LIB_FLAGS)

