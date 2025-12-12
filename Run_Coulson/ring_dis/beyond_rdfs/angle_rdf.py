import matplotlib.pyplot as plt
import numpy as np
import glob
import os
from tqdm import tqdm

savefig=False

# rcparams config


# defining system
pore = 24
system = 1290
temps = [1000, 3000, 5000]
cut_off = 200

base_dir = "../../Results_TR"


for T in temps:
    temp = T
    fil = os.path.join(base_dir, f"Pore_{pore}_{system}", "TR_theta", f"results_{temp}_*")    
    files = glob.glob(fil)
    
    
    all_theta = []
    all_radius = []
    all_charges =[]

    for fi in tqdm(files):
        data = np.loadtxt(fi, delimiter=",", skiprows=1)
        
        radius = data[:, 1]
        mask = radius < cut_off

        theta = data[:, 2][mask]
        radius = radius[mask]
        sizes = data[:, 3][mask]
        charges = sizes - 6
        
        # filter radius based on angles
        # if minus and greater then -45 or if plus and greatet then 45
        #ifor i in range(len(theta)):
        #    if theta[i] < 0 and theta[i] >= -35:
        #        all_theta.append(theta[i])
        #        all_radius.append(radius[i])
        #        all_charges.append(charges[i])
        #    elif theta[i] > 0 and theta[i] <= 35:
        #        all_theta.append(theta[i])
        #        all_radius.append(radius[i])
        #        all_charges.append(charges[i])
                # after computing: theta, radius, sizes, charges
        tol = 15  # +-35 degrees around each orthogonal direction
        centers = {'right': 0, 'up': 90, 'left': 180, 'down': -90}

        def ang_diff_array(a, b):
            """Smallest signed difference between a and b in degrees within (-180,180]."""
            return ( (a - b + 180) % 360 ) - 180

        # combined mask for any orthogonal direction
        mask_dir_total = np.zeros_like(theta, dtype=bool)

        # optional: collect per-direction groups if you want
        by_dir = {k: {'idx': [], 'theta': [], 'radius': [], 'charges': []} for k in centers}

        for name, c in centers.items():
            m = np.abs(ang_diff_array(theta, c)) <= tol
            if np.any(m):
                # store per-direction (indices are relative to the masked arrays)
                idxs = np.nonzero(m)[0]
                by_dir[name]['idx'].extend(idxs.tolist())
                by_dir[name]['theta'].extend(theta[m].tolist())
                by_dir[name]['radius'].extend(radius[m].tolist())
                by_dir[name]['charges'].extend(charges[m].tolist())

            mask_dir_total |= m

        # append selected entries from this file to the global lists
        all_theta.extend(theta[mask_dir_total].tolist())
        all_radius.extend(radius[mask_dir_total].tolist())
        all_charges.extend(charges[mask_dir_total].tolist()) 


    all_theta = np.array(all_theta)
    all_radius = np.array(all_radius)
    all_charges = np.array(all_charges)

    ##### plot 1 #####


      # Define bins
    bins = np.linspace(0, cut_off, 100)  # 50 bins (10 units wide)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])

    counts_w, _ = np.histogram(all_radius, bins=bins, weights=all_charges)
    
    r1 = bins[:-1]
    r2 = bins[1:]
    ring_areas = np.pi * (r2**2 - r1**2)
    

    g_r_q = counts_w / ring_areas

    plt.plot(bin_centers, g_r_q, marker='', label=T)
    plt.title('Ring charge radial distribution functions')
    plt.xlabel('Distance (r)')
    plt.ylabel('G(r)q')
    plt.grid(False)


if savefig:
    plt.savefig(f"Pore_{pore}_{system}_var_T_qrdf.png")

plt.legend()
plt.show()

