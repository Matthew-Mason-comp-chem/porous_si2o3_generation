import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np
import glob
import re
import os
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

# --- small helper to choose markers by system size ---
def marker_for_syssize(sys_size):
    if sys_size < 350:
        return '*'
    elif sys_size < 700:
        return 'x'
    else:
        return 'o'

print('Collecting files...')
ele_f = glob.glob("data/*Q*")
if not ele_f:
    print("⚠️  glob didn't find any files in data/*Q*")

ele_f = [path for path in ele_f if "Pore_30" in path]
#print(f"Found {len(ele_f)} files after filtering by '30'")

records = []

# --- Process electro data ---
for path in ele_f:
    #print(f"\n🔍 Processing: {path}")
    try:
        with open(path, 'r') as fh:
            data = np.genfromtxt(fh)
        if data is None or data.size < 3:
            print("⚠️  File seems too short or unreadable, skipping")
            continue
        ele_e = data[2]
    except Exception as e:
        print(f"⚠️  Read fail: {e}")
        continue

    info = re.findall(r"-?\d+", path)
    if len(info) < 5:
        print(f"⚠️  Skipping, not enough numeric tokens: {info}")
        continue

    try:
        pore_s = int(info[0])
        sys_s = int(info[1])
        seed = info[2]
        temp = info[3]
        step = info[4]
    except Exception as e:
        print(f"⚠️  Parse fail: {e}")
        continue

    ele_e = ele_e / int(sys_s)
    folder_name = f'../Results_TR/Pore_{pore_s}_{sys_s}/T_{temp}/S_{seed}/{step}/Run'

    if os.path.exists(folder_name):
        ringstats = os.path.join(folder_name, 'test_ringstats.out')
        if os.path.exists(ringstats):
            try:
                with open(ringstats, 'r') as rf:
                    array_pn = np.genfromtxt(rf)
                if array_pn.ndim < 2:
                    array_pn = np.atleast_2d(array_pn)
                var0 = sum([i**2 * (array_pn[-1, i]) for i in range(array_pn.shape[1])]) - 36
                records.append((pore_s, sys_s, ele_e, var0))
            except Exception as e:
                print(f"⚠️  Could not read ringstats: {e}")
        else:
            print(f"❌ Missing {ringstats}")
    else:
        print(f"❌ Folder missing: {folder_name}")

# --- Convert to array ---
if not records:
    print("❌ No valid data found.")
    raise SystemExit(1)

records = np.array(records, dtype=float)
pore_vals = records[:, 0]
sys_vals = records[:, 1]
elec_e_vals = records[:, 2]
var0_vals = records[:, 3]

pore_min, pore_max = pore_vals.min(), pore_vals.max()
sys_min, sys_max = sys_vals.min(), sys_vals.max()

# --- prepare static color mapping (unchanged) ---
norm = Normalize(vmin=pore_vals.min(), vmax=pore_vals.max())
cmap = plt.get_cmap("viridis")
colors = cmap(norm(pore_vals))  # precompute colors once

# --- Plot setup (initial) ---
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.35)

# store scatter artists so we can remove them later
scatter_artists = []

# initial draw: create scatter artists for all points
for v, e, p, s, c in zip(var0_vals, elec_e_vals, pore_vals, sys_vals, colors):
    mk = marker_for_syssize(s)
    sc = ax.scatter(v, e, marker=mk, color=c, edgecolors='k',
                    linewidths=0.4, s=80, alpha=0.9)
    scatter_artists.append(sc)

ax.set_xlabel("var0")
ax.set_ylabel("elec_e")
ax.set_title(f"elec_e vs var0 | pore:{pore_min:.1f}-{pore_max:.1f} sys:{sys_min:.1f}-{sys_max:.1f}")
ax.grid(True, alpha=0.3)

# create a single static colorbar (only once)
sm = ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
cbar.set_label("Pore size")

# --- Slider axes ---
ax_pore_min = plt.axes([0.25, 0.20, 0.65, 0.03])
ax_pore_max = plt.axes([0.25, 0.15, 0.65, 0.03])
ax_sys_min = plt.axes([0.25, 0.10, 0.65, 0.03])
ax_sys_max = plt.axes([0.25, 0.05, 0.65, 0.03])

slider_pore_min = Slider(ax_pore_min, 'pore min', pore_min, pore_max, valinit=pore_min)
slider_pore_max = Slider(ax_pore_max, 'pore max', pore_min, pore_max, valinit=pore_max)
slider_sys_min = Slider(ax_sys_min, 'sys min', sys_min, sys_max, valinit=sys_min)
slider_sys_max = Slider(ax_sys_max, 'sys max', sys_min, sys_max, valinit=sys_max)

# --- Update (remove previous scatter artists, then draw new ones) ---
def update(val):
    pmin, pmax = slider_pore_min.val, slider_pore_max.val
    smin, smax = slider_sys_min.val, slider_sys_max.val
    mask = (pore_vals >= pmin) & (pore_vals <= pmax) & (sys_vals >= smin) & (sys_vals <= smax)
    print(f"\n🧭 Range filter -> pore:[{pmin},{pmax}], sys:[{smin},{smax}], matches: {mask.sum()}")

    # remove old scatter artists
    for art in scatter_artists:
        try:
            art.remove()
        except Exception:
            pass
    scatter_artists.clear()

    # draw new (filtered) points, appending their artists to the list
    for v, e, p, s, c, keep in zip(var0_vals, elec_e_vals, pore_vals, sys_vals, colors, mask):
        if keep:
            mk = marker_for_syssize(s)
            sc = ax.scatter(v, e, marker=mk, color=c, edgecolors='k',
                            linewidths=0.4, s=80, alpha=0.9)
            scatter_artists.append(sc)

    ax.set_title(f"elec_e vs var0 | pore:{pmin:.1f}-{pmax:.1f} sys:{smin:.1f}-{smax:.1f}")
    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw_idle()

slider_pore_min.on_changed(update)
slider_pore_max.on_changed(update)
slider_sys_min.on_changed(update)
slider_sys_max.on_changed(update)

print("✅ Plot ready — adjust sliders to filter data ranges.")
plt.show()

