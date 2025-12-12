import numpy as np
import pandas as pd
import os
import glob
import re
import json

base_dir = "../../../Results_TR"

# systems of interest
#pore_sizes = [15, 20, 24, 30, 15, 20, 24, 30]
#system_sizes = [494, 478, 440, 404, 1336, 1310, 1290, 1232]

# find all sub dirs
from tqdm import tqdm

system_sizes = [1290, 0]
pore_sizes = [24, 0]

for i in tqdm(range(len(system_sizes))):
    pore_s = pore_sizes[i]
    sys_s = system_sizes[i]
    
    d = f"Pore_{pore_s}_{sys_s}"
    e = os.path.join(base_dir, d)
    if os.path.exists(e):
        dirs = glob.glob(os.path.join(e, 'T_-*/S_*/*'))
            
        assors = []
        final_pn_dis = []
        seeds = []
        temps =[]

        #need to collect seed, temp, pn dis, assor
        for di in dirs:
            # obtaining temp/seed
            if not os.path.exists(os.path.join(di, 'Run', "test_ringstats.out")):
                print("simulation failed skipping", os.path.join(di, 'Run', "test_ringstats.out"))
                continue

            match = re.search(r'T_-([^/]+)/S_([^/]+)/', di)
            if match:
                seeds.append(match.group(2))
                temps.append(int(match.group(1)))

            with open(os.path.join(di, 'Run', "test_ringstats.out"), "r") as f:
                array_pn = np.genfromtxt(f)
                final_pn = array_pn[-1, 4:25]
            with open(os.path.join(di, "Run", "test_correlations.out"), "r") as f:
                ass = np.genfromtxt(f, usecols=0)
                ass0 = ass[-1]
            
            assors.append(ass0)
            final_pn_dis.append(final_pn)

    else:
        print(e, "doesnt exist")

    # build and save dataframe for each system
    print(temps[:4])
    
    # processinf ring dis into more useful format
    ring_offset = 4

    pn_arrays = [np.asarray(x, dtype=float) for x in final_pn_dis]
    max_len = max(arr.size for arr in pn_arrays) if pn_arrays else 0
    
    pn_matrix = np.full((len(pn_arrays), max_len), np.nan, dtype=float)
    for i, arr in enumerate(pn_arrays):
        pn_matrix[i, : arr.size] = arr
    
    pn_cols = {}
    for j in range(max_len):
        col_name = f"mem_ring_{j + ring_offset}"
        pn_cols[col_name] = pn_matrix[:, j]
    
    df = pd.DataFrame({
        'temp': temps,
        'seeds': seeds,
        'assors': assors,
    })
    
    df = pd.concat([df, pd.DataFrame(pn_cols)], axis=1)

    df.to_csv(f'Pore_{pore_s}_{sys_s}_pn_assor.csv', index=False)


