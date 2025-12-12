import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

# Load data
with open('TriangleRaft_reference_data.dat', 'r') as f:
    data = np.genfromtxt(f)

p6 = data[:, 0]
u2 = data[:, 1]
ass = data[:, 2]
ham = data[:, 3]
elec = data[:, 4]

# Plot 1: p6 vs u2
plt.scatter(p6, u2, marker='*', color='black')
plt.title('p6 vs u2')
plt.xlabel('p6')
plt.ylabel('u2')
plt.savefig('p6_vs_u2.png', dpi=300, bbox_inches='tight')
plt.close()

# Plot 2: u2 vs ham
plt.scatter(u2, ham, marker='*', color='black')
plt.title('u2 vs ham')
plt.xlabel('u2')
plt.ylabel('ham')
plt.savefig('u2_vs_ham.png', dpi=300, bbox_inches='tight')
plt.close()

# Plot 3: u2 vs elec
plt.scatter(u2, elec, marker='*', color='black')
plt.title('u2 vs elec')
plt.xlabel('u2')
plt.ylabel('elec')
plt.savefig('u2_vs_elec.png', dpi=300, bbox_inches='tight')
plt.close()

# Plot 4: p6 vs ass
plt.scatter(p6, ass, marker='*', color='black')
plt.title('p6 vs ass')
plt.xlabel('p6')
plt.ylabel('ass')
plt.savefig('p6_vs_ass.png', dpi=300, bbox_inches='tight')
plt.close()

