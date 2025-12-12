import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import pandas as pd
import re
from matplotlib import cm, colors

base_dir = '../../Results_TR'

########### filters ################
pore_min = 24       # e.g. 10
pore_max = 24       # e.g. 20

system_min = 1100     # e.g. 300
system_max = 2200     # e.g. 800

temp_min =  3000      # e.g. 300
temp_max = 3001      # e.g. 700

seed_min = 0       # e.g. 0
seed_max = 50       # e.g. 1000
####################################

# Defining markers for different system limits
def marker(system_size):
    if system_size < 400:
        return '*'
    if 400 <= system_size <= 600:
        return 'x'
    return 'o'

def calculate_mean(shells_list_pore):
    mean_k_t = []
    for i in range(0, len(shells_list_pore)):
        data = np.array(shells_list_pore[i])
        #print('np array', data)
        mean_k = np.mean(data)
        #print('mean k', mean_k)
        mean_k_t.append(mean_k)
    return mean_k_t

def in_range(val, vmin, vmax):
    if vmin is not None and val < vmin:
        return False
    if vmax is not None and val > vmax:
        return False
    return True


# defining file pattern

file_glob_pattern = 'results_*_*_*'

# Parse directory names and extract pore size and system size
pore_dir_re = re.compile(r"Pore_(\d+)_([0-9]+)")

# Parse filename and extract temp or seed
file_re = re.compile(r"results_(?P<temp>[-+]?\d+(\.\d+)?)_(?P<seed>\d+)_shell\.dat")

# Find all sub dirs and filter
all_pore_dirs = []
for entry in os.listdir(base_dir):
    m = pore_dir_re.match(entry)
    if m:
        pore_val = int(m.group(1))
        sys_val = int(m.group(2))
        if not in_range(pore_val, pore_min, pore_max):
            continue
        if not in_range(sys_val, system_min, system_max):
            continue
        all_pore_dirs.append((entry, pore_val, sys_val))

if not all_pore_dirs:
    raise SystemExit(f"No pore directories found in {base_dir} matching filters.")
print("""

""")
print("Systems being ploted", all_pore_dirs)
print("""

""")

# Determine color mapping for pore sizes (continuous)
pore_sizes = sorted({p for (_, p, _) in all_pore_dirs})
vmin = min(pore_sizes)
vmax = max(pore_sizes)
norm = colors.Normalize(vmin=vmin, vmax=vmax)
cmap = cm.get_cmap('viridis')  # change cmap if you like

plt.figure(figsize=(9,6))

mean_values_by_shell = {}

seen_pores = set()

for dirname, pore_val, sys_val in all_pore_dirs:

    TR_shells_dir = os.path.join(base_dir, dirname, 'TR_SHELLS')
    if not os.path.isdir(TR_shells_dir):
        print(f"Warning no: {TR_shells_dir}")
        continue
    pattern = os.path.join(TR_shells_dir, file_glob_pattern)
    files = glob.glob(pattern)

    if not files:
        print(f"No files matching {pattern} in {TR_shells_dir}")
        continue
    
    for fil in sorted(files):
         # temp fix
        if pore_val in seen_pores:
            print("skipping")
            continue
        seen_pores.add(pore_val)
        
        fname = os.path.basename(fil)
        m = file_re.match(fname)
        if not m:
            print(f"Skipping file with unexpected name: {fname}")
            continue

        temp = float(m.group('temp'))
        seed = int(m.group('seed'))

        # apply temp & seed filters
        if not in_range(temp, temp_min, temp_max):
            continue
        if not in_range(seed, seed_min, seed_max):
            continue

        with open(fil, 'r') as file:
            lines = file.readlines()
            shells_list_pore = [list(map(int, line.split())) for line in lines]
        mean_k_t = calculate_mean(shells_list_pore)
        
        # Plot mean ring size vs shell number for this pore
        plt.plot(range(1, len(mean_k_t) + 1), mean_k_t,
                 label=f'Pore {pore_val}, Sys {sys_val}',
                 color=cmap(norm(pore_val)),
                 marker=marker(sys_val))

        # Store mean values for each shell
        for shell_index, mean_value in enumerate(mean_k_t):
            if shell_index + 1 not in mean_values_by_shell:
                mean_values_by_shell[shell_index + 1] = []
            mean_values_by_shell[shell_index + 1].append((pore_val, mean_value))

plt.xlabel('Shell Number')
plt.ylabel('Mean Ring Size')
plt.title('Mean Ring Size vs Shell Number')
plt.legend()
plt.show()

# --- Second plot: Mean ring size for each shell vs Pore size ---
plt.figure(figsize=(9,6))

for shell_number, values in mean_values_by_shell.items():
    if shell_number > 7:
        continue

    values.sort(key=lambda x: x[0])  # Sort by pore size
    pore_sizes, mean_ring_sizes = zip(*values)

    plt.plot(pore_sizes, mean_ring_sizes, label=f'Shell {shell_number}', marker='o')


plt.xlabel('Pore Size')
plt.ylabel('Mean Ring Size')
plt.title('Mean Ring Size for Each Shell vs Pore Size')
plt.legend(title='Shells', loc='upper right', bbox_to_anchor=(1, 1))
plt.show()

