import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import re

base_dir = '../Results_TR'

pore_s = 30
sys_s = 1232

pore_dir = f"Pore_{pore_s}_{sys_s}"
path = os.path.join(base_dir, pore_dir)

if not os.path.exists(path):
    print('System doesnt exist: see avaiable systems:' , os.listdir(base_dir))

files = glob.glob(f"{path}/T_-*/S_*/2500/netmc.log")

print(len(files))

with open(files[0], 'r') as f:
    text = f.read()
    print(files[0])

# Use regex to find the value after "Monte Carlo acceptance:"
match = re.search(r'Monte Carlo acceptance:\s*([0-9.]+)', text)


temps = []
mc_vals = []

for fil in files:
    with open(fil, 'r') as f:
        text = f.read()
    mc = re.search(r'Monte Carlo acceptance:\s*([0-9.]+)', text)
    if not mc:
        continue

    mc = float(mc.group(1))
    temp = temp = int(fil.split('/T_-')[1].split('/')[0])
    temp = 10**(-temp/1000)

    temps.append(temp)
    mc_vals.append(mc)

print(len(temps), len(mc_vals))
print(mc_vals)

temps = np.array(temps)
mc_vals = np.array(mc_vals)

from matplotlib import rcParams

# --- Style tweaks ---
plt.style.use('default')
rcParams['font.family'] = 'DejaVu Sans'   # clean, readable font
rcParams['font.size'] = 14
rcParams['axes.linewidth'] = 1.2

fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(temps, mc_vals, s=60, edgecolor='black', facecolor='skyblue', marker="*")

ax.set_xlabel('Temperature (a.u.)', fontsize=16)
ax.set_ylabel('Monte Carlo Acceptance', fontsize=16)
ax.set_title(f'Pore_{pore_s}_{sys_s}', fontsize=18, pad=10)

# Remove grid and make ticks cleaner
ax.grid(False)
ax.tick_params(direction='out', length=6, width=1.2, colors='black')

plt.tight_layout()

plt.savefig(f"monte-carlo_figuers/pore_{pore_s}_{sys_s}.png")
plt.show()

