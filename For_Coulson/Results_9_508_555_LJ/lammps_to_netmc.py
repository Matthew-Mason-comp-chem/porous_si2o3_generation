import shutil

import numpy as np
import time
import sys
import os
import re, yaml
try:
    from yaml import CSafeLoader as Loader
except ImportError:
    from yaml import SafeLoader as Loader


with open('netmc.inpt', 'r') as f:
    skip = f.readline()
    FinalFolder = f.readline().strip().split()
    skip = f.readline()
    skip = f.readline()
    InitialFolder = f.readline().strip().split()

InitialFolder = InitialFolder[0][2:]
FinalFolder   = FinalFolder[0][2:]

print(InitialFolder)
print(FinalFolder)




if os.path.isfile(FinalFolder+'/Si_results.dat')==True:

    print('Write Si Positions')

    ###############################################################
    # Si

    with open(FinalFolder+'/Si_results.dat', 'r') as f:
        natoms = np.genfromtxt(f, skip_header=2, max_rows=1)
    natoms = int(natoms[0])

    with open(FinalFolder+'/Si_results.dat', 'r') as f:
        nbonds = np.genfromtxt(f, skip_header=4, max_rows=1)
    nbonds = int(nbonds[0])

    with open(FinalFolder+'/Si_results.dat', 'r') as f:
        dims = np.genfromtxt(f, skip_header=9, max_rows=3)
    dims = dims[:,1]

    with open(FinalFolder+'/Si_results.dat', 'r') as f:
        crds_array = np.genfromtxt(f, skip_header=27, max_rows=natoms)

    refs = crds_array[:, 0]
    refs = [int(i) for i in refs]

    with open(FinalFolder+'/test_Si_crds.dat', 'w') as f:
        for i in range(min(refs), max(refs)+1):
            ref = refs.index(i)
            f.write('{:<24}{:<24}{:<24}\n'.format(crds_array[int(ref), 3], crds_array[int(ref), 4], crds_array[int(ref), 5]))

    with open(FinalFolder+'/Si_results.dat', 'r') as f:
        bonds_array = np.genfromtxt(f, skip_header=27+natoms+3+natoms+3, max_rows=nbonds)

    nodes = {}
    for i in refs:
        nodes['{:}'.format(i-1)] = {}
        nodes['{:}'.format(i-1)]['net'] = []
    for i in range(bonds_array.shape[0]):
        atom0, atom1 = int(bonds_array[i,2]-1), int(bonds_array[i,3]-1)
        nodes['{:}'.format(atom0)]['net'].append(atom1)
        nodes['{:}'.format(atom1)]['net'].append(atom0)

    with open(FinalFolder+'/test_Si_net.dat', 'w') as f:
        for i in range(min(refs), max(refs)+1):
            node = int(i-1)
            for j in range(len(nodes['{:}'.format(node)]['net'])):
                f.write('{:<10}'.format(nodes['{:}'.format(node)]['net'][j]))
            f.write('\n')

    shutil.copy(FinalFolder+'/test_A_dual.dat', FinalFolder+'/test_Si_dual.dat')

    with open(FinalFolder+'/test_Si_aux.dat', 'w') as f:
        f.write('{:}\n'.format(natoms))
        f.write('{:<10}{:<10}\n'.format(3,3))
        f.write('2DE\n')
        f.write('{:<24.6f}{:<24.6f}\n'.format(dims[0], dims[1]))
        f.write('{:<24.6f}{:<24.6f}\n'.format(1/dims[0], 1/dims[1]))


import time
#time.sleep(100)

if os.path.isfile(FinalFolder+'/BN_results.dat')==True:
    print('Write BN Positions')

    ###############################################################
    # Si

    with open(FinalFolder+'/BN_results.dat', 'r') as f:
        natoms = np.genfromtxt(f, skip_header=2, max_rows=1)
    natoms = int(natoms[0])

    with open(FinalFolder+'/BN_results.dat', 'r') as f:
        nbonds = np.genfromtxt(f, skip_header=4, max_rows=1)
    nbonds = int(nbonds[0])
    print(time.sleep(100))

    with open(FinalFolder+'/BN_results.dat', 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if 'Atoms' in line:
            start_line = i + 2  # Assuming that the atom coordinates start two lines after the 'Atoms' keyword
            break

    with open(FinalFolder+'/BN_results.dat', 'r') as f:
        crds_array = np.genfromtxt(f, skip_header=start_line, max_rows=natoms)

    refs = array[:, 0]
    refs = [int(i) for i in refs]



    with open(FinalFolder+'/BN_results.dat', 'r') as f:
        dims = np.genfromtxt(f, skip_header=9, max_rows=3)
    dims = dims[:,1]


    with open(FinalFolder+'/test_BN_crds.dat', 'w') as f:
        for i in range(min(refs), max(refs)+1):
            ref = refs.index(i)
            f.write('{:<24}{:<24}{:<24}\n'.format(crds_array[int(ref), 3], crds_array[int(ref), 4], crds_array[int(ref), 5]))

    with open(FinalFolder+'/BN_results.dat', 'r') as f:
        if Lists_Bonds == False:
            skip_header = 24 + natoms + 3+ natoms +3
        else:
            skip_header = 23+ natoms + 3+ natoms +3
        bonds_array = np.genfromtxt(f, skip_header=skip_header, max_rows=nbonds)



    nodes = {}
    for i in refs:
        nodes['{:}'.format(i-1)] = {}
        nodes['{:}'.format(i-1)]['net'] = []
    for i in range(bonds_array.shape[0]):
        bond_type, atom0, atom1 = int(bonds_array[i,1]), int(bonds_array[i,2]-1), int(bonds_array[i,3]-1)
        if (bond_type<3):
            nodes['{:}'.format(atom0)]['net'].append(atom1)
            nodes['{:}'.format(atom1)]['net'].append(atom0)
    
 

#for i in range(bonds_array.shape[0]):
#    atom0, atom1 = int(bonds_array[i,2]-1), int(bonds_array[i,3]-1)
#    nodes['{:}'.format(atom0)]['net'].append(atom1)
#    nodes['{:}'.format(atom1)]['net'].append(atom0)
 
    with open(FinalFolder+'/test_BN_net.dat', 'w') as f:
        for i in range(min(refs), max(refs)+1):
            node = int(i-1)
            for j in range(len(nodes['{:}'.format(node)]['net'])):
                f.write('{:<10}'.format(nodes['{:}'.format(node)]['net'][j]))
            f.write('\n')

    shutil.copy(FinalFolder+'/test_A_dual.dat', FinalFolder+'/test_BN_dual.dat')

    with open(FinalFolder+'/test_BN_aux.dat', 'w') as f:
        f.write('{:}\n'.format(natoms))
        f.write('{:<10}{:<10}\n'.format(3,3))
        f.write('2DE\n')
        f.write('{:<24.6f}{:<24.6f}\n'.format(dims[0], dims[1]))
        f.write('{:<24.6f}{:<24.6f}\n'.format(1/dims[0], 1/dims[1]))





################################################################
if os.path.isfile(FinalFolder+'/Si2O3_results.dat')==True:
    print('Write Si2O3 Positions')
    # Si2O3
    
    with open(FinalFolder+'/Si2O3_results.dat', 'r') as f:
        natoms = np.genfromtxt(f, skip_header=2, max_rows=1)
    natoms = int(natoms[0])
    
    with open(FinalFolder+'/Si2O3_results.dat', 'r') as f:
        nbonds = np.genfromtxt(f, skip_header=4, max_rows=1)
    nbonds = int(nbonds[0])
        
    with open(FinalFolder+'/Si2O3_results.dat', 'r') as f:
        dims = np.genfromtxt(f, skip_header=7, max_rows=3)
    dims = dims[:,1]


    with open(FinalFolder+'/Si2O3_results.dat', 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if 'Atoms' in line:
            start_line = i + 2  # Assuming that the atom coordinates start two lines after the 'Atoms' keyword
            break

    with open(FinalFolder+'/Si2O3_results.dat', 'r') as f:
        crds_array = np.genfromtxt(f, skip_header=start_line, max_rows=natoms)    
    
    refs = crds_array[:, 0]
    refs = [int(i) for i in refs]
    
    
    
    
    with open(FinalFolder+'/test_Si2O3_crds.dat', 'w') as f:
        for i in range(min(refs), max(refs)+1):
            ref = refs.index(i)
            f.write('{:<24}{:<24}{:<24}\n'.format(crds_array[int(ref), 3], crds_array[int(ref), 4], crds_array[int(ref), 5]))
    
    with open(FinalFolder+'/Si2O3_results.dat', 'r') as f:
        skip_header = start_line + natoms + 3+ natoms +3
        bonds_array = np.genfromtxt(f, skip_header=skip_header, max_rows=nbonds)
    
    nodes = {}
    for i in refs:
        nodes['{:}'.format(i-1)] = {}
        nodes['{:}'.format(i-1)]['net'] = []
    for i in range(bonds_array.shape[0]):
        bond_type, atom0, atom1 = int(bonds_array[i,1]), int(bonds_array[i,2]-1), int(bonds_array[i,3]-1)
        if (bond_type<3):
            nodes['{:}'.format(atom0)]['net'].append(atom1)
            nodes['{:}'.format(atom1)]['net'].append(atom0)
    
    with open(FinalFolder+'/test_Si2O3_net.dat', 'w') as f:
        for i in range(min(refs), max(refs)+1):
            node = int(i-1)
            for j in range(len(nodes['{:}'.format(node)]['net'])):
                f.write('{:<10}'.format(nodes['{:}'.format(node)]['net'][j]))
            f.write('\n')
    
    shutil.copy(FinalFolder+'/test_A_dual.dat', FinalFolder+'/test_Si2O3_dual.dat')
    
    with open(FinalFolder+'/test_Si2O3_aux.dat', 'w') as f:
        f.write('{:}\n'.format(natoms))
        f.write('{:<10}{:<10}\n'.format(6,3))
        f.write('2DE\n')
        f.write('{:<24.6f}{:<24.6f}\n'.format(dims[0], dims[1]))
        f.write('{:<24.6f}{:<24.6f}\n'.format(1/dims[0], 1/dims[1]))
















