import numpy as np
import matplotlib.pyplot as plt
import time
import networkx as nx


from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Normalize
import matplotlib.pylab as pylab
import time

colormap_turquoise = cm.get_cmap("GnBu")
colormap_greens = cm.get_cmap("Greens")
colormap_blues = cm.get_cmap("Blues")
colormap_greys = cm.get_cmap("Greys")
colormap_reds = cm.get_cmap("Reds")
colormap_oranges = cm.get_cmap("YlOrBr")
colormap_purples = cm.get_cmap("PuRd")
colormap_pinks = cm.get_cmap("RdPu")

turquoise = colormap_turquoise(140)
green = colormap_greens(100)
blue = colormap_blues(150)
grey = colormap_greys(90)
red = colormap_reds(105)
orange = colormap_oranges(100)
purple = colormap_purples(100)
pink = colormap_pinks(80)

ring_colours = []
for i in range(3):
    ring_colours.append("white")
ring_colours.append(turquoise)
ring_colours.append(green)
ring_colours.append(blue)
ring_colours.append(grey)
ring_colours.append(red)
ring_colours.append(orange)
ring_colours.append(purple)
ring_colours.append(pink)
for i in range(40):
    ring_colours.append("black")

folder_name = 'Many_Atom_Test3'
file_name = 'test'
file_type = 'Si2O3'

#folder_name = '3200_atom_2000'
#file_name = 'test'
#folder_name = 'Imported'
#file_name = 'testA'
with open(folder_name+'/'+file_name+'_'+file_type+'_aux.dat', 'r') as f:
    natoms = np.genfromtxt(f, max_rows=1)
    natoms = int(natoms)
if file_type=='Si' or file_type=='C':
    natoms = natoms
elif file_type == 'Si2O3':
    natoms = int(natoms*2/5)
elif file_type == 'SiO2':
    natoms = int(natoms/6)

with open(folder_name+'/'+file_name+'_'+file_type+'_aux.dat',  'r') as f:
    pb = np.genfromtxt(f, skip_header=3, max_rows=1)
with open(folder_name+'/'+file_name+'_A_aux.dat',  'r') as f:
    pbA = np.genfromtxt(f, skip_header=3, max_rows=1)


with open(folder_name+'/'+file_name+'_'+file_type+'_crds.dat', 'r') as f:
    A_crds = np.genfromtxt(f, max_rows=natoms)
with open(folder_name+'/'+file_name+'_A_net.dat', 'r') as f:
    A_net = np.genfromtxt(f, dtype=int)
with open(folder_name+'/'+file_name+'_A_dual.dat', 'r') as f:
    A_dual = np.genfromtxt(f, dtype=int)

nodes = {}
#nNodes = A_crds.shape[0]
nNodes = natoms

print("********************************************* ", nNodes, "*****************************************************")

for i in range(nNodes):
    nodes['{:}'.format(i)] = {}
    nodes['{:}'.format(i)]['crds']  = A_crds[i,:]
    nodes['{:}'.format(i)]['net']   = A_net[i,:]
    nodes['{:}'.format(i)]['dual']  = A_dual[i,:]



#time.sleep(100)


dual = {}

with open(folder_name+'/'+file_name+'_B_crds.dat', 'r') as f:
    B_crds = np.genfromtxt(f)

B_crds = np.multiply(B_crds, pb[0]/pbA[0])

dual = {}
nDual = B_crds.shape[0]

for i in range(nDual):
    dual['{:}'.format(i)] = {}
    dual['{:}'.format(i)]['crds']   = B_crds[i, :]


with open(folder_name+'/'+file_name+'_B_net.dat', 'r') as f:
    
    count=0
    while True:
        line = f.readline()
        if not line:
            break
        v = np.asarray(line.strip().split())
        v = [int(i) for i in v]
        dual['{:}'.format(count)]['net'] = v
        count +=1 
#    B_net = np.genfromtxt(f)

with open(folder_name+'/'+file_name+'_B_dual.dat', 'r') as f:
    count=0
    while True:
        line = f.readline()
        if not line:
            break
        v = np.asarray(line.strip().split())
        v = [int(i) for i in v]
        dual['{:}'.format(count)]['dual'] = v
        count += 1
#    B_dual = np.genfromtxt(f)


def ordered_cnxs(dual_dict, node_dict):
    for ring in dual_dict.keys():
        print(ring)
        cnxs_list = dual_dict[ring]['dual']
        if not isinstance(cnxs_list, list):
            cnxs_list = cnxs_list.tolist()
        new_cnxs_list = []
        new_crd_list = []
        new_cnxs_list.append(cnxs_list[0])
        new_crd_list.append(node_dict['{:}'.format(cnxs_list[0])]['crds'])
        i = 0
        added = False
        print(len(cnxs_list))
        while i < len(cnxs_list)-1:
            print(i)
            node0 = new_cnxs_list[i]
            print(new_cnxs_list)
            connected_to_0 = node_dict['{:}'.format(node0)]['net'].tolist()
            print(connected_to_0)


            options = set(connected_to_0).intersection(cnxs_list)
            print(options)
            for val in new_cnxs_list:
                if val in options:
                    options.remove(val)
            print(options)
            options = list(options)
            new_cnxs_list.append(options[0])
            new_crd_list.append(node_dict['{:}'.format(options[0])]['crds'])
            i+=1

#            time.sleep(100)
#
#            for node1 in cnxs_list:
#                print(node1)
#                if node1 in connected_to_0 and node1 not in new_cnxs_list and added == False:
#                    new_cnxs_list.append(node1)
#                    i += 1
#                    added = True

        area = 0
        for i in range(len(cnxs_list)):
            x0, y0, x1, y1 = new_crd_list[i - 1][0], new_crd_list[i - 1][1], new_crd_list[i][0], new_crd_list[i][1]
            area += (x0 * y1 - x1 * y0)
        if area > 0:
            new_cnxs_list.reverse()
        dual_dict[ring]['dual'] = new_cnxs_list
    return
print('97')
ordered_cnxs(dual, nodes)
print('99')
broken_nodes = []
def check_A():
    for node in nodes.keys():
        for net in [int(i) for i in nodes[node]['net']]:
            #print(node, net)
            if int(node) in [int(i) for i in nodes.keys()] and int(net) in [int(i) for i in nodes.keys()]:
                #print([int(i) for i in self.nodesA[node]['net']],[int(i) for i in self.nodesA['{:}'.format(int(net))]['net']])
                skip = 0
            else:
                print('UNAVALIABLE NODES !! ')
                if int(node) in [int(i) for i in nodes.keys()]: print(node, [int(i) for i in nodes[node]['net']])
                if int(net)  in [int(i) for i in nodes.keys()]: print(net,  [int(i) for i in nodes[net]['net']])

                if int(node) not in [int(i) for i in nodes.keys()]: print(node)
                if int(net)  not in [int(i) for i in nodes.keys()]: print(net)
            if int(node) not in [int(i) for i in nodes['{:}'.format(int(net))]['net']]:
                print('########################################')
                print(node)
                print(nodes['{:}'.format(int(node))]['net'])
                print(net)
                print(nodes['{:}'.format(int(net))]['net'])
                print('Broken Node-Node')
                broken_nodes.append(node)
                broken_nodes.append(net)
#                time.sleep(100)
    for node in nodes.keys():
        for ring in nodes[node]['dual']:
            #print(dual['{:}'.format(int(ring))]['dual'])
            if int(node) not in dual['{:}'.format(int(ring))]['dual']:
                print('Broken Node-Dual')

check_A()


#fig, (ax1,ax2)  = plt.subplots(1,2) 

def import_Nodes():
#    nNodes = A_crds.shape[0]
    Nodes = nx.Graph()
#    nodes = {}

#    nDual = B_crds.shape[0]
    Dual  = nx.Graph()
#    dual = {}

#    for i in range(nNodes):
#        nodes['{:}'.format(i)] = {}
#        nodes['{:}'.format(i)]['crds']  = A_crds[i,:]
#        nodes['{:}'.format(i)]['net']   = A_net[i,:]
#        nodes['{:}'.format(i)]['dual']  = A_dual[i,:]
#    for i in range(nDual):
#        dual['{:}'.format(i)] = {}
#        dual['{:}'.format(i)]['crds']   = B_crds[i, :]
#        dual['{:}'.format(i)]['net']    = B_net[i, :]
#        dual['{:}'.format(i)]['dual']   = B_dual[i, :]



    for i in range(nNodes):
        Nodes.add_node('{:}'.format(i), pos=A_crds[i,:])
    for i in range(nNodes):
        for j in nodes['{:}'.format(i)]['net']:
            Nodes.add_edge('{:}'.format(i),'{:}'.format(j))

    for i in range(nDual):
        Dual.add_node('{:}'.format(i), pos=B_crds[i,:])
    for i in range(nDual):
        for j in dual['{:}'.format(i)]['net']:
            Dual.add_edge('{:}'.format(i),'{:}'.format(j))

    return Nodes, Dual


Nodes, Dual = import_Nodes()

plt.scatter([A_crds[i,0] for i in range(A_crds.shape[0])], [A_crds[i,1] for i in range(A_crds.shape[0])], color='b')
for i in broken_nodes:
    plt.text(A_crds[int(i),0], A_crds[int(i),1], '{:}'.format(int(i)), fontsize=8)

plt.scatter([B_crds[i,0] for i in range(B_crds.shape[0])], [B_crds[i,1] for i in range(B_crds.shape[0])], color='g')

for node0 in range(nNodes):
    for node1 in nodes['{:}'.format(node0)]['net']:
#        if node0<node1:
            crd0, crd1 = nodes['{:}'.format(node0)]['crds'], nodes['{:}'.format(node1)]['crds']
            x0,y0 = crd0[0], crd0[1]
            x1,y1 = crd1[0], crd1[1]
            dx = x1-x0
            dy = y1-y0
            if abs(dx) < 20 and abs(dy) < 20:
                plt.plot([x0,x1], [y0,y1], color='b', alpha=0.5)

plt.show()
print('plotting 2')

#####    for ring0 in range(nDual):
#####        for ring1 in dual['{:}'.format(ring0)]['net']:
#####    #        if ring0<ring1:
#####                crd0, crd1 = dual['{:}'.format(ring0)]['crds'], dual['{:}'.format(ring1)]['crds']
#####                x0,y0 = crd0[0], crd0[1]
#####                x1,y1 = crd1[0], crd1[1]
#####                dx = x1-x0
#####                dy = y1-y0
#####                if abs(dx) < 20 and abs(dy) < 20:
#####                    plt.plot([x0,x1], [y0,y1], color='g', alpha=0.5)
#####    plt.show()
#####    print('plotting 3')
#####    for node0 in range(nNodes):
#####        for ring1 in nodes['{:}'.format(node0)]['dual']:
#####            crd0, crd1 = nodes['{:}'.format(node0)]['crds'], dual['{:}'.format(ring1)]['crds']
#####            x0,y0 = crd0[0], crd0[1]
#####            x1,y1 = crd1[0], crd1[1]
#####            dx = x1-x0
#####            dy = y1-y0
#####            if abs(dx) < 20 and abs(dy) < 20:
#####                plt.plot([x0,x1], [y0,y1], color='y', alpha=0.5, linestyle='dashed')
#####
#####    for ring0 in range(nDual):
#####        for node1 in dual['{:}'.format(ring0)]['dual']:
#####            crd0, crd1 = dual['{:}'.format(ring0)]['crds'], nodes['{:}'.format(node1)]['crds']
#####            x0,y0 = crd0[0], crd0[1]
#####            x1,y1 = crd1[0], crd1[1]
#####            dx = x1-x0
#####            dy = y1-y0
#####            if abs(dx) < 20 and abs(dy) < 20:
#####                plt.plot([x0,x1], [y0,y1], color='orange', alpha=0.5, linestyle='dotted')
#####
#####    plt.show()
fig = plt.figure()
ax = fig.add_subplot(111)
lw=0.5
alpha=1.0
zorder=1
patches = []
plotting_ring_colours = []

for ring0 in range(nDual):
    ring = dual['{:}'.format(ring0)]['dual']
    ring_crds = []
    ring_crds.append(nodes['{:}'.format(ring[0])]['crds'][:2])

    for i in range(1,len(ring)):
        print(ring[i-1], ring[i])

        crd0, crd1 = ring_crds[i-1], nodes['{:}'.format(ring[i])]['crds']
        x0,y0 = crd0[0], crd0[1]
        x1,y1 = crd1[0], crd1[1]
        dx = x1-x0
        dy = y1-y0
        if dx>pb[0]/2:
            dx -= pb[0]
        elif dx<-pb[0]/2:
            dx += pb[0]
        if dy>pb[1]/2:
            dy -= pb[1]
        elif dy<-pb[1]/2:
            dy += pb[1]
        ring_crds.append(np.array([x0+dx, y0+dy]))
#        if abs(dx) < 20 and abs(dy) < 20:
#            plt.plot([x0,x1], [y0,y1], alpha=0.5)
    print(ring_crds)
    ring_crds = np.array(ring_crds)
    for x in range(0, 2):
        for y in range(0, 2):
            new_ring_crds = ring_crds.copy()
            print(x, y, ring_crds[0, 0], ring_crds[0, 1])
            for i in range(ring_crds.shape[0]):
                new_ring_crds[i,0] += x*pb[0]
                new_ring_crds[i,1] += y*pb[1]
#            print(ring_crds)

            patches.append(Polygon(new_ring_crds, True))
            plotting_ring_colours.append(ring_colours[len(new_ring_crds)])

ax.add_collection(
    PatchCollection(
        patches,
        facecolor=plotting_ring_colours,
        edgecolor="k",
        linewidths=lw,
        alpha=alpha,
        zorder=zorder,
    )
)

with open(folder_name+'/'+file_name+'_'+file_type+'_crds.dat', 'r') as f:
   o_crds = np.genfromtxt(f, skip_header=natoms)
plt.scatter(o_crds[:,0], o_crds[:,1], color='r', s=0.5)



ax.set_xlim(-pb[0] * 0.5, pb[0] * 2.5)
ax.set_ylim(-pb[1] * 0.5, pb[1] * 2.5)
plt.show()

for node0 in range(nNodes):
    node_dual = nodes['{:}'.format(node0)]['dual']
    for i in range(len(node_dual)):
        #print(ring[i-1], ring[i])

        crd0, crd1 = dual['{:}'.format(node_dual[i-1])]['crds'], dual['{:}'.format(node_dual[i])]['crds']
        x0,y0 = crd0[0], crd0[1]
        x1,y1 = crd1[0], crd1[  1]
        dx = x1-x0
        dy = y1-y0
        if abs(dx) < 20 and abs(dy) < 20:
            plt.plot([x0,x1], [y0,y1], alpha=0.5)
plt.show()


def refresh(ax):
#        Nodes, Dual = update_Nodes(self)
   node_pos = nx.get_node_attributes(Nodes, 'pos')
   ring_pos = nx.get_node_attributes(Dual, 'pos')

   plt.scatter([node_pos[node][0] for node in node_pos], [node_pos[node][1] for node in node_pos], color='b')
   plt.scatter([ring_pos[ring][0] for ring in ring_pos], [ring_pos[ring][1] for ring in ring_pos], color='g')


   for node in Nodes:
       edges = Nodes.edges(node)
       for edge0, edge1 in edges:
           edge0, edge1 = int(float(edge0)), int(float(edge1))
           if edge0 < edge1 and '{:}'.format(edge0) in Nodes.nodes and '{:}'.format(edge1) in Nodes.nodes:
               crd0, crd1 =  (node_pos['{:}'.format(edge0)][0], node_pos['{:}'.format(edge0)][1]), \
                             (node_pos['{:}'.format(edge1)][0], node_pos['{:}'.format(edge1)][1])


               (x0,y0) = crd0
               (x1,y1) = crd1
               dx = x1-x0
               dy = y1-y0
               if abs(dx) < 10 and abs(dy) < 10:
                   ax.plot([x0,x1], [y0,y1], color='b', alpha=0.5)


   for ring in Dual:
       edges = Dual.edges(ring)
       for edge0, edge1 in edges:
           edge0, edge1 = int(float(edge0)), int(float(edge1))
           if edge0 < edge1:

               crd0, crd1 =  (ring_pos['{:}'.format(edge0)][0], ring_pos['{:}'.format(edge0)][1]), \
                             (ring_pos['{:}'.format(edge1)][0], ring_pos['{:}'.format(edge1)][1])


               (x0,y0) = crd0 
               (x1,y1) = crd1 
               dx = x1-x0
               dy = y1-y0
               if abs(dx) < 10 and abs(dy) < 10:
                   ax.plot([x0,x1], [y0,y1], color='g', alpha=0.5)
   plt.show()
#refresh()
