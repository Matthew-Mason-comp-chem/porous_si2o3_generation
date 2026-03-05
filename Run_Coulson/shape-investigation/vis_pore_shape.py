import numpy as np
import os
import matplotlib.pyplot as plt
import sys
from collections import Counter

r0 = 2.86667626014*2


# def system
system = "TR"
pore = 17
cell_size = 1336
T = 5000
S = 6
steps = 10000

# extract relevant files
path = '../Results_{:}/Pore_{:}_{:}/T_-{:}/S_{:}/{:}/Run/'.format(system, pore, cell_size, T,S, steps)
if not os.path.isfile('../Results_{:}/Pore_{:}_{:}/TR_rings/results_{:}_{:}_rings.dat'.format(system, pore,cell_size, T,S)):
    print("skipping")
    
    print(os.listdir(f"../Results_TR"))
    print(os.listdir(f"../Results_TR/Pore_{pore}_{cell_size}/T_-{T}"))
    sys.exit(1)

print(path)
with open(path+'test_B_dual.dat', 'r') as f:
   B_net = np.genfromtxt(f, max_rows=1, dtype=int)
with open(path+'test_Si2O3_net.dat', 'r') as f:
   A_net = np.genfromtxt(f, max_rows=cell_size, dtype=int)
with open(path+'test_Si2O3_crds.dat', 'r') as f:
   A_crds = np.genfromtxt(f, dtype=float)
with open('../Results_{:}/Pore_{:}_{:}/TR_rings/results_{:}_{:}_rings.dat'.format(system, pore,cell_size, T,S), 'r') as f:
    array = np.genfromtxt(f, dtype=float)


# find o atoms around pore - this doesnt always work!!!
roundring_si_distance = []
si_crds = []
o_atoms = []
for si in B_net:
    cnxs = A_net[int(si),:]
    for o in cnxs:
#            if int(o) not in o_atoms: o_atoms.append(int(o))
        o_atoms.append(int(o))
    si_crds.append(A_crds[si,:2])

for i in range(len(si_crds)):
    roundring_si_distance.append(np.linalg.norm(np.subtract(si_crds[i-1], si_crds[i]))/r0)
print(np.mean(roundring_si_distance), ' +- ', np.std(roundring_si_distance))
print(roundring_si_distance)
count = Counter(o_atoms)
o_atoms = [item for item, freq in count.items() if freq > 1]

crds = []
for o in o_atoms:
    crds.append(A_crds[o,:2])
points = np.asarray(crds)
#    print(points)

node_radius = 2.63/(2*0.529177)

# plot 
print("here                 ",crds)

#for arr in crds:
#    plt.scatter(arr[0], arr[1], color="blue", label="oxygen")
#
#plt.legend()
#plt.show()

########################### plot 1 sanity check ##################################

fig, ax = plt.subplots()

for arr in crds:
    ax.scatter(arr[0], arr[1], color="black")



# Plot O atoms (red)
for o in range(int(2*A_crds.shape[0]/5), A_crds.shape[0]):
    ax.scatter(A_crds[o, 0], A_crds[o,1], color="red")

# Plot Si atoms (blue)
for si in range(int(2*A_crds.shape[0]/5)):
    ax.scatter(A_crds[si, 0], A_crds[si,1], color="blue")

# Add *one* legend entry per atom type
# Collect unique handles and labels
handles = [
    plt.Line2D([], [], color='red', marker='o', linestyle='None', label='O'),
    plt.Line2D([], [], color='blue', marker='o', linestyle='None', label='Si')
]

count = 0
for arr in crds:
    ax.scatter(arr[0], arr[1], color="black")
    count += 1

print("""


        crds
        
        
        """)

print(crds)


# check if number of atoms in crds matches pore size
if count == pore:
    print("success")
else:
    print("Not indenified the por")



ax.legend(handles=handles)

ax.set_aspect('equal')
ax.axis('off')


plt.close()



############################## plot 2 - hard spheres #################################
from scipy.optimize import minimize
from scipy.spatial import Voronoi, ConvexHull
from shapely.geometry import Point, Polygon

fig, ax = plt.subplots()
ax.plot(points[:, 0], points[:, 1], 'o', color='r')


for o in range(int(2*A_crds.shape[0]/5), A_crds.shape[0]):
    circle = plt.Circle((A_crds[o, 0], A_crds[o,1]), node_radius, color='red', fill=True)
    ax.add_patch(circle)
for si in range(int(2*A_crds.shape[0]/5)):
    circle = plt.Circle((A_crds[si, 0], A_crds[si,1]), 1.609, color='yellow', fill=True)
    ax.add_patch(circle)

def find_largest_inscribed_circle(coords, radius):
    pts = np.asarray(coords)
    hull = ConvexHull(pts)
    poly = Polygon(pts[hull.vertices]).buffer(-radius)
    if poly.is_empty: 
        return (None, 0.0)

    vor = Voronoi(pts)
    best = (None, 0.0)
    for v in vor.vertices:
        p = Point(v)
        if poly.contains(p):
            d = poly.exterior.distance(p)
            if d > best[1]:
                best = (v, d)
    if best[0] is None:
        c = poly.representative_point()
        best = ((c.x, c.y), poly.exterior.distance(c))
    return tuple(best[0]), best[1]

center, radius = find_largest_inscribed_circle(crds, node_radius)



def find_smallest_enclose_circle(coords, node_radius):
    P = np.asarray(coords, dtype=float)
    if len(P) == 0:
        return None, None, None
    if len(P) == 1:
        r = 0.0
        return tuple(P[0]), r, max(r - node_radius, 0.0)

    def circle2(a, b):
        c = (a + b) / 2.0
        return c, np.linalg.norm(a - c)

    def circle3(a, b, c):
        ax, ay = a; bx, by = b; cx, cy = c
        d = 2 * (ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
        if abs(d) < 1e-14:
            return None, np.inf
        a2 = ax*ax + ay*ay
        b2 = bx*bx + by*by
        c2 = cx*cx + cy*cy
        ux = (a2*(by-cy) + b2*(cy-ay) + c2*(ay-by)) / d
        uy = (a2*(cx-bx) + b2*(ax-cx) + c2*(bx-ax)) / d
        center = np.array([ux, uy])
        return center, np.linalg.norm(center - a)

    P = P.copy()
    np.random.shuffle(P)
    c, r = None, 0.0

    for i, p in enumerate(P):
        if c is None or np.linalg.norm(p - c) > r + 1e-12:
            c, r = p.copy(), 0.0
            for j in range(i):
                q = P[j]
                if np.linalg.norm(q - c) > r + 1e-12:
                    c, r = circle2(p, q)
                    for k in range(j):
                        s = P[k]
                        if np.linalg.norm(s - c) > r + 1e-12:
                            c3, r3 = circle3(p, q, s)
                            if c3 is not None:
                                c, r = c3, r3

    rout = max(r - node_radius, 0.0)
    return tuple(c), float(r), rout

center1, enc_r, rout = find_smallest_enclose_circle(crds, node_radius)


# inside circle
ax.add_patch(plt.Circle(center, radius, color='blue', fill=False, lw=2, label='largest inscribed'))
plt.axis('equal')

# outside circle
#ax.add_patch(plt.Circle(center1, rout, color='blue', fill=False, lw=2, label='smallest enclosed'))
#plt.axis('equal')


plt.legend()
plt.savefig(f"lar_inscr_cir_{pore}_{cell_size}_{T}_{S}")
plt.show()
