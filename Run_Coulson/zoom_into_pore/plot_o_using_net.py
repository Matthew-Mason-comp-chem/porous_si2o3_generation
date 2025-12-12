import numpy as np
import os
import matplotlib.pyplot as plt
import sys
from collections import Counter

r0 = 2.86667626014*2


# def system
system = "TR"
pore = 24
cell_size = 228
T = 1000
S = 11
steps = 2500

# extract relevant files
path = '../Results_{:}/Pore_24_{:}/T_-{:}/S_{:}/2500/Run/'.format(system, cell_size, T,S)
if not os.path.isfile('../Results_{:}/Pore_24_{:}/TR_rings/results_{:}_{:}_rings.dat'.format(system, cell_size, T,S)):
    print("skipping")
    sys.exit(1)

print(path)
with open(path+'test_B_dual.dat', 'r') as f:
   B_net = np.genfromtxt(f, max_rows=1, dtype=int)
with open(path+'test_Si2O3_net.dat', 'r') as f:
   A_net = np.genfromtxt(f, max_rows=cell_size, dtype=int)
with open(path+'test_Si2O3_crds.dat', 'r') as f:
   A_crds = np.genfromtxt(f, dtype=float)
with open('../Results_{:}/Pore_24_{:}/TR_rings/results_{:}_{:}_rings.dat'.format(system, cell_size, T,S), 'r') as f:
    array = np.genfromtxt(f, dtype=float)


# find o atoms around pore
roundring_si_distance = []
si_crds = []
o_atoms = []
for si in B_net:
    cnxs = A_net[int(si),:]
    for o in cnxs:
#            if int(o) not in o_atoms: o_atoms.append(int(o))
        o_atoms.append(int(o))
    si_crds.append(A_crds[si,:2])

for i in range(len(si_crds)):
    roundring_si_distance.append(np.linalg.norm(np.subtract(si_crds[i-1], si_crds[i]))/r0)
print(np.mean(roundring_si_distance), ' +- ', np.std(roundring_si_distance))
print(roundring_si_distance)
count = Counter(o_atoms)
o_atoms = [item for item, freq in count.items() if freq > 1]

crds = []
for o in o_atoms:
    crds.append(A_crds[o,:2])
points = np.asarray(crds)
#    print(points)

node_radius = 2.63/(2*0.529177)

# plot 
print("here                 ",crds)

for arr in crds:
    plt.scatter(arr[0], arr[1], color="blue", label="oxygen")

plt.legend()
plt.show()
fig, ax = plt.subplots()

for arr in crds:
    ax.scatter(arr[0], arr[1], color="black")



# Plot O atoms (red)
for o in range(int(2*A_crds.shape[0]/5), A_crds.shape[0]):
    ax.scatter(A_crds[o, 0], A_crds[o,1], color="red")

# Plot Si atoms (blue)
for si in range(int(2*A_crds.shape[0]/5)):
    ax.scatter(A_crds[si, 0], A_crds[si,1], color="blue")

# Add *one* legend entry per atom type
# Collect unique handles and labels
handles = [
    plt.Line2D([], [], color='red', marker='o', linestyle='None', label='O'),
    plt.Line2D([], [], color='blue', marker='o', linestyle='None', label='Si')
]

for arr in crds:
    ax.scatter(arr[0], arr[1], color="black")


ax.legend(handles=handles)

ax.set_aspect('equal')
ax.axis('off')
plt.show()

