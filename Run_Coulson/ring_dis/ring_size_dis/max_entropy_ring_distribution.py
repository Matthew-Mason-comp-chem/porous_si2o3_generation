import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import glob
import re
import os
from tqdm import tqdm
import pandas as pd

### plotting max entropy ring distribution ##########
def plot_max_entropy(p6):
    # open node_dist.dat
    mdata = np.loadtxt("node_dist.dat", delimiter=None, skiprows=1)
    
    p6_vals = mdata[:, 2]
    
    closest_idx = np.argmin(np.abs(p6_vals - p6))
    print(closest_idx, p6)
    
    pn = mdata[closest_idx, 0:9]
    
    plt.plot(ring_sizes, pn, marker='', linestyle='-', linewidth=2, label=p6)

    
savefig = True
output = "ref_distributions.png"

# rcparmas config





ring_sizes = np.arange(4, 13)  # ring sizes 4–12
plt.figure(figsize=(6,4))

#p6 = [1, 0.8, 0.6, 0.4, 0.2, 0.1, 0.05, 0.01]
p6 = [1, 0.65, 0.2, 0.05]




for p in p6:
    plot_max_entropy(p)

plt.xlabel("Ring size (n)")
plt.ylabel("Pₙ (average)")
plt.title("Average Ring Size Distribution")
plt.grid(False)
plt.tight_layout()
plt.legend()

if savefig:
    plt.savefig(output)
plt.show()

