import sys
import h5py
import numpy as np

#height
# 1 = 2m
# 2 = 4m
# 3 = 6m
# etc
h = 1

f = "a001outp.hdf5"
hf = h5py.File(f,'r')
n = hf.get('chm')
d = np.array(n)
hf.close()

s = d.shape

outsize=int(s[0]*s[1])
outhdf = np.zeros(outsize)
idx=0

for a in range (0,int(s[0])):
    for b in range (0,int(s[1])):
        outhdf[idx] = float(d[a,b,h]*1000000000.0)
        idx = idx+1

f = "output_new.csv"
np.savetxt(f, outhdf, delimiter=",",
            comments='',header='NO2')

