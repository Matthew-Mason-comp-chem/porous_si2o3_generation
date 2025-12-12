import os
import re
import glob
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

base_dir = "../../Results_TR"

############ Define system ####################
pore_s = 20
sys_s = 478
###############################################

pattern = os.path.join(base_dir, f"Pore_{pore_s}_{sys_s}", "T_-*", "S_*", "2500", "Run", "test_ringstats.out")
print(pattern)

files = glob.glob(pattern)

# Dictionary to group var0 values by temperature
temp_dict = defaultdict(list)

for fil in files:
    with open(fil, 'r') as f:
        array_pn = np.genfromtxt(f)
        var0 = sum([i**2 * (array_pn[-1, i]) for i in range(array_pn.shape[1])]) - 36

    # extract temp number after T_-
    match = re.search(r"T_-(\d+)", fil)
    if match:
        temp_num = int(match.group(1))
        temp = 10**(-temp_num / 1000)
        temp_dict[temp].append(var0)

# average var0 over all seeds for each temperature
temps = sorted(temp_dict.keys())
varos_mean = [np.mean(temp_dict[t]) for t in temps]
varos_std = [np.std(temp_dict[t]) for t in temps]  # optional, for error bars

# plot
plt.errorbar(temps, varos_mean, yerr=varos_std, fmt='o', capsize=4)
plt.xlabel("Temperature (converted)")
plt.ylabel("Average var0")
plt.title(f"Pore {pore_s}, System {sys_s}")
plt.show()

