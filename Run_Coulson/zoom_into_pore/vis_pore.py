import matplotlib.pyplot as plt
import numpy as np
import os 

########## Set system of interest #############

pore = 24
system = 1290
temp = 2000
seed = 38
steps = 10000

###############################################

base_dir ="../Results_TR"
input_dir = os.path.join(
    base_dir,
    f"Pore_{pore}_{system}",
    f"T_-{temp}",
    f"S_{seed}",
    str(steps)
)

if not os.path.isdir(input_dir):
    print(os.listdir(base_dir))

f = os.path.join(input_dir, 'Run/test_B_crds.dat')

data = np.genfromtxt(f)

x = data[:, 0]
y = data[:, 1]

plt.scatter(x, y, color='red')
f = os.path.join(input_dir, 'Run/test_Si_crds.dat')

data = np.genfromtxt(f)

x = data[:, 0]
y = data[:, 1]

plt.scatter(x, y)
plt.show()
