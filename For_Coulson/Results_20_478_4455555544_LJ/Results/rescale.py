import numpy as np
import os

with open('rescale.dat', 'r') as f:
   rescale_array = np.genfromtxt(f, dtype=float)

################################################
if os.path.isfile('initial_test_A_aux.dat')==False:
    os.rename('test_A_aux.dat', 'initial_test_A_aux.dat')
    os.rename('test_B_aux.dat', 'initial_test_B_aux.dat')
    os.rename('test_A_crds.dat', 'initial_test_A_crds.dat')
    os.rename('test_B_crds.dat', 'initial_test_B_crds.dat')

with open('initial_test_A_aux.dat', 'r') as f:
   lines = f.readlines()
pbc = lines[3].strip().split()
print(lines)
new_pbc = '{:<10.8f}    {:<10.8f}\n'.format(rescale_array[0]*float(pbc[0]),rescale_array[1]*float(pbc[1]))
new_rpbc = '{:<10.8f}    {:<10.8f}\n'.format(1/(rescale_array[0]*float(pbc[0])),1/(rescale_array[1]*float(pbc[1])))
lines[3] = new_pbc
lines[4] = new_rpbc
print(lines)
with open('test_A_aux.dat', 'w') as f:
   f.writelines(lines) 

with open('initial_test_B_aux.dat', 'r') as f:
   lines = f.readlines()
pbc = lines[3].strip().split()
print(lines)
new_pbc = '{:<10.8f}    {:<10.8f}\n'.format(rescale_array[0]*float(pbc[0]),rescale_array[1]*float(pbc[1]))
new_rpbc = '{:<10.8f}    {:<10.8f}\n'.format(1/(rescale_array[0]*float(pbc[0])),1/(rescale_array[1]*float(pbc[1])))
lines[3] = new_pbc
lines[4] = new_rpbc
print(lines)
with open('test_B_aux.dat', 'w') as f:
   f.writelines(lines)


#################################################
with open('initial_test_A_crds.dat', 'r') as f:
   array = np.genfromtxt(f)

array[:,0]*=rescale_array[0]
array[:,1]*=rescale_array[1]

with open('test_A_crds.dat', 'w') as f:
   np.savetxt(f, array, fmt='%.8f')

with open('initial_test_B_crds.dat', 'r') as f:
   array = np.genfromtxt(f)

array[:,0]*=rescale_array[0]
array[:,1]*=rescale_array[1]

with open('test_B_crds.dat', 'w') as f:
   np.savetxt(f, array, fmt='%.8f')
##################################################


