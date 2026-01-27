import numpy as np
import matplotlib.pyplot as plt
import time
import networkx as nx
import os
import subprocess
import re, yaml
try:
    from yaml import CSafeLoader as Loader
except ImportError:
    from yaml import SafeLoader as Loader



from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Normalize
import matplotlib.pylab as pylab
import time

######################## Passing Arg from postprocess.sh ###############################################
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--steps", type=int, required=True)
args = parser.parse_args()

steps = args.steps

########################################################################################################



shell_count = 5
home = os.getcwd()
colormap_turquoise = cm.get_cmap("GnBu")
colormap_greens = cm.get_cmap("Greens")
colormap_blues = cm.get_cmap("Blues")
colormap_greys = cm.get_cmap("Greys")
colormap_reds = cm.get_cmap("Reds")
colormap_oranges = cm.get_cmap("YlOrBr")
colormap_purples = cm.get_cmap("PuRd")
colormap_pinks = cm.get_cmap("RdPu")

colormap_1 = cm.get_cmap("Purples")
colormap_2 = cm.get_cmap("BuPu")


turquoise = colormap_turquoise(140)
green = colormap_greens(100)
blue = colormap_blues(150)
grey = colormap_greys(90)
red = colormap_reds(105)
orange = colormap_oranges(100)
purple = colormap_purples(100)
pink = colormap_pinks(80)

purple1 = colormap_1(100)
purple2 = colormap_2(100)

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
ring_colours.append(purple1)
ring_colours.append(purple2)
for i in range(40):
    ring_colours.append("black")

#plt.scatter([i for i in range(20)], [i for i in range(20)], color=[ring_colours[i] for i in range(20)])
#plt.show()
r_sisi = 2.86667626014*2
r_cc = 1.0
for T in range(1000,5001,100):


    for S in range(0,106,1):
        folder = 'T_-{:}/S_{:}/{:}/'.format(T, S, steps)
        folder_name = folder+'Run'
        
        if not os.path.isdir(folder_name):
            continue
        
        if os.path.isfile(folder_name + '/Q_TR_engtot.out'):
            print(f"Skipping {folder_name}, energy already calculated.")
            continue

        print(os.listdir(folder_name))

        file_name = 'test'
        file_type = 'Si2O3'
 
        if os.path.isfile(folder_name+'/'+file_name+'_'+file_type+'_aux.dat')==True: 
            
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
            #    plt.scatter(x, y)
            #    plt.scatter(np.mean(x), np.mean(y))
            #    plt.show()
                com_v = np.array([np.mean(x), np.mean(y)])
                if com_v[0]>pb[0]: com_v[0] -=pb[0]
                if com_v[0]<0: com_v[0] +=pb[0]
                if com_v[1]>pb[1]: com_v[1] -=pb[1]
                if com_v[1]<0: com_v[1] +=pb[1]

                return com_v
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
           #    plt.scatter(x, y)
           #    plt.scatter(np.mean(x), np.mean(y))
           #    plt.show()
               ring_crds = np.vstack((np.asarray(x), np.asarray(y))).T
               return ring_crds
            
            dual = {}
            nDual = B_crds.shape[0]
            
            for i in range(nDual):
                dual['{:}'.format(i)] = {}
#                dual['{:}'.format(i)]['crds']   = B_crds[i, :]
            
            
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
            with open(folder_name+'/fixed_rings.dat', 'r') as f:
                array = np.genfromtxt(f)
            
            with open(folder_name+'/'+file_name+'_B_crds.dat', 'w') as f:
                for i in range(B_crds.shape[0]):
                    f.write('{:<26}{:<26}\n'.format(B_crds[i,0], B_crds[i,1]))
            with open(folder_name+'/PARM_Q_TR.lammps', 'w') as f:
                f.write('dielectric {:}\n'.format(1/r_sisi))
                f.write('pair_style coul/cut {:}\n'.format(5*r_sisi))

                f.write('pair_coeff * *\n')
            with open(folder_name +'/Q_TR.data', 'w') as f:
                f.write('DATA FILE Produced from netmc results (cf David Morley)\n')
                f.write('{:} atoms\n'.format(B_crds.shape[0]))
                f.write('0 bonds\n')#+charge_array.shape[0]))
                f.write('0 angles\n')
                f.write('0 dihedrals\n')
                f.write('0 impropers\n')
                f.write('10 atom types\n')
#                f.write('3 bond types\n')
                f.write('0 bond types\n')
                f.write('0 angle types\n')
                f.write('0 dihedral types\n')
                f.write('0 improper types\n')
                f.write('0.00000 {:<5} xlo xhi\n'.format(pb[0]))
                f.write('0.00000 {:<5} ylo yhi\n'.format(pb[1]))
                f.write(' Masses\n')
                f.write('\n')
                for i in range(1,11):
                   f.write('{:} 1 # Charged_{:}\n'.format(i, i))
                f.write('\n')
                f.write(' Atoms # full\n\n')
                for i in range(B_crds.shape[0]):
                    if i in array[1:]:
                        f.write('{:<4} {:<4} {:<4} {:<24} {:<24} {:<24} {:<24}# N\n'.format(int(i + 1), int(i+1), 10, len(dual['{:}'.format(i)]['net'])-6,
                                                                                       B_crds[i, 0],
                                                                                       B_crds[i, 1], 0.0))

                    else:
                        f.write('{:<4} {:<4} {:<4} {:<24} {:<24} {:<24} {:<24}# N\n'.format(int(i + 1), int(i+1), len(dual['{:}'.format(i)]['net'])-3, len(dual['{:}'.format(i)]['net'])-6,
                                                                                       B_crds[i, 0],
                                                                                       B_crds[i, 1], 0.0))

            with open(folder_name+'/Q_TR.in', 'w') as f:
    
                f.write('log Q_TR.log\n')
                f.write('units                   electron                                                   \n')
                f.write('dimension               2                                                          \n')
                f.write('processors              * * *                                                        \n')
                f.write('boundary                p p p                                                      \n')
                f.write('\n')
                f.write('#####################################################################              \n')
                f.write('\n')
                f.write('variable time equal 25*0.02418884326                                               \n')
                f.write('\n')
                f.write('#####################################################################              \n')
                f.write('\n')
                f.write('#read data\n')
                f.write('atom_style              full                                                  \n')
                f.write('read_data               Q_TR.data                                                  \n')
                f.write('timestep ${time}                                                                   \n')
                f.write('\n')
                f.write('#####################################################################              \n')
                f.write('\n')
                f.write('#potential                                                                         \n')
                f.write('include                 PARM_Q_TR.lammps                                                \n')
                f.write('\n')
                #        f.write('#####################################################################              \n')
                #        f.write('\n')
                #        f.write('pair_write 1 1 50 r 2.0 6.0 OO_pair.dat OO_Pair                                    \n')
                #        f.write('pair_write 2 2 50 r 2.0 6.0 SiSi_pair.dat SiSi_Pair                                \n')
                #        f.write('bond_write 1 50 2.0 6.0 OO_bond.dat OO_bond                                        \n')
                #        f.write('bond_write 2 50 2.0 6.0 SiSi_bond.dat SiSi_bond                                    \n')
                #        f.write('\n')
                f.write('#####################################################################              \n')
                f.write('\n')
                f.write('#outputs                                                                           \n')
                f.write('thermo                  0                                                       \n')
                f.write('thermo_style            custom step pe ke epair ebond etotal vol temp              \n')
                f.write('\n')
                f.write('#####################################################################              \n')
                f.write('\n')
                f.write('dump 1 all custom 1 forces.dat id fx fy fz\n')
                f.write('thermo_modify           line yaml                                                  \n')
                f.write('\n')
                f.write('#####################################################################              \n')
                f.write('\n')
                f.write('fix 1 all nvt temp 0.00000001 0.0000001 $(100.0*dt)\n')
                f.write('run 0')

                f.write('\n')
        #        f.write('#####################################################################              \n')

            


            os.chdir(folder_name)
            subprocess.call(['/u/mw/shug7609/lammps-2025/build/lmp', '-in', 'Q_TR.in'])
             
            docs = ""
            with open("Q_TR.log", 'r') as f:
                for line in f:
                    m = re.search(r"^(keywords:.*$|data:$|---$|\.\.\.$|  - \[.*\]$)", line)
                    if m: docs += m.group(0) + '\n'
            
            thermo = list(yaml.load_all(docs, Loader=Loader))
            
            #print("Number of runs: ", len(thermo))
            
            for i in range(len(thermo)):
                if i==0:
                    data = np.asarray(thermo[0]['data'])
                else:
                    data = np.vstack((data, np.asarray(thermo[i]['data'])))
            
            engtot_array = data
            
            with open('Q_TR_engtot.out', 'w') as f:
            
                for i in range(engtot_array.shape[0]):
                    f.write('    {:<15}{:<15}{:<15}\n'.format(int(engtot_array[i,0]), 0.000, engtot_array[i,5]))


#            with open('forces.dat', 'r') as f:
#                array_f = np.genfromtxt(f, skip_header=9) 
#            r_list, f_list, crd_list = [], [], []
#
#            for atom in range(array_f.shape[0]):
#                ref = int(array_f[atom,0]-1)
#                v = np.subtract(B_crds[0,:], B_crds[ref,:])
#                r = np.linalg.norm(v)
#                norm_v = np.divide(v,r)
#                f = np.dot(norm_v, array_f[atom,1:3])
#                r_list.append(r)
#                f_list.append(f)
#                crd_list.append(B_crds[ref,:])
#                plt.arrow(B_crds[ref,0], B_crds[ref,1], 10*array_f[atom, 1], 10*array_f[atom,2], head_width=1.0)
#                plt.scatter(B_crds[ref,0], B_crds[ref,1])
#            plt.show()
#            norm = Normalize(-1,1)
#            cmap = cm.get_cmap('viridis')
#
#            for atom in range(len(crd_list)):
#                arrow = np.multiply(np.divide(np.subtract(B_crds[0,:], crd_list[atom]), np.linalg.norm(np.subtract(B_crds[0,:], crd_list[atom]))), f_list[atom]*10)
#                plt.arrow(crd_list[atom][0], crd_list[atom][1], arrow[0], arrow[1], head_width=1.0)
#                plt.scatter(crd_list[atom][0], crd_list[atom][1])
#            plt.show()
#
#            plt.scatter([crd_list[i][0] for i in range(len(crd_list))], [crd_list[i][1] for i in range(len(crd_list))], color=cmap(norm(f_list))) 
#            plt.show()
#            plt.scatter(r_list, f_list)
#            plt.show()

            os.chdir(home)

            for i in range(nDual):
                dual['{:}'.format(i)]['crds']   = B_crds[i, :]



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

