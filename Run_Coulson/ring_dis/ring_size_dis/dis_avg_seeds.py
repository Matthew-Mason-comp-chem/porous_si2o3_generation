import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import glob
import re
import os
from tqdm import tqdm
import pandas as pd

### plotting max entropy ring distribution ##########
plotmaxentro = True

def plot_max_entropy(p6):
    # open node_dist.dat
    mdata = np.loadtxt("node_dist.dat", delimiter=None, skiprows=1)
    
    p6_vals = mdata[:, 2]
    
    closest_idx = np.argmin(np.abs(p6_vals - p6))
    print(closest_idx, p6)
    
    pn = mdata[closest_idx, 0:9]
    
    plt.plot(ring_sizes, pn, marker='', linestyle='-', linewidth=2, label='max entropy')

    
savefig = True

# rcparmas config





# defining system
pore = 24
system = 1290
temp = 5000
steps = 10000

base_dir = "../../Results_TR"

input_dir = os.path.join(
    base_dir,
    f"Pore_{pore}_{system}",
    f"T_-{temp}",
)

if not os.path.isdir(input_dir):
    print(os.listdir(base_dir))

pattern = os.path.join(input_dir, f"*/{steps}/Run")

files = glob.glob(pattern)
print(files)

pn_list = []

for i in tqdm(range(len(files))):
    # load test_ringstats.out
    fil = os.path.join(files[i], "test_ringstats.out")
    if os.path.exists(fil):
        with open(fil, "r") as f:
                array_pn = np.loadtxt(f)
                final_pn = array_pn[-1, 4:13]

    #print(final_pn)
    pn_list.append(final_pn)


if pn_list:
    avg_pn = np.mean(pn_list, axis=0)
    ring_sizes = np.arange(4, 13)  # ring sizes 4–12
    
    plt.figure(figsize=(6,4))

    if plotmaxentro:
        p6 = avg_pn[2]
        plot_max_entropy(p6)

    plt.plot(ring_sizes, avg_pn, marker='o', linestyle='-', linewidth=2, label='data')
    plt.xlabel("Ring size (n)")
    plt.ylabel("Pₙ (average)")
    plt.title("Average Ring Size Distribution")
    plt.grid(False)
    plt.tight_layout()
    output = f"ring_dis_{pore}_{system}_{temp}"
    plt.legend()

    if savefig:
        plt.savefig(output)
    plt.show()

