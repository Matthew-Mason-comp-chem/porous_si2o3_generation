import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import re
from matplotlib import cm, colors

# -------------------------------
# User-editable parameters
# -------------------------------
base_dir = '../../Results_TR'

# Filtering limits (set to None to disable that filter)
pore_min = 24       # e.g. 10
pore_max = 25       # e.g. 20

system_min = 1000     # e.g. 300
system_max = 1400     # e.g. 800

temp_min =  3000      # e.g. 300
temp_max = 3001      # e.g. 700

seed_min = 0       # e.g. 0
seed_max = 50       # e.g. 1000

output = f"meankvst_{system_min}_{system_max}_{temp_min}_{temp_max}"

# Marker mapping by system size group
def system_marker(system_size):
    if system_size < 400:
        return '*'
    if 400 <= system_size <= 600:
        return 'x'
    return 'o'



# defining pattern

file_glob_pattern = "results_*_*_*"

# Parse directory name like 'Pore_14_502' to (pore_size:int, system_size:int)
pore_dir_re = re.compile(r'Pore_(\d+)_([0-9]+)')

# Parse result filename like 'results_300_1_0_shell.dat' to (temp:int, seed:int)
file_re = re.compile(r'results_(?P<temp>[-+]?\d+(\.\d+)?)_(?P<seed>\d+)_shell\.dat')

# Helper: check if value within min/max (None means no bound)
def in_range(val, vmin, vmax):
    if vmin is not None and val < vmin:
        return False
    if vmax is not None and val > vmax:
        return False
    return True

# Find all pore directories under base_dir
all_pore_dirs = []
for entry in os.listdir(base_dir):
    m = pore_dir_re.match(entry)
    if m:
        pore_val = int(m.group(1))
        sys_val = int(m.group(2))
        # apply pore & system filters (if set)
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

legend_entries = []

# Iterate over matching directories and plot matching files
for dirname, pore_val, sys_val in all_pore_dirs:
    TR_shells_dir = os.path.join(base_dir, dirname, 'TR_SHELLS')
    if not os.path.isdir(TR_shells_dir):
        print(f"Warning: {TR_shells_dir} does not exist, skipping.")
        continue

    # Find result files under TR_SHELLS
    pattern = os.path.join(TR_shells_dir, file_glob_pattern)
    T_files = glob.glob(pattern)
    if not T_files:
        print(f"No files matching {pattern} in {TR_shells_dir}")
        continue

    for T_dir in sorted(T_files):
        fname = os.path.basename(T_dir)
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

        # Read file: each line -> list of ints/floats
        with open(T_dir, 'r') as file:
            lines = [ln.strip() for ln in file.readlines() if ln.strip()]
        if not lines:
            print(f"Empty or whitespace-only file: {T_dir}")
            continue

        # convert each line to list of numbers
        shells_list_pore = []
        for line in lines:
            # tolerate ints or floats separated by whitespace
            parts = line.split()
            try:
                nums = [float(x) for x in parts]
            except ValueError:
                # try to filter out any non-numeric tokens
                nums = []
                for tok in parts:
                    try:
                        nums.append(float(tok))
                    except ValueError:
                        pass
            if nums:
                shells_list_pore.append(nums)

        if not shells_list_pore:
            print(f"No numeric data found in {T_dir}, skipping.")
            continue

        # Calculate mean per shell (list index -> shell number)
        def calculate_mean(shells):
            mean_k_t = []
            for arr in shells:
                a = np.array(arr, dtype=float)
                mean_k_t.append(np.mean(a))
            return mean_k_t

        mean_k_t = calculate_mean(shells_list_pore)

        # color and marker
        color = cmap(norm(pore_val))
        marker = system_marker(sys_val)

        # label
        label = f"Pore={pore_val},Sys={sys_val},T={int(temp) if temp.is_integer() else temp},seed={seed}"
        x = list(range(1, len(mean_k_t) + 1))

        # plot with line + marker (markersize chosen so markers are visible)
        plt.plot(x, mean_k_t, marker=marker, markersize=6, linestyle='-', color=color, label=label)

# Build a custom legend for markers (system-size groups) and a colorbar for pore sizes
# Marker legend
from matplotlib.lines import Line2D
marker_legend_elems = [
    Line2D([0], [0], marker='*', color='w', markerfacecolor='k', markersize=8, label='< 400'),
    Line2D([0], [0], marker='x', color='w', markerfacecolor='k', markersize=8, label='400 - 600'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='k', markersize=8, label='> 600'),
]
plt.legend(handles=marker_legend_elems, title='System size groups', loc='upper right')

# Colorbar for pore sizes
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])  # required for colorbar
cbar = plt.colorbar(sm, pad=0.02)
cbar.set_label('Pore size')

plt.xlabel('Shell Number')
plt.ylabel('Mean Ring Size')
plt.title('Mean Ring Size vs Shell Number (colored by pore size, marker by system size)')
plt.grid(alpha=0.3)
plt.tight_layout()



plt.savefig(output)
plt.show()

