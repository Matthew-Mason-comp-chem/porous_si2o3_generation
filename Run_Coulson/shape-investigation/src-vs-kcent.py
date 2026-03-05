"""
"""

basedir="../Results_TR"

import numpy as np
import os
import matplotlib.pyplot as plt
import sys
from collections import Counter
import glob
#from scipy.optimize import minimize
#from scipy.spatial import Voronoi, ConvexHull
#from shapely.geometry import Point, Polygon
import scipy
import csv


r0 = 2.86667626014*2
node_radius = 2.63/(2*0.529177)


#### Def systems ###
sys_s_min = 1000
sys_s_max = 1400
pore_sizes = range(8, 36, 1)
steps = 10000 

temps=[5000, 1300]
labels = ["r", "b", "black"]




# Saving data
CSV_FILE = "results.csv"
HEADERS  = ["k", "sys_s", "src_avgs", "T"]
# ── load temperatures already stored in the file ─────────────────────────────
existing_temps = set()

if os.path.exists(CSV_FILE):
    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing_temps.add(float(row["T"]))

# ── write new rows only for temperatures not yet present ─────────────────────
file_exists = os.path.exists(CSV_FILE)




failed= []

for idx, T in enumerate(temps):
    label = labels[idx]
    temp = T
    src_avgs = []
    k = []
    sys_s = []
    for pore in pore_sizes:
        dirs=glob.glob(f"{basedir}/Pore_{pore}_*")
        if dirs:
            print(pore, "exists")
            for d in dirs:
                try:
                    num = int(d.split("_")[-1])
                except ValueError:
                    continue
                if num > sys_s_min and num < sys_s_max:
                    print("found", d)
                    


                    # obtain src at temp and avg over seeds
                    # 1. Find all seeds
                    path = os.path.join(d, f"T_-{temp}/S_*/*")
                    seeds = glob.glob(path)
                    
                    src = []
                    for s in seeds:
                        print(s)
                        # 2. cal src for system
                        path = os.path.join(s, "Run/")
                        
                        if not os.path.exists(path+'test_B_dual.dat'):
                            continue
                        
                        if pore > 12:
                            with open(path+'test_B_dual.dat', 'r') as f:
                                for line in f:
                                    values = list(map(int, line.split()))
                                    if len(values) == pore:
                                        B_net = np.array(values, dtype=int)
                                        break

                        else:
                            # Find all matching rows
                            candidate_rows = []
                            with open(path+'test_B_dual.dat', 'r') as f:
                                for line in f:
                                    values = list(map(int, line.split()))
                                    if len(values) == pore:
                                        candidate_rows.append(np.array(values, dtype=int))

                            if len(candidate_rows) == 1:
                                B_net = candidate_rows[0]
                            else:
                                # Load coordinates to find centre
                                with open(path+'test_Si2O3_crds.dat', 'r') as f:
                                    A_crds = np.genfromtxt(f, dtype=float)

                                # Find centre from A_crds x/y bounds
                                x_mid = (A_crds[:, 0].max() + A_crds[:, 0].min()) / 2
                                y_mid = (A_crds[:, 1].max() + A_crds[:, 1].min()) / 2
                                centre = np.array([x_mid, y_mid])

                                # For each candidate row, compute COM of its ring and find distance to centre
                                best_row = None
                                best_dist = np.inf
                                for row in candidate_rows:
                                    ring_crds = np.array([A_crds[si, :2] for si in row])
                                    com = ring_crds.mean(axis=0)
                                    dist = np.linalg.norm(com - centre)
                                    if dist < best_dist:
                                        best_dist = dist
                                        best_row = row

                                B_net = best_row



                        #with open(path+'test_B_dual.dat', 'r') as f:
                        #    B_net = np.genfromtxt(f, max_rows=1, dtype=int)
                        
                        with open(path+'test_Si2O3_net.dat', 'r') as f:
                           A_net = np.genfromtxt(f, max_rows=num, dtype=int)
                        with open(path+'test_Si2O3_crds.dat', 'r') as f:
                           A_crds = np.genfromtxt(f, dtype=float)
                      
                        # find o atoms around pore
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
                        #print(np.mean(roundring_si_distance), ' +- ', np.std(roundring_si_distance))
                        #print(roundring_si_distance)
                        count = Counter(o_atoms)
                        o_atoms = [item for item, freq in count.items() if freq > 1]

                        count = 0
                        crds = []
                        for o in o_atoms:
                            crds.append(A_crds[o,:2])
                            count += 1
                        crds = np.asarray(crds)
                        
                        if count == pore:
                            print("success")
                        else:
                            failed.append(pore)

                        # Running analysis on only oxygen coordinates 
                        def Hull_Stats(A, area, perimeter):
                            hull = scipy.spatial.ConvexHull(A)
                            hull_area = hull.volume
                            hull_perimeter = hull.area
                            balance_repartition = np.sqrt(min([np.std(A[:, 0]), np.std(A[:, 1])])/max([np.std(A[:, 0]), np.std(A[:, 1])]))

                            solidity = area/hull_area
                            convexity = hull_perimeter/perimeter
                            SRC = solidity * balance_repartition * convexity
                            return SRC
                        
                        def calculate_area(A):
                            x = A[:, 0]
                            y = A[:, 1]
                            return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

                        def calculate_perimeter(A):
                            return np.sum(np.sqrt(np.sum(np.diff(A, axis=0)**2, axis=1))) + np.sqrt(np.sum((A[0] - A[-1])**2))
         
                        area = calculate_area(crds)
                        perimeter = calculate_perimeter(crds)
                        SRC = Hull_Stats(crds, area, perimeter)

                        #print(SRC)
                        if SRC > 0.1: 
                            src.append(SRC)

                        #def find_largest_inscribed_circle(coords, radius):
                        #    pts = np.asarray(coords)
                        #    hull = ConvexHull(pts)
                        #    poly = Polygon(pts[hull.vertices]).buffer(-radius)
                        #    if poly.is_empty:
                        #        return (None, 0.0)
                        #    vor = Voronoi(pts)
                        #    best = (None, 0.0)
                        #    for v in vor.vertices:
                        #        p = Point(v)
                        #        if poly.contains(p):
                        #            d = poly.exterior.distance(p)
                        #            if d > best[1]:
                        #                best = (v, d)
                        #    if best[0] is None:
                        #        c = poly.representative_point()
                        #        best = ((c.x, c.y), poly.exterior.distance(c))
                        #    return tuple(best[0]), best[1]
                        #
                        #center, radius = find_largest_inscribed_circle(crds, node_radius)
                        #
                        #print(radius)
                        #
                        #def find_smallest_enclose_circle(coords, node_radius):
                        #    P = np.asarray(coords, dtype=float)
                        #    if len(P) == 0:
                        #        return None, None, None
                        #    if len(P) == 1:
                        #        r = 0.0
                        #        return tuple(P[0]), r, max(r - node_radius, 0.0)
                        #    def circle2(a, b):
                        #        c = (a + b) / 2.0
                        #        return c, np.linalg.norm(a - c)
    #
                        #    def circle3(a, b, c):
                        #        ax, ay = a; bx, by = b; cx, cy = c
                        #        d = 2 * (ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
                        #        if abs(d) < 1e-14:
                        #            return None, np.inf
                        #        a2 = ax*ax + ay*ay
                        #        b2 = bx*bx + by*by
                        #        c2 = cx*cx + cy*cy
                        #        ux = (a2*(by-cy) + b2*(cy-ay) + c2*(ay-by)) / d
                        #        uy = (a2*(cx-bx) + b2*(ax-cx) + c2*(bx-ax)) / d
                        #        center = np.array([ux, uy])
                        #        return center, np.linalg.norm(center - a)
    #
                         #   P = P.copy()
                        #    np.random.shuffle(P)
                        #    c, r = None, 0.0
    #
     #                       for i, p in enumerate(P):
     #                           if c is None or np.linalg.norm(p - c) > r + 1e-12:
     #                               c, r = p.copy(), 0.0
     #                               for j in range(i):
    #                                    q = P[j]
    #                                    if np.linalg.norm(q - c) > r + 1e-12:
    #                                        c, r = circle2(p, q)
    #                                        for k in range(j):
    #                                            s = P[k]
    #                                            if np.linalg.norm(s - c) > r + 1e-12:
    #                                                c3, r3 = circle3(p, q, s)
    #                                                if c3 is not None:
    #                                                    c, r = c3, r3
    #
    #                        rout = max(r - node_radius, 0.0)
    #                        return tuple(c), float(r), rout
    #
    #                    center, enc_r, rout = find_smallest_enclose_circle(crds, node_radius)
    #                    print(rout)
                    
                    print(f"Pore {pore}", src)
                    src = np.array(src)
                    src_mean = np.mean(src)
                    print(src_mean)
                    
                    if src_mean > 0.1:
                        src_avgs.append(src_mean)
                        k.append(pore)
                        sys_s.append(num)
                        continue
    print(T)
    print(k)
    print(src_avgs)
    print(sys_s)

    plt.scatter(k, src_avgs, label=label)
    

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)

        if not file_exists:
            writer.writeheader()

        if T in existing_temps:
            print(f"T={T} already in file — skipping.")
            continue
        
        print(f"Writing data for T={T} …")
        for k_val, sys_val, src_val in zip(k, sys_s, src_avgs):
            writer.writerow({
                "k":        k_val,
                "sys_s":    sys_val,
                "src_avgs": src_val,
                "T":        T,
            })

    print("Done.")

print(failed, "systems were src is sus")

plt.legend()
plt.show()
