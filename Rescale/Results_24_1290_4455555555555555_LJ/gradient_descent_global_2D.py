import subprocess
import numpy as np
import time
import sys

import re, yaml
try:
    from yaml import CSafeLoader as Loader
except ImportError:
    from yaml import SafeLoader as Loader


if len(sys.argv)>2:
    file_string = sys.argv[1]
    start_array_x = float(sys.argv[2])
    start_array_y = float(sys.argv[3])
    start_array_z = float(sys.argv[4])
    time_step = float(sys.argv[5])
else:
    file_string = 'Si'
    start_array_x, start_array_y, start_array_z = 1,1,1
    time_step = 0.001

def produce_engtot(string):

    docs = ""
    with open("{:}_log.lammps".format(string)) as f:
        for line in f:
            m = re.search(r"^(keywords:.*$|data:$|---$|\.\.\.$|  - \[.*\]$)", line)
            if m: docs += m.group(0) + '\n'

    thermo = list(yaml.load_all(docs, Loader=Loader))

    print("Number of runs: ", len(thermo))

    for i in range(len(thermo)):
        if i==0:
            data = np.asarray(thermo[0]['data'])
        else:
            data = np.vstack((data, np.asarray(thermo[i]['data'])))

    engtot_array = data

    with open('{:}_energies.out'.format(string), 'w') as f:
        f.write('   Step                   PotEng                   KinEng                   E_pair                   E_bond                   TotEng                   Volume              Temp\n')

        for i in range(engtot_array.shape[0]):
            for j in range(engtot_array.shape[1]):
                if j==0:
                    f.write('{:<25}'.format(int(engtot_array[i,j])))
                else:
                    f.write('{:<25}'.format(engtot_array[i,j]))
            f.write('\n')

    with open('{:}_engtot.out'.format(string), 'w') as f:

        for i in range(engtot_array.shape[0]):
            f.write('    {:<25}{:<25}{:<25}\n'.format(int(engtot_array[i,0]), 0.000, engtot_array[i,1]))
    return engtot_array[-1,1]


# Define the scale factors to loop over

with open(file_string+".in", "r") as file:
    template_script = file.read()

step = 0
#time_step = 0.0001
#time_step = 0.000000000000001
#com = np.array([0.91,0.91,1.00])
#com = np.array([0.9439176,  0.94391753, 1.2        ])
#com = np.array([0.94237663, 0.94232184, 1.        ])
#com = np.array([1.22432821, 1.22432821, 1.22432821])
#com = np.array([0.8313231325494934, 0.945383663790235, 1.0567576001793595])
com = np.array([float(start_array_x),float(start_array_y),float(start_array_z)])
#com = np.array([0.94375523, 0.94375296, 0.93844054])
#Eo = 10.804396
#Eo = 105

modified_script = template_script.replace("${xscale}", str(com[0]))
modified_script = modified_script.replace("${yscale}", str(com[1]))
modified_script = modified_script.replace("${zscale}", str(com[2]))

with open(file_string+"_temp.in", "w") as temp_file:
    temp_file.write(modified_script)

subprocess.run(["/u/mw/shug7609/lammps-2025/build/lmp", "-in", file_string+"_temp.in", "-l", file_string+"_temp_log.lammps", "-screen", "debug.txt"])

Eo = produce_engtot(file_string+"_temp")

#Eo = 7.53085865098987
dE = 0.1*Eo
grad = 0.01/(time_step)
x_list, y_list, z_list, e_list = [],[],[],[]


import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
def visualise_search():
    x_list, y_list, z_list, e_list = [],[],[],[]
    step_size =0.1
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlabel('X Scale')
    ax.set_ylabel('Y Scale')
    ax.set_zlabel('Z Scale')

    phi = np.arange(0,np.pi,np.pi/10)
#    phi = np.array([np.pi/2])
    theta = np.arange(0,2*np.pi,np.pi/10)
    rho = np.array([step_size])
    com = np.array([0,0,0])   
    for phi_scale in phi:
        for theta_scale in theta:
            for rho_scale in rho:
                print(phi_scale, theta_scale, rho_scale)
                xscale = com[0]+rho_scale*np.sin(phi_scale)*np.cos(theta_scale)
                yscale = com[1]+rho_scale*np.sin(phi_scale)*np.sin(theta_scale)
                zscale = com[2]+rho_scale*np.cos(phi_scale)
                print(xscale, yscale, zscale)
                x_list.append(xscale)
                y_list.append(yscale)
                z_list.append(zscale)
    img = ax.scatter(x_list, y_list, z_list, s=100)
    fig.colorbar(img, ax=ax, label='Energy')
    plt.show()
#visualise_search()
x_list, y_list, z_list, e_list = [],[],[],[]
while step<1000 and dE>0:
    print(grad)
    print(time_step*grad)
#    print(time_step*time_step*grad)

    step_size = min([time_step*grad, 0.01])
    print('------------------------------------------------------------------------------------ Step ', step, '  Energy ', Eo, '  dE ', dE, ' step : ', step_size)

    # Spherical
#    phi = np.arange(0,np.pi,np.pi/10)
    #phi = np.array([np.pi/2])
#    theta = np.arange(0,2*np.pi,np.pi/10)
    rho = np.array([0.5*step_size, step_size])

    N = 100
    # Golden angle in radians
    golden_angle = np.pi * (3 - np.sqrt(5))

    # # Initialize arrays for theta and phi
    # theta = golden_angle * np.arange(N)
    # z = np.linspace(1 - 1.0 / N, 1.0 / N - 1, N)
    # radius = np.sqrt(1 - z * z)

    for rho_scale in rho:
        for i in range(N):
            print(i)
            theta = i*(2*np.pi/N)
            x = np.cos(theta)  # x coordinate
            y = np.sin(theta)  # y coordinate

            xscale = com[0] + rho_scale*x
            yscale = com[1] + rho_scale*y
            zscale = com[2]

        # for theta_scale in theta:
        #
        #     xscale = com[0] + rho_
        #
        #     for rho_scale in rho:
        #         xscale = com[0]+rho_scale*np.sin(phi_scale)*np.cos(theta_scale)
        #         yscale = com[1]+rho_scale*np.sin(phi_scale)*np.sin(theta_scale)
        #         zscale = com[2]+rho_scale*np.cos(phi_scale)
        #         print('*************', com[0], rho_scale*np.sin(phi_scale)*np.cos(theta_scale), '(',rho_scale, np.sin(phi_scale), np.cos(theta_scale), ')', com[0]+rho_scale*np.sin(phi_scale)*np.cos(theta_scale))
        #         print('*************', com[1], rho_scale*np.sin(phi_scale)*np.sin(theta_scale), '(',rho_scale, np.sin(phi_scale), np.sin(theta_scale), ')', com[1]+rho_scale*np.sin(phi_scale)*np.sin(theta_scale))
        #         print('*************', com[2], rho_scale*np.cos(phi_scale), '(',rho_scale, np.cos(phi_scale), ')', com[2]+rho_scale*np.cos(phi_scale))

#    x_scale_factors = np.arange(com[0]-5*step_size, com[0]+5*step_size, step_size)  # 0.9 to 1.1 inclusive, with a step of 0.1
#    y_scale_factors = np.arange(com[1]-5*step_size, com[1]+5*step_size, step_size)  # 0.9 to 1.1 inclusive, with a step of 0.1
#    z_scale_factors = np.arange(com[2]-5*step_size, com[2]+5*step_size, step_size)  # 0.9 to 1.1 inclusive, with a step of 0.1
#    print(x_scale_factors, y_scale_factors, z_scale_factors)
#    x_list, y_list, z_list, e_list = [],[],[],[]

# Loop over all combinations of scale factors
#    for xscale in x_scale_factors:
#        for yscale in y_scale_factors:
#            for zscale in z_scale_factors:
                # Replace the placeholders with the current scale factors
            modified_script = template_script.replace("${xscale}", str(xscale))
            modified_script = modified_script.replace("${yscale}", str(yscale))
            modified_script = modified_script.replace("${zscale}", str(zscale))

        # Write the modified script to a temporary file
            with open(file_string+"_temp.in", "w") as temp_file:
                temp_file.write(modified_script)

        # Run the LAMMPS simulation
        # Replace 'lmp_executable' with your LAMMPS command, e.g., 'lmp', 'mpirun -np 4 lmp', etc.
            subprocess.run(["/u/mw/shug7609/lammps-2025/build/lmp", "-in", file_string+"_temp.in", "-l", file_string+"_temp_log.lammps", "-screen", "debug.txt"])

            e_val = produce_engtot(file_string+"_temp")

            #print(phi_scale, theta_scale, rho_scale)
            print(xscale, yscale, zscale, e_val, '/', Eo)

            x_list.append(xscale)
            y_list.append(yscale)
            z_list.append(zscale)
            e_list.append(e_val)


    print('########################################')
    old_com = com
    com = np.array([x_list[e_list.index(min(e_list))], y_list[e_list.index(min(e_list))], z_list[e_list.index(min(e_list))]])
    print('\n\nCOM ', old_com, ' -> ', com, '\n\n')

    dr = np.linalg.norm(np.subtract(old_com, com))
    Ef = e_list[e_list.index(min(e_list))]
    dE = Eo-Ef

    print('dr = ', dr, ' dE = ', dE)

    grad = dE/dr

    if dE>1: dE = 0.1
#    if dE==0: 
#        time_step /= 2
#        dE = 0.1
    Eo = Ef
    step +=1 
print('----------------------------------------------------------------------------------------- Final Step ', step, '  Energy ', Eo, '  dE ', dE, com)
print(com)
            # Here you might want to add code to parse the output of the simulation
            # and extract the energy or any other required data, then log it with the scaling factors.

# Make sure to clean up temporary files if necessary

with open('e_vs_xyz_grad_desc_{:}.dat'.format(file_string), 'a+') as f:
    for i in range(len(x_list)):
        f.write('{:<10f} {:<10f} {:<10f} {:<26f}\n'.format(x_list[i], y_list[i], z_list[i], e_list[i]))

e_min = min(e_list)
e_min_ref = e_list.index(e_min)
print(x_list[e_min_ref], y_list[e_min_ref], z_list[e_min_ref])
with open('rescale.dat', 'w') as f:
    f.write('{:<10} {:<10}'.format(x_list[e_min_ref], y_list[e_min_ref]))

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

img = ax.scatter(x_list, y_list, e_list, c=e_list, cmap=plt.hot(), s=100)
fig.colorbar(img, ax=ax, label='Energy')
ax.set_xlabel('X Scale')
ax.set_ylabel('Y Scale')
ax.set_zlabel('Z Scale')

plt.show()



