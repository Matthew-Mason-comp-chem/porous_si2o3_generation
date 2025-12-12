import numpy as np
import matplotlib.pyplot as plt

temps = np.array([1000, 1050, 1100, 1150,1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2500, 3000, 4000, 5000])
values = 10**(-temps/1000)

print("plotting")
plt.scatter(values, values)
plt.xlabel('Temperature (K)')
plt.ylabel('10^(-T/1000)')
plt.title('Exponential Decay vs Temperature')
plt.grid(True)

print("showing")
plt.show()

