import sys
import h5py
import numpy as np
from pygnuplot import gnuplot
import os

try:
    n_arg = int(sys.argv[1])
    n_path = sys.argv[2]
except IndexError:
    print ("Usage: " + sys.argv[0] + "[number_of_runs] [path_to_dir_with_Run]")
    sys.exit(-1)
except ValueError:
    print ("Usage: " + sys.argv[0] + "[number_of_runs] [path_to_dir_with_Run]")
    sys.exit(-1)
if os.path.isdir(sys.argv[2]) == False:
    print ("Usage: " + sys.argv[0] + "[number_of_runs] [path_to_dir_with_Run]")
    sys.exit(-1)
print (n_arg)
hf = [ {} for x in range (1,n_arg+1) ]
chem = [ {} for x in range (1,n_arg+1) ]
d = [ {} for x in range (1,n_arg+1) ]

for i in range (0,n_arg):
    f = n_path + "/Run_" + str(i+1) + "/a001outp.hdf5"
    print(f)
    hf[i] = h5py.File(f,'r')
    chem[i] = hf[i].get('chm')
    d[i] = np.array(chem[i])
    hf[i].close()
    n,m,l = d[i].shape

mmean = np.zeros((n,m,l),np.float)

for i in range(0,n-1):
    for j in range(0,m-1):
        for k in range(0,l-1):
            sum = 0.0
            for h in range(1,n_arg+1):
                sum += d[h-1][i,j,k]
            mmean[i,j,k] = sum/n_arg


outsize=int(n*m)
outmean = np.zeros(outsize)
idx=0

xtab = np.zeros(outsize)
ytab = np.zeros(outsize)

for a in range (0,n):
    for b in range (0,m):
        xtab[idx] = a
        ytab[idx] = b
        outmean[idx] = float(mmean[a,b,1])
        idx = idx+1

f = "2m_no2_mean.csv"
np.savetxt(f, np.c_[xtab, ytab, outmean], delimiter='\t', comments='',header='X, Y, Z value')


g = gnuplot.Gnuplot()

g.set(terminal='pngcairo size 880,480',
    output = '"2m_no2_mean.png"',
    title = '"NO2 concentration at 2m height"',
    xlabel = '"X position"',
    ylabel = '"Y position"',
    palette = 'defined ( 0 "green", 1 "yellow", 20 "orange", 100 "red", 200 "purple")',
    cblabel = '"ug/m3"',
    pm3d = 'interpolate 1,1',
    dgrid3d = '50,50 qnorm 2')
g.splot('"2m_no2_mean.csv" using 1:2:3 with pm3d notitle')
