import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

fil = "Pore_15_1336_pn_assor.csv"
data = pd.read_csv(fil)

p6s = data['mem_ring_6']
p4s = data["mem_ring_4"]
assor = data['assors']
labels = data['temp']   # these go from 0 → 0.1

# Convert to real temperature scale
temps = 10 ** (-labels / 1000)

# Use normal linear normalization in the converted temperature range
norm = plt.Normalize(temps.min(), temps.max())

# Use reversed colormap so hot (low T value) = red, cold (high T value) = blue
colors = plt.cm.plasma_r(norm(temps))

########################################### plot 1 ###########################################################################

plt.scatter(p6s, assor, c=colors, marker="*", s=80)

# Add colorbar (legend)
sm = plt.cm.ScalarMappable(norm=norm, cmap='plasma_r')
cbar = plt.colorbar(sm)
cbar.set_label('Converted Temperature (10^(-x/1000))')

plt.xlabel("mem_ring_6")
plt.ylabel("assors")
plt.title("Assors vs mem_ring_6 colored by Converted Temperature")

plt.show()

########################################### plot 2 ######################################################

plt.scatter(p4s, assor, c=colors, marker="*", s=80)

# Add colorbar (legend)
sm = plt.cm.ScalarMappable(norm=norm, cmap='plasma_r')
cbar = plt.colorbar(sm)
cbar.set_label('Converted Temperature (10^(-x/1000))')

plt.xlabel("p4")
plt.ylabel("assors")
plt.title("Assors vs mem_ring_6 colored by Converted Temperature")

plt.show()

