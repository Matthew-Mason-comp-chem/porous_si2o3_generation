import numpy as np
import matplotlib.pyplot as plt
import glob
from sklearn.linear_model import LinearRegression
import re
import os
from tqdm import tqdm

pore_size = 30
save_fig = False


print('collecting files')
hamf = glob.glob(f"data/*Pore_{pore_size}*test*")
elef = glob.glob(f"data/*Pore_{pore_size}*Q*")

print(len(hamf), len(elef))

ham_e_tot = []
sys_s_tot = []
var0_tot = []

# process harmonic data
for fil in tqdm(hamf):
    with open(fil, 'r') as f:
        data = np.genfromtxt(f)
        harmonic_e = data[-1, 3]
    info = re.findall(r"-?\d+", fil)
    pore_s = info[0]
    sys_s = info [1]
    temp = info[3]
    seed = info[2]
    step = info[4]
    ham_e = harmonic_e / (int(sys_s))
    
    if ham_e > 10:
        print("not plotting outlier")
        continue

    # check if Run files exist for this simulation - sometimes the sim fails
    folder_name = f'../Results_TR/Pore_{pore_s}_{sys_s}/T_{temp}/S_{seed}/{step}/Run'

    if os.path.exists(folder_name):
        with open(folder_name + '/test_ringstats.out', 'r') as f:
            array_pn = np.genfromtxt(f)
            var0 = sum([i**2 * (array_pn[-1, i]) for i in range(array_pn.shape[1])]) - 36
    else:
        print(f'cant find ringstats: {folder_name}')
    
    # appending data
    ham_e_tot.append(ham_e)
    sys_s_tot.append(int(sys_s))
    var0_tot.append(var0)

print("Getting ready to plot")

# convert to numpy arrays for easy indexing
ham_e_tot = np.array(ham_e_tot)
sys_s_tot = np.array(sys_s_tot)
var0_tot = np.array(var0_tot)

# find unique system sizes and make a tuple
unique_sys_sizes = tuple(sorted(set(sys_s_tot.tolist())))
print("unique system sizes (tuple):", unique_sys_sizes)

# remove NaN var0 points from plotting (if desired)
valid_mask = ~np.isnan(var0_tot)
if not np.any(valid_mask):
    raise RuntimeError("No valid var0 values found — cannot plot.")

x = var0_tot[valid_mask]
y = ham_e_tot[valid_mask]
sizes = sys_s_tot[valid_mask]

# set up colormap mapping from smallest -> biggest system size
cmap = plt.get_cmap("viridis")
vmin = sizes.min()
vmax = sizes.max()
norm = plt.Normalize(vmin=vmin, vmax=vmax)

# make scatter plot with star markers, colored by system size
plt.figure(figsize=(7,5))
sc = plt.scatter(x, y, marker='*', s=150, c=sizes, cmap=cmap, norm=norm, edgecolors='k', linewidths=0.4)
plt.xlabel("Var₀")
plt.ylabel("Harmonic energy per atom")
plt.title(f"Harmonic energy vs Var₀ (Pore {pore_size})")
plt.grid(True, alpha=0.3)

# Colorbar showing discrete ticks for the unique system sizes
from matplotlib.cm import ScalarMappable
sm = ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])   # for colorbar
cbar = plt.colorbar(sm, pad=0.02)
# set ticks at the unique system sizes (works because colorbar values are data values)
cbar.set_ticks(list(unique_sys_sizes))
cbar.set_label("System size (atoms)")
cbar.ax.set_yticklabels([str(u) for u in unique_sys_sizes])

# Plotting reference data
# --- Add reference data + linear regression fit ---
ref_file = "TriangleRaft_reference_data.dat"
try:
    ref_data = np.genfromtxt(ref_file)
    ref_var0 = ref_data[:, 1]   # column 1 (0-based index)
    ref_hamE = ref_data[:, 3]   # column 4 (0-based index)

    # perform linear regression
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(ref_var0.reshape(-1, 1), ref_hamE)
    xfit = np.linspace(ref_var0.min(), ref_var0.max(), 200)
    yfit = model.predict(xfit.reshape(-1, 1))

    # plot reference points and regression line
    plt.scatter(ref_var0, ref_hamE, color='gray', marker='o', label='Reference data')
    plt.plot(xfit, yfit, color='black', linestyle='--', label='Linear fit')

    print(f"Reference linear fit: y = {model.coef_[0]:.3g} * x + {model.intercept_:.3g}")

except Exception as e:
    print(f"Could not load or fit reference data: {e}")



outname = f"Hamvsvar_{pore_size}"

if save_fig:
    plt.savefig(outname, dpi=300)
    print("Saved figure to", outname)
else:
    plt.show()

