CXX=g++
OPT = -O3

CXXFLAGS = $(INCLUDE_FLAG) $(OPT)

all: project

project: project.cpp
	$(CXX) -c -o project.o $<
	$(CXX) -shared -o libproject.dll project.o $(LIB_FLAGS)

