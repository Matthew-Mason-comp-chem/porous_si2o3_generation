import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import re


base_dir = '../../Results_TR'

# Plotting the ring distribution per shell

pore_s = 15
temp = 4000
sys_s = 1336
    
pore_dir = f"Pore_{pore_s}_{sys_s}"

TR_shells_dir = os.path.join(base_dir, pore_dir, 'TR_SHELLS')
if not os.path.isdir(TR_shells_dir):
    print(f"Warning: {TR_shells_dir} does not exist, skipping.")
    print(os.listdir(base_dir))

pattern = os.path.join(TR_shells_dir, f'results*{temp}*')
files = glob.glob(pattern)
print(pattern)
print(f"files: {files}")
print("number of files", len(files))

if not files:
    print(os.listdir(TR_shells_dir))

# Averaged over random seed
# parameters
low, high = 4, 12
values = np.arange(low, high + 1)
num_shells_to_plot = 10  # si = 0..5

# container to collect fractions for each shell index across files (seeds)
seed_fractions = {si: [] for si in range(num_shells_to_plot)}

for idx, fil in enumerate(files):
    with open(fil, 'r') as file:
        lines = file.readlines()
        shells_list_pore = [list(map(int, line.split())) for line in lines]

    for si in range(0, len(shells_list_pore)):
        if si >= num_shells_to_plot:
            continue

        data = np.array(shells_list_pore[si])
        filtered = data[(data >= low) & (data <= high)]

        if len(filtered) != len(data):
            # this seed/file: shell has reached a pore -> skip this shell in this seed
            # keep behavior consistent with your original code (you printed and skipped)
            print(f'file {fil}: shell {si} has reached a pore, skipping this seed for this shell')
            continue

        total = len(filtered)
        fractions = []
        for i in values:
            frac = np.sum(filtered == i) / total if total > 0 else 0
            fractions.append(frac)

        # collect this seed's fractions for this shell index
        seed_fractions[si].append(np.array(fractions))

# after collecting all seeds, compute mean and std and plot
plt.figure()
for si in range(num_shells_to_plot):
    if len(seed_fractions[si]) == 0:
        print(f'No valid seeds for shell {si}, skipping plot for this shell')
        continue

    stack = np.vstack(seed_fractions[si])  # shape: (n_seeds, n_values)
    mean_frac = np.mean(stack, axis=0)
    std_frac = np.std(stack, axis=0, ddof=0)  # population std; change ddof=1 if you prefer sample std

    plt.errorbar(values, mean_frac, yerr=std_frac, label=f'shell {si}', marker='o', capsize=3)

plt.xlabel('ring size')
plt.ylabel('fraction')
plt.legend()
output = f"ring_dis_per_shell_{pore_s}_{sys_s}_{temp}"
plt.savefig(output)
plt.show()
