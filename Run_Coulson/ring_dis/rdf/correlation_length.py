import matplotlib.pyplot as plt
import matplotlib as mpl
import glob
import re
import os
from tqdm import tqdm
import pandas as pd
import numpy as np

savefig = True

# rcparmas config




# defining system
pore = 24
system = 1290
temps = [1000, 3000]

steps = 10000

base_dir = "../../Results_TR"

# seperates different temps
offset = [0, 2, 4, 6, 8]

for idx, T in enumerate(temps):
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

        data = np.loadtxt(os.path.join(base, tr_r))
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
    all_distances = np.array(all_dis)
    all_c = np.array(all_c)

    # Define bins
    bins = np.linspace(0, cut_off, 150)  # 50 bins (10 units wide)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])

    # Raw counts per bin
    counts, _ = np.histogram(all_distances, bins=bins)
    counts_w, _ = np.histogram(all_distances, bins=bins, weights=all_c)

    # Compute exact ring areas
    r1 = bins[:-1]
    r2 = bins[1:]
    ring_areas = np.pi * (r2**2 - r1**2)

    # Normalize counts by ring area
    g_r = counts / ring_areas
    g_r_q = counts_w / ring_areas


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

    plt.figure(2)
    plt.plot(bin_centers, g_r_q, marker='', label=T)
    plt.title('Normalized Distance Distribution (Exact Ring Area)')
    plt.xlabel('Distance (r)')
    plt.ylabel('Counts / Area of Ring')
    plt.grid(False)


    ######################### plot 3 ##############################
    g_r_abs = np.abs(g_r_q) 
    r = bin_centers
    logs = np.log(g_r_abs*r) #+ offset[idx]
    
    plt.figure(3)
    plt.plot(bin_centers, logs, marker='', label=T)
    plt.title('Normalized Distance Distribution (Exact Ring Area)')
    plt.xlabel('Distance (r)')
    plt.ylabel('Counts / Area of Ring')
    plt.grid(False)


#if savefig:
#    plt.savefig(f"Pore_{pore}_{system}_T_{temp}_qrdf.png")

plt.figure(2)
plt.legend()
plt.figure(3)
plt.legend()
plt.show()








