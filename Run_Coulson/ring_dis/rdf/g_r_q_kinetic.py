import numpy as np
import matplotlib.pyplot as plt


data = np.loadtxt("data/ring_growth/Gq_15.dat")

print(data[:, 1])

plt.plot(data[:, 0], data[:, 1])
plt.xlim(0, 50)

plt.show()
