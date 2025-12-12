import numpy as np
import matplotlib.pyplot as plt
import glob
import re
import os


pore_s = 30
temp = 5000
sys_s = 1232

print('collecting files')
ham_f = glob.glob(f"data/Pore_{pore_s}*{sys_s}*{temp}*2500*test*")

if not ham_f:
    print("glob didnt find any files")

# process harmonic data
for fil in ham_f[:]:
    with open(fil, 'r') as f:
        data = np.genfromtxt(f)
        harmonic_e = data[-1, 3]
    info = re.findall(r"-?\d+", fil)
    pore_s = info[0]
    sys_s = info [1] 
    temp = info[3]
    seed = info[2]
    step = info[4]
    # check if Run files exist for this simulation - sometimes the sim fails
    folder_name = f'../Results_TR/Pore_{pore_s}_{sys_s}/T_{temp}/S_{seed}/{step}/Run' 
    
    if os.path.exists(folder_name):
        with open(folder_name + '/test_ringstats.out', 'r') as f:  
            array_pn = np.genfromtxt(f)
            var0 = sum([i**2 * (array_pn[-1, i]) for i in range(array_pn.shape[1])]) - 36
    else:
        print(f'cant find ringstats: {folder_name}')

     
    # how does harmonic energy change over time of the simulation
    print(len(data[:, 3]))
    d = np.array(data[:, 3])
    d = d/int(sys_s)
    plt.scatter(range(len(data[:, 3])), d) 
    print(f'showing plot for: {folder_name}')
    plt.xlabel("steps")
    plt.ylabel("harmonic energy")
    plt.savefig(f'anneling_process_{pore_s}_{sys_s}_{temp}')
    plt.show()
    # are the systems with large harmonic energy just not quenching? they seem to be reaching a minium
