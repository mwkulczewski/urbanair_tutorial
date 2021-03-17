#!/bin/bash

export PATH=$PATH:/usr/lib64/openmpi/bin

mpirun -np 4 /vecma/urbanair

python3.6 $HOME/urbanair_tutorial/process_hdf5.py
