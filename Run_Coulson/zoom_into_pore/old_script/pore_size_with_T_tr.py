import numpy as np
import matplotlib.pyplot as plt

T_list = []
A_list = []
shell_1_list = []
cell_size_list = []
color_list = []
color = ['r', 'g', 'b', 'c', 'tab:pink', 'y', 'm', 'k']
system = 'TR'
r0 = 2.86667626014*2

n_list = []
maxrlist = []
for i in range(6,26,2):
    interior_angle = np.pi*(i-2)/i

#    print('    ', 2*np.pi/3*180/np.pi, interior_angle*180/np.pi, (interior_angle-2*np.pi/3)*180/np.pi)
    remainder = (interior_angle-2*np.pi/3)/2
    
#    print(i,remainder,np.pi*22.5/180, remainder*180/np.pi)
    n_list.append(i)
    maxrlist.append((1.609*2*np.cos(remainder))/(2*np.tan(np.pi/i))-1.609*np.sin(remainder)-2.63/2)
    print(i, (1.609*2*np.cos(remainder))/(2*np.tan(np.pi/i))-1.609*np.sin(remainder)-2.63/2)
 
plt.scatter([i for i in n_list if i<12], [maxrlist[i] for i in range(len(n_list)) if n_list[i]<12], color='b')
plt.scatter([i for i in n_list if i>=12], [maxrlist[i] for i in range(len(n_list)) if n_list[i]>=12], color='r')
plt.plot(n_list, [2.60/2 for i in n_list], label='He')
plt.plot(n_list, [2.75/2 for i in n_list], label='Ne')
plt.plot(n_list, [3.40/2 for i in n_list], label='Ar')
plt.plot(n_list, [3.65/2 for i in n_list], label='Kr')


plt.plot(n_list, [3.64/2 for i in n_list], label=r'N$_2$')
plt.plot(n_list, [3.30/2 for i in n_list], label=r'CO$_{2}$')
plt.plot(n_list, [3.46/2 for i in n_list], label=r'O$_{2}$')
plt.plot(n_list, [5.50/2 for i in n_list], label=r'SF$_{6}$')


plt.legend()
plt.show()

import os

import numpy as np
from scipy.spatial import Delaunay, Voronoi
from shapely.geometry import Point, Polygon
from shapely.geometry.polygon import Polygon


from collections import Counter
import matplotlib.patches as patches
from scipy.spatial import ConvexHull, Voronoi


#def refinterstitial():
#    with open('24_atoms.out', 'r') as f:
#        array = np.genfromtxt(f)


def interstitial2(B_net, A_net, A_crds):
    # Example set of points (nodes)
    # net contains Si atoms - model all oxygens attached to these si? no just edge ones
#    plt.scatter(A_crds[:,2], A_crds[:,3])
    roundring_si_distance = []
    si_crds = []
    o_atoms = []
    for si in B_net:
        cnxs = A_net[int(si),:]
        for o in cnxs:
#            if int(o) not in o_atoms: o_atoms.append(int(o))
            o_atoms.append(int(o))
        si_crds.append(A_crds[si,:2])
    for i in range(len(si_crds)):x.idd
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
#    node_radius = 2.63

    hull = ConvexHull(points)
    hull_points = points[hull.vertices]

    # Create a polygon from the convex hull
    polygon = Polygon(hull_points)
    polygon = polygon.buffer(-node_radius)
    # Create the Voronoi diagram from the points
    vor = Voronoi(points)
    # Function to find the largest empty circle (incircle)
    def largest_incircle(voronoi, polygon):
        max_circle = (None, 0)  # (center, radius)

        # Loop through Voronoi vertices
        for point in voronoi.vertices:
            # Check if the Voronoi vertex is inside the polygon
            if polygon.contains(Point(point)):
                # Find the distance from this vertex to the edges of the polygon
                distance = polygon.exterior.distance(Point(point))
            
                # Update the max_circle if this is the largest distance found
                if distance > max_circle[1]:
                    max_circle = (point, distance)
    
        return max_circle
  
    # Find the largest inscribed circle
    center, radius = largest_incircle(vor, polygon)
# Plotting 
    plot = True
    if plot:
        fig, ax = plt.subplots()
        ax.plot(points[:, 0], points[:, 1], 'o', color='r')
        for point_count in range(points.shape[0]):
            circle = plt.Circle((points[point_count,0], points[point_count,1]), node_radius, color='red', fill=True)
            ax.add_patch(circle)

        for o in range(int(2*A_crds.shape[0]/5), A_crds.shape[0]):
 
            circle = plt.Circle((A_crds[o, 0], A_crds[o,1]), node_radius, color='red', fill=True)
            ax.add_patch(circle)
        for si in range(int(2*A_crds.shape[0]/5)):
            circle = plt.Circle((A_crds[si, 0], A_crds[si,1]), 1.609, color='yellow', fill=True)
            ax.add_patch(circle)


# Plot the convex hull
        for simplex in hull.simplices:
            ax.plot(points[simplex, 0], points[simplex, 1], 'k-')

# Plot the largest inscribed circle
        circle = plt.Circle(center, radius, color='black', fill=False, label="Largest Inscribed Circle")
        ax.add_patch(circle)
#        circle = plt.Circle(center, ((1/0.529177) * ((1.609*2*np.cos(np.pi*22.5/180))/(2*np.tan(np.pi/24))-1.609*np.sin(np.pi*22.5/180)-2.63/2)), color='black', fill=False, label="Largest Inscribed Circle")
#        ax.add_patch(circle)
    # Set axis limits and labels
        ax.set_aspect('equal', 'box')
#    ax.set_xlim(-1, 5)
#    ax.set_ylim(-1, 5)
        ax.axis('off')
        plt.legend()
        plt.show()
    print(radius, ((1/0.529177) * ((1.609*2*np.cos(np.pi*22.5/180))/(2*np.tan(np.pi/24))-1.609*np.sin(np.pi*22.5/180)-2.73)))
    print(radius*0.529177 > 1.609*2*np.cos(np.pi*22.5/180)/(2*np.tan(np.pi/24))-1.609*np.sin(np.pi*22.5/180)-2.73)
    if radius > (1/0.529177)*((1.609*2*np.cos(np.pi*22.5/180))/(2*np.tan(np.pi/24))-1.609*np.sin(np.pi*22.5/180)-2.73):
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> broken')
    if radius*0.529177 > 1.609*2*np.cos(np.pi*22.5/180)/(2*np.tan(np.pi/24))-1.609*np.sin(np.pi*22.5/180)-2.73:
        print('###################################################### broken')
    return radius*0.529177#, (1.609*2*np.cos(np.pi*22.5/180))/(2*np.tan(np.pi/24))-1.609*np.sin(np.pi*22.5/180)-2.73
def interstitial(B_net, A_net, A_crds):
    # Example set of points (nodes)
    # net contains Si atoms - model all oxygens attached to these si? no just edge ones
#    plt.scatter(A_crds[:,2], A_crds[:,3])
    si_crds = []
    o_atoms = []
    for si in B_net:
        cnxs = A_net[int(si),:]
        for o in cnxs:
#            if int(o) not in o_atoms: o_atoms.append(int(o))
            o_atoms.append(int(o))
        si_crds.append(A_crds[si,:2])
    count = Counter(o_atoms)
    o_atoms = [item for item, freq in count.items() if freq > 1]

    crds = []
    for o in o_atoms:
        crds.append(A_crds[o,:2])
    points = np.asarray(crds)
#    print(points)
    
    node_radius = 5.10226
    node_radius = 2.63
    # Create points as shapely Points
    shapely_points = [Point(p).buffer(node_radius) for p in points]

    # Create the union of all points
    union_points = shapely_points[0]
    for point in shapely_points[1:]:
        union_points = union_points.union(point)

    # Compute Delaunay triangulation
    delaunay = Delaunay(points)
    triangles = points[delaunay.simplices]

    # Compute Voronoi diagram
    vor = Voronoi(points)
    vertices = vor.vertices

    # Define the polygon (inflated boundary)
    polygon = union_points.convex_hull

    # Find the largest empty circle
    max_radius = 0
    best_center = None

    for vertex in vertices:
        point = Point(vertex)
        if polygon.contains(point):
           radius = point.distance(polygon.exterior)
           if radius > max_radius:
               max_radius = radius
               best_center = vertex
    #print(crds, vertex)
    circle_list = []
    for local in crds:
        circle_list.append(patches.Circle((local[0], local[1]), node_radius, edgecolor='red', facecolor='red'))
#        ax.add_patch(circle)
#        circle = plt.Circle((local[0], local[1]), node_radius, color='r')
#        ax.add_patch(circle)
#    plt.scatter(A_crds[:,0], A_crds[:,1], color='b')
##    plt.scatter([local[0] for local in si_crds], [local[1] for local in si_crds], color='y', markersize=200*node_radius)
##    plt.scatter([local[0] for local in crds], [local[1] for local in crds], color='r', markersize=200*node_radius)
    pore = patches.Circle((vertex[0], vertex[1]), max_radius, edgecolor='black', facecolor='none')
#    ax.add_patch(circle)
##    plt.scatter(vertex[0], vertex[1], color='k',markersize=200*max_radius)
#    ax.set_aspect('equal', 'box')
#    ax.set_xlim(-radius-1, radius+1)
#    ax.set_ylim(-radius-1, radius+1)
##    plt.show()
#    print(max_radius)
    fig, ax = plt.subplots()
    for circle in circle_list:
        ax.add_patch(circle)
    ax.add_patch(pore)
    plt.scatter([local[0] for local in si_crds], [local[1] for local in si_crds], color='y', s=node_radius)
    plt.scatter([local[0] for local in crds], [local[1] for local in crds], color='r', s=node_radius)
    plt.show()

    return max_radius/1.88973

#fig, ax = plt.subplots()
#
#for cell_size in [140, 228, 332, 452, 588, 740]:
#    index = [140, 228, 332, 452, 588, 740].index(cell_size)
#    fig, ax = plt.subplots()
#
##for cell_size in [740]:
##    index = [740].index(cell_size)
#
#
#    T_list = []
#    A_list = []
#    shell_1_list = []
#    cell_size_list = []
#    color_list = []
#
#    for T in range(1000,3001,100):
#        for S in range(0,5,1):
#            print(cell_size, T, S)         
#            with open('Results_{:}/Pore_24_{:}/TR_rings/TR_24_{:}_{:}_rings.dat'.format(system, cell_size, T,S), 'r') as f:
#               array = np.genfromtxt(f, dtype=float)
#            T_list.append(10**(-T/1000))
#            if system=='TR':
#                A_list.append(array[4,0]/r0**2)
#            else:
#                A_list.append(array[4,0])
#     
#            with open('Results_{:}/Pore_24_{:}/TR_SHELLS/TR_24_{:}_{:}_shell.dat'.format(system, cell_size, T,S), 'r') as f:
#               shell0 = np.genfromtxt(f, max_rows=1, dtype=float)
#            shell_1_list.append(np.mean(shell0))
#            cell_size_list.append(cell_size)
#            color_list.append(color[index])
#
##    ax.plot(T_list, A_list, color=color_list[0], label='{:} atoms'.format(cell_size))
#    ax.scatter(T_list, A_list, color=color_list, label='{:} atoms'.format(cell_size))
#
#    ax.set_xlabel('log$_{10}$(T)')           
#    ax.set_ylabel('Pore area')
#    ax.set_xscale('log')
#    plt.legend()
#    plt.show()
#
#


fig, ax = plt.subplots()
#f = open('Area_vs_T.dat', 'w')
for system in ['TR']:
    mean_T = []
    mean_A = []
    u_A = []
    l_A = []

    if system=='TR': color='r'
    else: color='b'
    for T in range(1000,5001,50):
        cellsize_list = []
        A_list = []
        T_list = []
        for S in range(0,50,1):
            for cell_size in [228, 440, 1290]:
                index = [228, 440, 1290].index(cell_size)
                #if os.path.isfile('../../Results_{:}/Pore_24_{:}/TR_rings/TR_24_{:}_{:}_rings.dat'.format(system, cell_size, T,S))==False:    print('------- Absent Results_{:}/Pore_24_{:}/TR_rings/results_{:}_{:}_rings.dat'.format(system, cell_size, T,S))
                if not os.path.isfile('../../Results_{:}/Pore_24_{:}/TR_rings/results_{:}_{:}_rings.dat'.format(system, cell_size, T,S)):
                    continue
                
                with open('../../Results_{:}/Pore_24_{:}/TR_rings/results_{:}_{:}_rings.dat'.format(system, cell_size, T,S), 'r') as f:
                   array = np.genfromtxt(f, dtype=float)
                if system=='TR':
                    cellsize_list.append(cell_size)
                    T_list.append(10**(-T/1000))
                    A_list.append(array[3,0])
                else:
                    cellsize_list.append(cell_size)
                    T_list.append(10**(-T/1000))
                    A_list.append(array[3,0])

        mean_T.append(10**(-T/1000))
        mean_A.append(np.mean(A_list))
#        u_A.append(np.percentile(A_list,0.25))
#        l_A.append(np.percentile(A_list,0.75))
        if system=='TR': 
            ax.scatter(T_list, A_list, color=color, alpha=0.2, marker='x')
        else:
            ax.scatter(T_list, A_list, color=color, alpha=0.2, marker='*')
            #    ax.plot(T_list, A_list, color=color_list[0], label='{:} atoms'.format(cell_size))
        with open('TriangleRaft_FixedPoreSize_SRC_vs_T.dat', 'a+') as f:
            for i in range(len(T_list)):
                f.write('{:.8f} {:.8f} {:.8f}\n'.format(cellsize_list[i], T_list[i], A_list[i]))
    ax.plot(mean_T, mean_A, color=color)
f.close()
ax.set_xlabel('log$_{10}$(T)')
ax.set_ylabel('Shape Regularity Coefficient')
ax.set_xscale('log')
plt.ylim(0.5,1)
plt.legend()
plt.show()



fig, ax = plt.subplots()

for system in ['TR']:
    mean_T = []
    mean_A = []
    u_A = []
    l_A = []
    
    if system=='TR': color='r'
    else: color='b'
    for T in range(1000,5001,50):
        A_list = []
        T_list = []
        for S in range(0,50,1):
            for cell_size in [228, 440, 1290]:
                index = [228, 440, 1290].index(cell_size)
                #if os.path.isfile('../../Results_{:}/Pore_24_{:}/TR_rings/TR_24_{:}_{:}_rings.dat'.format(system, cell_size, T,S))==False:    print('------- Absent Results_{:}/Pore_24_{:}/TR_rings/TR_24_{:}_{:}_rings.dat'.format(system, cell_size, T,S))
                
                path = '../../Results_{:}/Pore_24_{:}/T_-{:}/S_{:}/2500/Run/'.format(system, cell_size, T,S)
                #print(path) 
                if not os.path.isfile('../../Results_{:}/Pore_24_{:}/TR_rings/results_{:}_{:}_rings.dat'.format(system, cell_size, T,S)):
                    continue

                with open('../../Results_{:}/Pore_24_{:}/TR_rings/results_{:}_{:}_rings.dat'.format(system, cell_size, T,S), 'r') as f:
                   array = np.genfromtxt(f, dtype=float)


                if system=='TR':
                    T_list.append(10**(-T/1000))
                    cellsize_list.append(cell_size)
                    for val in np.where(array[1,:]==24):
                        A_list.append(array[3,val]/r0**2)
                else:
                    T_list.append(10**(-T/1000))
                    cellsize_list.append(cell_size)
                    for val in np.where(array[1,:]==24):
                        A_list.append(array[3,val])
                                
        mean_T.append(10**(-T/1000))
        mean_A.append(np.mean(A_list))
#        u_A.append(np.percentile(A_list,0.25))
#        l_A.append(np.percentile(A_list,0.75))
        ax.scatter(T_list, A_list, color=color, alpha=0.2)
            #    ax.plot(T_list, A_list, color=color_list[0], label='{:} atoms'.format(cell_size))
        #print(T_list, A_list)
        with open('TriangleRaft_FixedPoreSize_ReducedArea_vs_T.dat', 'a+') as f:
            for i in range(len(T_list)):
                f.write('{:.8f} {:.8f} {:.8f}\n'.format(cellsize_list[i], float(T_list[i]), float(A_list[i])))
    ax.plot(mean_T, mean_A, color=color)
    ax.plot(mean_T, [(24*1.2**2)/(4*np.tan(np.pi/24)) for i in mean_T], color='k', label='Ideal Polygon Area')
 
ax.set_xlabel('log$_{10}$(T)')           
ax.set_ylabel('Pore area')
ax.set_xscale('log')
plt.ylim(30,80)
plt.legend()
plt.show()

fig, ax = plt.subplots()
mean_A = []
mean_T = []
mean_r = []
system = 'TR'
for T in range(1000,3001,50):
    A_list = []
    T_list = []
    r_list = []
    for S in range(0,50,1):
        for cell_size in [228, 440, 1290]:
           index = [228, 440, 1290].index(cell_size)
           path = '../../Results_{:}/Pore_24_{:}/T_-{:}/S_{:}/2500/Run/'.format(system, cell_size, T,S)
           if not os.path.isfile('../../Results_{:}/Pore_24_{:}/TR_rings/results_{:}_{:}_rings.dat'.format(system, cell_size, T,S)):
               continue
           
           print(path) 
           with open(path+'test_B_dual.dat', 'r') as f:
               B_net = np.genfromtxt(f, max_rows=1, dtype=int)
           with open(path+'test_Si2O3_net.dat', 'r') as f:
               A_net = np.genfromtxt(f, max_rows=cell_size, dtype=int)
           with open(path+'test_Si2O3_crds.dat', 'r') as f:
               A_crds = np.genfromtxt(f, dtype=float)
           with open('../../Results_{:}/Pore_24_{:}/TR_rings/results_{:}_{:}_rings.dat'.format(system, cell_size, T,S), 'r') as f:
               array = np.genfromtxt(f, dtype=float)
           T_list.append(10**(-T/1000))
           A_list.append(array[3,0]/r0**2)
           
           r_list.append(interstitial2(B_net, A_net, A_crds))
           
    mean_T.append(10**(-T/1000))
    mean_A.append(np.mean(A_list))
    mean_r.append(np.mean(r_list))
#        u_A.append(np.percentile(A_list,0.25))
#        l_A.append(np.percentile(A_list,0.75))
    print([i-((1.609*2*np.cos(np.pi*22.5/180))/(2*np.tan(np.pi/24))-1.609*np.sin(np.pi*22.5/180)-2.63/2) for i in r_list])
    ax.scatter(T_list, r_list, color=color, alpha=0.2)
            #    ax.plot(T_list, A_list, color=color_list[0], label='{:} atoms'.format(cell_size))
ax.plot(mean_T, mean_r, color=color)
#print(mean_T, np.cos(np.pi()/24))
ax.plot(mean_T, [((1.609*2*np.cos(np.pi*22.5/180))/(2*np.tan(np.pi/24))-1.609*np.sin(np.pi*22.5/180)-2.63/2) for i in mean_T], color='k', label='Regular Polygon')

ax.set_xlabel('log$_{10}$(T)')
ax.set_ylabel('Interstitial Site Radius $\AA$')
ax.set_xscale('log')
plt.legend()
plt.show()

print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
print((1.609*2*np.cos(np.pi*0/180))/(2*np.tan(np.pi/6))-2.63/2)

#for cell_size in [140, 228, 332, 452, 588, 740]:
#    index = [140, 228, 332, 452, 588, 740].index(cell_size)
#    fig, ax = plt.subplots()
#
##for cell_size in [740]:
##    index = [740].index(cell_size)
#
#
#    T_list = []
#    A_list = []
#    shell_1_list = []
#    cell_size_list = []
#    color_list = []
#
#    for T in range(1000,3001,100):
#        for S in range(0,5,1):
#            print(cell_size, T, S)
#            with open('Results_{:}/Pore_24_{:}/TR_rings/TR_24_{:}_{:}_rings.dat'.format(system, cell_size, T,S), 'r') as f:
#               array = np.genfromtxt(f, dtype=float)
#            T_list.append(10**(-T/1000))
#            if system=='TR':
#                A_list.append(array[4,0]/r0**2)
#            else:
#                A_list.append(array[4,0])
#
#            with open('Results_{:}/Pore_24_{:}/TR_SHELLS/TR_24_{:}_{:}_shell.dat'.format(system, cell_size, T,S), 'r') as f:
#               shell0 = np.genfromtxt(f, max_rows=1, dtype=float)
#            shell_1_list.append(np.mean(shell0))
#            cell_size_list.append(cell_size)
#            color_list.append(color[index])
#
##    ax.plot(T_list, A_list, color=color_list[0], label='{:} atoms'.format(cell_size))
#    ax.scatter(T_list, shell_1_list, color=color_list, label='{:} atoms'.format(cell_size))
#
#    ax.set_xlabel('log$_{10}$(T)')
#    ax.set_ylabel('Mean ring size of first shell')
#    ax.set_xscale('log')
#    plt.legend()
#    plt.show()
#
#
#
#
#fig, ax = plt.subplots()
#
#for cell_size in [140, 228, 332, 452, 588, 740]:
#    index = [140, 228, 332, 452, 588, 740].index(cell_size)
#    fig, ax = plt.subplots()
#
#
#    T_list = []
#    A_list = []
#    shell_1_list = []
#    cell_size_list = []
#    color_list = []
#
#    for T in range(1000,3001,100):
#        for S in range(0,5,1):
#            print(cell_size, T, S)
#            with open('Results_{:}/Pore_24_{:}/TR_rings/TR_24_{:}_{:}_rings.dat'.format(system, cell_size, T,S), 'r') as f:
#               array = np.genfromtxt(f, dtype=float)
#            T_list.append(10**(-T/1000))
#            if system=='TR':
#                A_list.append(array[4,0]/r0**2)
#            else:
#                A_list.append(array[4,0])
#
#            with open('Results_{:}/Pore_24_{:}/TR_SHELLS/TR_24_{:}_{:}_shell.dat'.format(system, cell_size, T,S), 'r') as f:
#               shell0 = np.genfromtxt(f, max_rows=1, dtype=float)
#            shell_1_list.append(np.mean(shell0))
#            cell_size_list.append(cell_size)
#            color_list.append(color[index])
#
#    ax.scatter(shell_1_list, A_list, color=color_list, label='{:} atoms'.format(cell_size))
#
#    #ax.set_xscale('log')
#    ax.set_xlabel('Mean Ring size in first shell')
#    ax.set_ylabel('Pore area')
#    
#    plt.legend()
#    plt.show()



fig, ax = plt.subplots()

for system in ['TR', 'C']:

    cell_size_list = []
    A_list = []
color = ['r', 'b']


for T in range(1000,3001,500):

    fig, ax = plt.subplots()

    TR_cell_size_list = []
    TR_A_list = []
    C_cell_size_list = []
    C_A_list = []


    for S in range(0,5,1):

#        TR_cell_size_list = []
#        TR_A_list = []
#        C_cell_size_list = []
#        C_A_list = []

        for cell_size in [140, 228, 332, 452, 588, 740]:
            index = [140, 228, 332, 452, 588, 740].index(cell_size)
            system = 'TR'
            with open('../../Results_{:}/Pore_24_{:}/TR_rings/TR_24_{:}_{:}_rings.dat'.format(system, cell_size, T,S), 'r') as f:
               array = np.genfromtxt(f, dtype=float)
            T_list.append(10**(-T/1000))
            if system=='TR':
                A= array[4,0]/r0**2
            else:
                A = array[4,0]

            with open('../../Results_{:}/Pore_24_{:}/TR_SHELLS/TR_24_{:}_{:}_shell.dat'.format(system, cell_size, T,S), 'r') as f:
               shell0 = np.genfromtxt(f, max_rows=1, dtype=float)
            TR_cell_size_list.append(cell_size)
            TR_A_list.append(A)
            system = 'C'
            with open('../../Results_{:}/Pore_24_{:}/TR_rings/TR_24_{:}_{:}_rings.dat'.format(system, cell_size, T,S), 'r') as f:
               array = np.genfromtxt(f, dtype=float)
            T_list.append(10**(-T/1000))
            if system=='TR':
                A = array[4,0]/r0**2
            else:
                A = array[4,0]

            with open('../../Results_{:}/Pore_24_{:}/TR_SHELLS/TR_24_{:}_{:}_shell.dat'.format(system, cell_size, T,S), 'r') as f:
               shell0 = np.genfromtxt(f, max_rows=1, dtype=float)
            C_cell_size_list.append(cell_size)
            C_A_list.append(A)

#        ax.scatter(TR_cell_size_list, TR_A_list, label='TR', color='r')
#        ax.scatter(C_cell_size_list, C_A_list, label='C', color='b')
    ax.scatter(TR_cell_size_list, [C_A_list[i]/TR_A_list[i] for i in range(len(C_A_list))], label='T={:}'.format(T))



#            ax.scatter(cell_size_list, A_list, label='{:}'.format(system), color=color_list)
    ax.set_xlabel('Number of atoms in simulation')
    ax.set_ylabel('Pore Area')
    #ax.set_xscale('log')
    plt.legend()
    plt.show()





