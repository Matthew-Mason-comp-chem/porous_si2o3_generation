import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import glob
import re
import os
from tqdm import tqdm
import pandas as pd

savefig = True
ro  = 2.86667626014*2 

# rcparmas config




# defining system
pore = 30
system = 404
temps = [1000, 3000, 5000]
steps = 2500

base_dir = "../../Results_TR"

sep = [0, 1, 2, 3]
gg = -1

for T in temps:
    gg = gg + 1
    print(gg) 
    print(sep[gg])
    se = sep[gg]

    temp = T

    input_dir = os.path.join(
        base_dir,
        f"Pore_{pore}_{system}",
        f"T_-{temp}",
    )

    if not os.path.isdir(input_dir):
        print(os.listdir(base_dir))

    pattern = os.path.join(input_dir, f"*/{steps}")

    files = glob.glob(pattern)
    
    seeds = [int(re.search(r'S_(\d+)', p).group(1)) for p in files]

    print(files)
    
    norm = len(files)

    # Average over seeds

    base = f"{base_dir}/Pore_{pore}_{system}"


    all_dis = []
    all_c = []

    cut_off = 250

    for i in tqdm(range(len(seeds)-0)):  
        seed = seeds[i]

        # load TR_R
        tr_r = f"TR_r/results_{temp}_{seed}_r.dat"
        if not os.path.exists(os.path.join(base, tr_r)):
            continue
        
        fil = os.path.join(base, tr_r)
        data = np.loadtxt(fil)

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
    bins = np.linspace(0, cut_off/ro, 150)  # 50 bins (10 units wide)
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


    #plt.plot(bin_centers, g_r, marker='')
    #plt.title('Normalized Distance Distribution (Exact Ring Area)')
    #plt.xlabel('Distance (r)')
    #plt.ylabel('Counts / Area of Ring')
    #plt.grid(False)

    #if savefig:
    #    plt.savefig(f"Pore_{pore}_{system}_T_{temp}_rdf.png")
    #
    #plt.show()

    ######################### plot 2 #############################

    
    plt.plot(bin_centers, g_r_q + se, marker='', label=T)
    plt.title('Ring charge radial distribution functions')
    plt.xlabel('Distance (r)')
    plt.ylabel('G(r)q')
    plt.grid(False)

plt.legend()


if savefig:
    plt.savefig(f"Pore_{pore}_{system}_var_T_qrdf.png")

plt.show()
