import numpy as np
import matplotlib.pyplot as plt
import time
import networkx as nx
import os
import scipy
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Normalize
import matplotlib.pylab as pylab
import time


# added
import math
import csv
from collections import defaultdict


######################## Passing Arg from postprocess.sh ###############################################
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--steps", type=int, required=True)
args = parser.parse_args()

steps = args.steps

########################################################################################################




shell_count = 2


colormap_greens = cm.get_cmap("Greens")
colormap_blues = cm.get_cmap("Blues")
colormap_greys = cm.get_cmap("Greys")
colormap_reds = cm.get_cmap("Reds")
colormap_oranges = cm.get_cmap("YlOrBr")
colormap_purples = cm.get_cmap("PuRd")
colormap_pinks = cm.get_cmap("RdPu")

colormap_1 = cm.get_cmap("Purples")
colormap_2 = cm.get_cmap("BuPu")


#turquoise = colormap_turquoise(140)
#green = colormap_greens(100)
#blue = colormap_blues(150)
#grey = colormap_greys(90)
#red = colormap_reds(105)
#orange = colormap_oranges(100)
#purple = colormap_purples(100)
#pink = colormap_pinks(80)

#purple1 = colormap_1(100)
#purple2 = colormap_2(100)

#ring_colours = []
#for i in range(3):
#    ring_colours.append("white")
#ring_colours.append(turquoise)
#ring_colours.append(green)
#ring_colours.append(blue)
#ring_colours.append(grey)
#ring_colours.append(red)
#ring_colours.append(orange)
#ring_colours.append(purple)
#ring_colours.append(pink)
#ring_colours.append(purple1)
#ring_colours.append(purple2)
#for i in range(40):
#    ring_colours.append("black")


def Eutaxy(A):
    n = A.shape[0]
    S = np.dot(A.T, A)
    TrS = np.trace(S)
    SS = np.dot(S, S)
    TrSS = np.trace(SS)
    return TrS/(np.sqrt(TrSS)*np.sqrt(n))

    

def Hull_Stats(A, area, perimeter):

    # hull
    hull = scipy.spatial.ConvexHull(A)
    # hull_area
    hull_area = hull.volume
    # hull perimeter
    hull_perimeter = hull.area
    # hull balance_repartition
    balance_repartition = np.sqrt(min([np.std(A[:,0]), np.std(A[:,1])])/max([np.std(A[:,0]), np.std(A[:,1])]))

    solidity = area/hull_area
    convexity = hull_perimeter/perimeter
    SRC = solidity * balance_repartition * convexity
    return SRC


for T in range(1000,5001, 100):


    for S in range(0,100,1):
        folder = 'T_-{:}/S_{:}/{:}/'.format(T, S, steps)
        folder_name = folder+'Run'
        file_name = 'test'
        file_type = 'Si2O3'
        

        # skip systems which have already been calculated
        if os.path.exists('TR_theta/results_{:}_{:}_theta.out'.format(T,S)):
            print("skipping")
            continue

        if os.path.isfile(folder_name+'/'+file_name+'_'+file_type+'_aux.dat')==True: 

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
            
            
            
            dual = {}
            
            with open(folder_name+'/'+file_name+'_B_crds.dat', 'r') as f:
                B_crds = np.genfromtxt(f)
            
            B_crds = np.multiply(B_crds, pb[0]/pbA[0])

            def com(i):
                x = []
                y = []
                for node in dual['{:}'.format(i)]['dual']:
                    if len(x)==0:
                        x.append(A_crds[node,0])
                        y.append(A_crds[node,1])
                    else:
                        x0, y0 = x[-1], y[-1]
                        x1, y1 = A_crds[node,0], A_crds[node,1]
                        if x0 - x1 > pb[0]/2:
                            x1 +=pb[0]
                        elif x0 - x1 < -pb[0]/2:
                            x1 -=pb[0]
                        if y0 - y1 > pb[1]/2:
                            y1+=pb[1]
                        elif y0 - y1 < -pb[1]/2:
                            y1-=pb[1]
                        x.append(x1)
                        y.append(y1)
                return np.array([np.mean(x), np.mean(y)])
            def local_ring(i):
               x = []
               y = []
               for node in dual['{:}'.format(i)]['dual']:
                   if len(x)==0:
                       x.append(A_crds[node,0])
                       y.append(A_crds[node,1])
                   else:
                       x0, y0 = x[-1], y[-1]
                       x1, y1 = A_crds[node,0], A_crds[node,1]
                       if x0 - x1 > pb[0]/2:
                           x1 +=pb[0]
                       elif x0 - x1 < -pb[0]/2:
                           x1 -=pb[0]
                       if y0 - y1 > pb[1]/2:
                           y1+=pb[1]
                       elif y0 - y1 < -pb[1]/2:
                           y1-=pb[1]
                       x.append(x1)
                       y.append(y1)
               ring_crds = np.vstack((np.asarray(x), np.asarray(y))).T

               area = 0
               for i in range(ring_crds.shape[0]):
                   area += ring_crds[i-1,0]*ring_crds[i,1] - ring_crds[i,0]*ring_crds[i-1,1]
               area = abs(area/2)
               perimeter = 0
               for i in range(ring_crds.shape[0]):
                   perimeter += np.linalg.norm(np.subtract(ring_crds[i-1,:], ring_crds[i,:]))

               r_ideal = (2.86667626014*2)
               n = ring_crds.shape[0]
               area_ideal = (r_ideal**2*n)/(4*np.tan(np.pi/n))
               perimeter_ideal = n*r_ideal

               return ring_crds, area, perimeter
            
            dual = {}
            nDual = B_crds.shape[0]
            
            for i in range(nDual):
                dual['{:}'.format(i)] = {}
            
            
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
            print(dual['69']['net'], 168)
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
#                    print(ring)
                    cnxs_list = dual_dict[ring]['dual']
                    if not isinstance(cnxs_list, list):
                        cnxs_list = cnxs_list.tolist()
                    new_cnxs_list = []
                    new_crd_list = []
                    new_cnxs_list.append(cnxs_list[0])
                    new_crd_list.append(node_dict['{:}'.format(cnxs_list[0])]['crds'])
                    i = 0
                    added = False
#                    print(len(cnxs_list))
                    while i < len(cnxs_list)-1:
#                        print(i)
                        node0 = new_cnxs_list[i]
#                        print(new_cnxs_list)
                        connected_to_0 = node_dict['{:}'.format(node0)]['net'].tolist()
#                        print(connected_to_0)
            
            
                        options = set(connected_to_0).intersection(cnxs_list)
#                        print(options)
                        for val in new_cnxs_list:
                            if val in options:
                                options.remove(val)
#                        print(options)
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

            for i in range(B_crds.shape[0]):
                B_crds[i,:] = com(i)
             
            with open(folder_name+'/'+file_name+'_'+file_type+'_B_crds.dat', 'w') as f:
                for i in range(B_crds.shape[0]):
                    f.write('{:<26}{:<26}\n'.format(B_crds[i,0], B_crds[i,1]))

            for i in range(nDual):
                dual['{:}'.format(i)]['crds']   = B_crds[i, :]
                ring_crds, area, perimeter = local_ring(i)
                dual['{:}'.format(i)]['area']  = area
                dual['{:}'.format(i)]['perimeter']  = perimeter
                dual['{:}'.format(i)]['eutaxy'] = Eutaxy(ring_crds)
                dual['{:}'.format(i)]['SRC'] = Hull_Stats(ring_crds, area, perimeter)




            print(dual['69']['net'], 237)

#            print('97')
            ordered_cnxs(dual, nodes)
#            print('99')
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
            print(dual['69']['net'], 316)

            accounted_for = []
            accounted_for.append(0)
            shell_dict = {}
            shell_dict['-1'] = []
            shell_dict['0'] = [0]
            shell_dict_crds = {}
            shell_dict_crds['-1'] = []
            shell_dict_crds['0'] = [B_crds[0,:]]
            #print(pb)
            r_cut = min(pb)*0.5

            color_list = ['k', 'r', 'g', 'b', 'c', 'y', 'm', 'k', 'r', 'g', 'b', 'c', 'y', 'm']

            
#            fig = plt.figure()
#            ax = fig.add_subplot(111)
#            lw=0.5
#            alpha=1.0
#            zorder=1
#            patches = []
#            plotting_ring_colours = []

 
            for shell in range(1,shell_count+1):
#                fig = plt.figure()
#                ax = fig.add_subplot(111)
#                lw=0.5
#                alpha=1.0
#                zorder=1
#                patches = []
#                plotting_ring_colours = []
            
#                print('SHELL : ', shell)
                shell_dict['{:}'.format(shell)]=[]
                shell_dict_crds['{:}'.format(shell)]=[]
#                print('MEMBERS to check for duplicates ', shell_dict['{:}'.format(shell-1)])
                print('DUPLICATE ', shell-1, len(shell_dict['{:}'.format(shell-1)]) - len(list(set(shell_dict['{:}'.format(shell-1)]))))
                for member_count in range(len(shell_dict['{:}'.format(shell-1)])):
#                for member in shell_dict['{:}'.format(shell-1)]:
                    member = shell_dict['{:}'.format(shell-1)][member_count]                   
#                    index_val = shell_dict['{:}'.format(shell-1)].index(member)
                    old_crd = shell_dict_crds['{:}'.format(shell-1)][member_count]

                    for shell_dual_node in dual['{:}'.format(member)]['net']:
#                        v = np.subtract(B_crds[member,:], B_crds[shell_dual_node,:])
#                        v = np.subtract(old_crd, B_crds[shell_dual_node,:])

#                        r= np.linalg.norm(v)
#                        print(shell, r, r_cut)
            
#####                        if int(shell_dual_node) not in accounted_for and r < r_cut:
#####                            shell_dict['{:}'.format(shell)].append(int(shell_dual_node))
#####                            shell_dict_crds['{:}'.format(shell)].append(B_crds[int(shell_dual_node),:])
#####                            accounted_for.append(int(shell_dual_node))
#####                            offset = np.array([0,0])
#####                            new_ring_crds = np.add(local_ring(shell_dual_node), offset)
#####                            patches.append(Polygon(new_ring_crds, True))
#####                            plotting_ring_colours.append(color_list[shell])

                        
                        for x_offset in range(-5,6):
                            for y_offset in range(-5,6):
                                if x_offset==0 and y_offset==0 and 1<0: print('')
                                else:
                                    new_crd = np.add(B_crds[shell_dual_node,:],np.array([pb[0]*x_offset, pb[1]*y_offset]))
                                    v = np.subtract(old_crd, new_crd)
                                    r = np.linalg.norm(v)
                                    previous_shell_crds = []
                                    for lower_shell in range(0, shell+1):
                                        previous_shell_crds += shell_dict_crds['{:}'.format(lower_shell)]
                                    is_in_list = np.any(np.all(new_crd == previous_shell_crds, axis=1))
                                    if r < r_cut and is_in_list==False:
                                        shell_dict['{:}'.format(shell)].append(int(shell_dual_node))
                                        shell_dict_crds['{:}'.format(shell)].append(new_crd)
                                        offset = np.array([pb[0]*x_offset, pb[1]*y_offset])
            
                                        new_ring_crds = np.add(local_ring(shell_dual_node)[0], offset)
#                                        patches.append(Polygon(new_ring_crds, True))
 #                                       plotting_ring_colours.append(color_list[shell])
#                                        plt.text(new_crd[0], new_crd[1], '{:}'.format(shell_dual_node))


######                        if r > r_cut and int(shell_dual_node) not in [int(i) for i in shell_dict['{:}'.format(shell-1)]]:
######
#######                        elif r > r_cut and int(shell_dual_node):
######
######                            new_crd = B_crds[int(shell_dual_node),:]
##########                            plt.scatter(new_crd[0], new_crd[1], color=color_list[shell])
######
######                            if v[0] > pb[0]/2:
######                                 new_crd = np.add(new_crd, np.array([pb[0],0]))
######                                 print('+x')
######                            elif v[0] < -pb[0]/2:
######                                 new_crd = np.subtract(new_crd, np.array([pb[0],0]))
######                                 print('-x')
######                            if v[1] > pb[1]/2:
######                                 new_crd = np.add(new_crd, np.array([0,pb[1]]))
######                                 print('+y')
######                            elif v[1] < -pb[1]/2:
######                                 new_crd = np.subtract(new_crd, np.array([0,pb[1]]))
######                                 print('-y')
######            
######                            shell_dict['{:}'.format(shell)].append(int(shell_dual_node))
######                            shell_dict_crds['{:}'.format(shell)].append(new_crd)
######                            offset = np.subtract(new_crd, B_crds[int(shell_dual_node),:])
######
######                            new_ring_crds = np.add(local_ring(shell_dual_node), offset)
######                            patches.append(Polygon(new_ring_crds, True))
######                            plotting_ring_colours.append(color_list[shell])
#                ax.add_collection(
#                    PatchCollection(
#                        patches,
#                        facecolor=plotting_ring_colours,
#                        edgecolor="k",
#                        linewidths=lw,
#                        alpha=alpha,
#                        zorder=zorder,
#                    )
#                )
#            ax.set_xlim(-pb[0] * 2.5, pb[0] * 2.5)
#            ax.set_ylim(-pb[1] * 2.5, pb[1] * 2.5)
#
#            plt.show()

            shell_number = []
            mean_ring_sizes = []
            var_ring_sizes = []
            for shell in range(1,shell_count+1):
                shell_number.append(shell)
                
                ring_sizes = [len(dual['{:}'.format(i)]['net']) for i in shell_dict['{:}'.format(shell)]]
                mean_ring_sizes.append(np.mean(ring_sizes))
                var_ring_sizes.append(np.var(ring_sizes))
#            plt.plot(shell_number, mean_ring_sizes, label='{:}_{:}'.format(T,S))
 #   plt.show()#
            if not os.path.isdir('TR_SHELLS'): os.mkdir('TR_SHELLS')
#            with open('TR_SHELLS/results_{:}_{:}_shell.dat'.format(T,S), 'w') as f:
#                for shell in shell_number:
#                    ring_sizes = [len(dual['{:}'.format(i)]['net']) for i in shell_dict['{:}'.format(shell)]]
#                    for j in range(len(ring_sizes)):
#                        f.write('{:} '.format(ring_sizes[j]))
#                    f.write('\n')
#            if not os.path.isdir('TR_r'): os.mkdir('TR_r')
#            with open('TR_r/results_{:}_{:}_r.dat'.format(T,S), 'w') as f:
#                
#                r_list = []
#                q_list = []
#                center = B_crds[0,:]
#                for i in range(0,int(nNodes/2)):
#                    for x_offset in range(-5,6):
#                        for y_offset in range(-5,6):
#                            if i==0 and x_offset==0 and y_offset==0: skip = True
#                            else:
#                                new_crd = np.add(B_crds[i,:],np.array([pb[0]*x_offset, pb[1]*y_offset]))
#                                v = np.subtract(center, new_crd)
#                                r = np.linalg.norm(v)
#                                previous_shell_crds = []
#                                r_list.append(r)
#                                q_list.append(len(dual['{:}'.format(i)]['net']))
#                                                        
#                for i in r_list:
#                    f.write('{:}  '.format(i))
#                f.write('\n')
#                for i in q_list:
#                    f.write('{:}  '.format(i))
            if not os.path.isdir('TR_rings'): os.mkdir('TR_rings')
            #with open('TR_rings/results_{:}_{:}_rings.dat'.format(T,S), 'w') as f:
            #    for i in range(int(nNodes/2)):
            #        f.write('{:} '.format(i))
            #    f.write('\n')
            #    for i in range(int(nNodes/2)):
            #        f.write('{:} '.format(len(dual['{:}'.format(i)]['net'])))
            #    f.write('\n')
#
#                for i in range(int(nNodes/2)):
#                    f.write('{:} '.format(dual['{:}'.format(i)]['eutaxy']))
#                f.write('\n')
#                for i in range(int(nNodes/2)):
#                    f.write('{:} '.format(dual['{:}'.format(i)]['SRC']))
#                f.write('\n')

            #
            # ensure directories exist
            if not os.path.isdir('TR_theta'):
                os.mkdir('TR_theta')

            # center used previously for TR_r
            center = B_crds[0,:]
            nDual = B_crds.shape[0]

            # We'll collect tuples (index, r, theta, q, eutaxy, SRC)
            theta_rows = []


            # Use the same loop limits as TR_r (0 .. nNodes/2 - 1)
            for i in range(0, int(nNodes/2)):
                # iterate periodic images just like you did for r_list in TR_r
                for x_offset in range(-5, 6):
                    for y_offset in range(-5, 6):
                        # skip the center's trivial self-image if you want (kept same logic as TR_r)
                        if i ==0 and x_offset ==0 and y_offset == 0:
                            continue
                        
                        new_crd = B_crds[i,:] + np.array([pb[0]*x_offset, pb[1]*y_offset])
                        v = center - new_crd
                        r = np.linalg.norm(v)
                        # compute angle in radians in range [-pi, pi]
                        theta = math.degrees(math.atan2(new_crd[1] - center[1], new_crd[0] - center[0]))
                        q = len(dual['{:}'.format(i)]['net']) if '{:}'.format(i) in dual else None
                        eut = dual['{:}'.format(i)]['eutaxy'] if '{:}'.format(i) in dual else None
                        src = dual['{:}'.format(i)]['SRC'] if '{:}'.format(i) in dual else None

                        theta_rows.append((i, r, theta, q, eut, src))


            # Write a flat CSV listing all (index, r, theta, q, eutaxy, SRC)
            theta_file = os.path.join('TR_theta', 'results_{:}_{:}_theta.csv'.format(T, S))
            with open(theta_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # header
                writer.writerow(['index', 'r', 'theta_rad', 'q', 'eutaxy', 'SRC'])
                for row in theta_rows:
                    # convert None -> '' for safe CSV writing
                    writer.writerow([row[0], '{:.12f}'.format(row[1]), '{:.12f}'.format(row[2]),
                         '' if row[3] is None else row[3],
                         '' if row[4] is None else '{:.12e}'.format(row[4]),
                         '' if row[5] is None else '{:.12e}'.format(row[5])])

