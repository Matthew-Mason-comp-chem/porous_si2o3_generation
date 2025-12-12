import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from node_me import NodeME
import sys

# Specify pore size range and system size range 
save_fig = False
base_dir = "../../Results_TR"

pore_min = 12
Pore_max = 36

Sys_min = 100
sys_max = 400

with open('node_dist.dat', 'r') as f:
    array = np.genfromtxt(f)
plt.plot(array[:,0], array[:,9], color='k')

#cmap = cm.tab20c
cmap = cm.viridis
print('Starting')
print(os.listdir("../../."))

ring_sizes = []
system_sizes = []
run_strings = []
for system_size_folder in os.listdir("../../"):
    if (os.path.isdir(os.path.join("../..", system_size_folder)) and system_size_folder != 'Results_TR' and system_size_folder != 'Submission_TR' and system_size_folder[:7]=='Results'): 
        ring_size = int(system_size_folder.split('_')[1])
        ring_sizes.append(ring_size)
        system_size = int(system_size_folder.split('_')[2])
        system_sizes.append(system_size)
        run_string = str(system_size_folder.split('_')[3])
        run_strings.append(run_string)

print('Avaliable Ring Sizes : ', ring_sizes)

from tqdm import tqdm

for i in tqdm(range(len(ring_sizes))):
    color = cmap(i/len(ring_sizes)) 
    for T in range(1000,5001, 100):
        for S in range(0, 20 , 1):
            folder = '../../Results_TR/Pore_{:}_{:}/T_-{:}/S_{:}/2500/Run'.format(ring_sizes[i], system_sizes[i], T, S)
            if os.path.isfile(folder+'/test_ringstats.out'):
                with open(folder+'/test_ringstats.out', 'r') as f:
                    array_pn = np.genfromtxt(f)
                with open(folder+'/test_correlations.out', 'r') as f:
                    array_corr = np.genfromtxt(f)
                var0 = sum([i**2*(array_pn[-1,i]) for i in range(array_pn.shape[1])])-36

                no4s =run_strings[i].count('4')
                no5s =run_strings[i].count('5')

                pn1 = np.copy(array_pn[-1,:])
                pn1[4] -= float(2*no4s/system_size)
                pn1[5] -= float(2*no5s/system_size)
                pn1[ring_sizes[i]] -= float(2/system_size)
                
                new_sum = sum(pn1)
                pn1 = [i/new_sum for i in pn1]
                var1 = sum([i**2*pn1[i] for i in range(array_pn.shape[1])])-36
                plt.scatter(array_pn[-1,4], var1, color=color, label='{:} {:} rings'.format(ring_sizes[i], system_sizes[i]), marker='*')

 #                   plt.scatter(array_pn[-1,6], var1, color=color, label='{:}_{:}'.format(system ,system_size), marker='x')
 #                   plt.scatter(array_pn[-1,6], sum([i**2*(array_pn[-1,i]) for i in range(12)])-36, color=color, label='{:}_{:}'.format(system ,system_size), marker='x')
# Get legend handles and labels
handles, labels = plt.gca().get_legend_handles_labels()

# Create a dictionary to store unique handles
unique_handles = {}
for handle, label in zip(handles, labels):
    unique_handles[label] = handle

# Remove the existing legend
plt.gca().legend().remove()

# Create a new legend with only unique handles
plt.legend(unique_handles.values(), unique_handles.keys())
plt.title('Lemaitre Curve for Pore systems')
plt.xlabel(r'$p_{}$'.format(6))
plt.ylabel(r'$\langle k^2\rangle - \langle k \rangle^2$')


plt.show()
