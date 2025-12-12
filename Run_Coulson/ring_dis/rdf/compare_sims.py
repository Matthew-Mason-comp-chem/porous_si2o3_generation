import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import glob
import re
import os
from tqdm import tqdm
import pandas as pd

ro = 2.86667626014*2 
constant = 50
offset = 6 

# rcparmas config




savefig = True

# defining system
pore = 30
system = 404
temp = 3000
steps = 2500


data = np.loadtxt(f"data/ring_growth/Gq_{pore}.dat")

pore = 30

print(data[:, 1])

plt.plot(data[:, 0], -1*(data[:, 1] - offset), label="Ring Growth")

plt.xlim(0, 50)

base_dir = "../../Results_TR"

input_dir = os.path.join(
    base_dir,
    f"Pore_{pore}_{system}",
    f"T_-{temp}",
)

if not os.path.isdir(input_dir):
    print(os.listdir(base_dir))

pattern = os.path.join(input_dir, f"*/{steps}")

files = glob.glob(pattern)
norm = len(files)


seeds = [int(re.search(r'S_(\d+)', p).group(1)) for p in files]

print(files)

# Average over seeds

base = f"{base_dir}/Pore_{pore}_{system}"


all_dis = []
all_c = []

cut_off = 350

for i in tqdm(range(len(seeds)-0)):
    seed = seeds[i]

    # load TR_R
    tr_r = f"TR_r/results_{temp}_{seed}_r.dat"
    if not os.path.exists(os.path.join(base, tr_r)):
        continue

    #print("reading file")

    fil = os.path.join(base, tr_r)
    #data = pd.read_csv(fil, delim_whitespace=True, header=None, engine='c', dtype=float)
    data = np.loadtxt(fil)

    #print("done")
    #dis = np.array(data.iloc[0])
    #rings = np.array(data.iloc[1])
    dis = data[0]
    rings = data[1]

    charges = rings - 6

    mask = dis < cut_off
    dis = dis[mask]
    charges = charges[mask]
    # load TR_rings


    # load TR_SHELLS


    all_dis.extend(dis)
    all_c.extend(charges)

#################### plot 1 ###################################

# Convert to numpy array
all_distances = np.array(all_dis)/ ro
all_c = np.array(all_c)

# Define bins
bins = np.linspace(0, cut_off/ro, 300)  # 50 bins (10 units wide)
bin_centers = 0.5 * (bins[:-1] + bins[1:])

# Raw counts per bin
counts, _ = np.histogram(all_distances, bins=bins)
counts_w, _ = np.histogram(all_distances, bins=bins, weights=all_c)

# Compute exact ring areas
r1 = bins[:-1]
r2 = bins[1:]
ring_areas = np.pi * (r2**2 - r1**2)

# Normalize counts by ring area
g_r = counts / (ring_areas*norm)
g_r_q = counts_w / (ring_areas*norm)


######################### plot 2 #############################


plt.plot(bin_centers, g_r_q, marker='', label="Pore Evaporation")
plt.title(f"Pore {pore}")
plt.xlabel('Distance (r/ro)')
plt.ylabel('g_r_q')

plt.grid(False)

plt.legend()

if savefig:
    plt.savefig(f"Pore_{pore}_contrast.png")

plt.show()
            
