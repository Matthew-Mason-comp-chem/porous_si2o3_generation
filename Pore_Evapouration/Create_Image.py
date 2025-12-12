import cv2
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import time
import copy
import os
import sys
import shutil
list_x = []
list_y = []

#nodes = {}

node_list = []
node_cnxs = []

########################################################################################################################
#folder_name = 't-2000_s0_same'
folder_name = 'nxn_32x32'
#folder_name = 't-3200_s0_same'
#with open('next_folder.txt', 'w') as f:
#    f.write('{:}'.format('Results_24_3140_544554455445_LJ'))

#with open('next_folder.txt', 'r') as f:
#   folder_name = f.readline()
#folder_name = 'nxn_8x16'
#folder_name = 'nxn_20x20'


#   #folder_name = 'Results_10_704_4444545444544554454555555555454444444444_LJ'
#folder_name = 'Results_10_470_4444455554444444_LJ'
print(folder_name)
if folder_name[-2:]=='\n':
    folder_name = folder_name[:-2]
#folder_name = 't-10000_s0_same'

with open(folder_name+'/test_A_crds.dat', 'r') as f:
    A_crds = np.genfromtxt(f)
with open(folder_name+'/test_A_net.dat', 'r') as f:
    A_net = np.genfromtxt(f)
with open(folder_name+'/test_A_dual.dat', 'r') as f:
    A_dual = np.genfromtxt(f)

with open(folder_name+'/test_A_aux.dat', 'r') as f:
    A_pbc = np.genfromtxt(f, skip_header=3, skip_footer=1)
print('A PBC : ', A_pbc)
print(A_pbc[0], A_pbc[1])
############################################################
#time.sleep(100)
with open(folder_name+'/test_B_crds.dat', 'r') as f:
    B_crds = np.genfromtxt(f)
dual = {}
nDual = B_crds.shape[0]

for i in range(nDual):
    dual['{:}'.format(i)] = {}
    dual['{:}'.format(i)]['crds']   = B_crds[i, :]
with open(folder_name+'/test_B_net.dat', 'r') as f:

    count=0
    while True:
        line = f.readline()
        if not line:
            break
        v = np.asarray(line.strip().split())
        v = [int(i) for i in v]
        dual['{:}'.format(count)]['net'] = np.asarray(v)
        count +=1
#    B_net = np.genfromtxt(f)

with open(folder_name+'/test_B_dual.dat', 'r') as f:
    count=0
    while True:
        line = f.readline()
        if not line:
            break
        v = np.asarray(line.strip().split())
        v = [int(i) for i in v]
        dual['{:}'.format(count)]['dual'] = np.asarray(v)
        count += 1
#    B_dual = np.genfromtxt(f)




#with open(folder_name+'/test_B_crds.dat', 'r') as f:
#    B_crds = np.genfromtxt(f)
#with open(folder_name+'/test_B_net.dat', 'r') as f:
#    B_net = np.genfromtxt(f)
#with open(folder_name+'/test_B_dual.dat', 'r') as f:
#    B_dual = np.genfromtxt(f)
#
########################################################################################################################


def clockwise_cnxs_dual(dual_dict, array):

    cnx_list = array.tolist()

    new_cnx_list = []
    new_crd_list = []

    new_cnx_list.append(cnx_list[0])

    i=0
    added = False
    while i < len(cnx_list):
        ring0 = new_cnx_list[-1]
        connected_to_0 = dual_dict['{:}'.format(ring0)]['net'].tolist()
        new_crd_list.append(dual_dict['{:}'.format(ring0)]['crd'])
        for ring1 in cnx_list:
            if ring1 in connected_to_0 and ring1 not in new_cnx_list and added==False:
                new_cnx_list.append(ring1)
                i+=1
                added=True

    area =0
    for i in range(len(cnx_list)):
        x0, y0, x1, y1 = new_crd_list[i-1][0], new_crd_list[i-1][1], new_crd_list[i][0], new_crd_list[i][1]
        area += (x0*y1-x1*y0)
    if area > 0:
        new_cnx_list.reverse()
    return np.asarray(new_cnx_list)

def ordered_cnxs(dual_dict, node_dict):
    for ring in dual_dict.keys():

        cnxs_list = dual_dict[ring]['dual']
        if not isinstance(cnxs_list, list):
            cnxs_list = cnxs_list.tolist()
        new_cnxs_list = []
        new_crd_list = []
        new_cnxs_list.append(cnxs_list[0])

        i=0
        added = False
        while i < len(cnxs_list):
            node0 = new_cnxs_list[-1]
            connected_to_0 = node_dict['{:}'.format(node0)]['net'].tolist()
            new_crd_list.append(dual_dict['{:}'.format(node0)]['crd'])
            for ring1 in cnxs_list:
                if ring1 in connected_to_0 and ring1 not in new_cnxs_list and added == False:
                    new_cnxs_list.append(ring1)
                    i += 1
                    added = True

        area =0
        for i in range(len(cnxs_list)):
            x0, y0, x1, y1 = new_crd_list[i-1][0], new_crd_list[i-1][1], new_crd_list[i][0], new_crd_list[i][1]
            area += (x0*y1-x1*y0)
        if area > 0:
            new_cnxs_list.reverse()
        dual_dict[ring]['dual'] = new_cnxs_list
    return


########################################################################################################################

def import_Nodes():
    nNodes = A_crds.shape[0]
    Nodes = nx.Graph()
    nodes = {}

    nDual = B_crds.shape[0]
    Dual  = nx.Graph()
#    dual = {}

    for i in range(nNodes):
        nodes['{:}'.format(i)] = {}
        nodes['{:}'.format(i)]['crds']  = A_crds[i,:]
        nodes['{:}'.format(i)]['net']   = A_net[i,:]
        nodes['{:}'.format(i)]['dual']  = A_dual[i,:]
#    for i in range(nDual):
#        dual['{:}'.format(i)] = {}
#        dual['{:}'.format(i)]['crds']   = B_crds[i, :]
#        dual['{:}'.format(i)]['net']    = B_net[i, :]
#        dual['{:}'.format(i)]['dual']   = B_dual[i, :]



    for i in range(nNodes):
        Nodes.add_node('{:}'.format(i), pos=A_crds[i,:])
    for i in range(nNodes):
        for j in range(A_net.shape[1]):
            Nodes.add_edge('{:}'.format(i),'{:}'.format(A_net[i,j]))

    for i in range(nDual):
        Dual.add_node('{:}'.format(i), pos=B_crds[i,:])
    for i in range(nDual):

        for j in range(dual['{:}'.format(i)]['net'].shape[0]):
            Dual.add_edge('{:}'.format(i),'{:}'.format(dual['{:}'.format(i)]['net'][j]))

    return nodes, dual, Nodes, Dual
########################################################################################################################

########################################################################################################################


nodes, dual, Nodes, Dual = import_Nodes()


########################################################################################################################

class DrawLineWidget(object):
    def __init__(self,):
        self.original_image = cv2.imread('bg.png')
        self.clone = self.original_image.copy()
        self.new_ring = 0
        self.folder = "Results"
#
        self.lj=1
        self.rings_to_remove = []
        self.nodes, self.dual, self.Nodes, self.Dual = import_Nodes()
        self.deleted_nodes = []
        self.undercoordinated = []
        self.broken_rings = []
#        print(self.nodes.keys())
        cv2.namedWindow('image')
        cv2.setMouseCallback('image', self.extract_coordinates)

        # List to store start/end points
        self.image_coordinates = []

        #local variables to help recenter
        # dimensions of box = 1700x1000

        self.x_offset = 100
        self.y_offset = 100
        self.scale = int(450/np.sqrt(len(self.dual.keys())))

#        self.x_offset = -7200
#        self.y_offset = -4500
#        self.scale = int(6000/np.sqrt(len(self.dual.keys())))
        self.refresh_new_cnxs([])

    def log_write(self, string, val):
        self.logfile.write(string+str(val)+'\n')
    def check(self):
        print("---checking...")
        for node in self.nodes.keys():
            for net in [int(i) for i in self.nodes[node]['net']]:
                if int(node) in [int(i) for i in self.nodes.keys()] and int(net) in [int(i) for i in self.nodes.keys()]:
                    # print([int(i) for i in self.self.nodesA[node]['net']],[int(i) for i in self.self.nodesA['{:}'.format(int(net))]['net']])
                    skip = 0
                else:
                    print('UNAVALIABLE NODES !! ')
                    if int(node) in [int(i) for i in self.nodes.keys()]: print(node, [int(i) for i in self.nodes[node]['net']])
                    if int(net) in [int(i) for i in self.nodes.keys()]: print(net, [int(i) for i in self.nodes[net]['net']])

                    if int(node) not in [int(i) for i in self.nodes.keys()]: print(node)
                    if int(net) not in [int(i) for i in self.nodes.keys()]: print(net)
                if int(node) not in [int(i) for i in self.nodes['{:}'.format(int(net))]['net']]:
                    print('########################################')
                    print(node)
                    print(self.nodes['{:}'.format(int(node))]['net'])
                    print(net)
                    print(self.nodes['{:}'.format(int(net))]['net'])
                    print('Broken Node-Node')
                    time.sleep(100)
        for node in nodes.keys():
            for ring in nodes[node]['dual']:
                #print(dual['{:}'.format(int(ring))]['dual'])
                if int(node) not in dual['{:}'.format(int(ring))]['dual']:
                    print('Broken Node-Dual')
                    time.sleep(100)
        print("---...checked")
    def update_Nodes(self,):

        ## Clear All Nodes and Duals
        self.Nodes.clear()
        self.Dual.clear()

        ## Add back all nodes with crds
        for i in self.nodes.keys():
            self.Nodes.add_node('{:}'.format(i), pos=self.nodes['{:}'.format(i)]['crds'])
        ## Add all edges
        for i in self.nodes.keys():
            for j in self.nodes['{:}'.format(i)]['net']:
                self.Nodes.add_edge('{:}'.format(i), '{:}'.format(j))

        for i in self.dual.keys():
            self.Dual.add_node('{:}'.format(i), pos=self.dual['{:}'.format(i)]['crds'])
        for i in self.dual.keys():
            for j in self.dual['{:}'.format(i)]['net']:
                self.Dual.add_edge('{:}'.format(i), '{:}'.format(j))

        return self.Nodes, self.Dual

    # def update_Nodes_A(self, ):
    #     self.Nodes.clear()
    #     self.Dual.clear()
    #
    #     for i in self.nodesA.keys():
    #         #            print(self.nodes['{:}'.format(i)].keys())
    #         #            print(self.nodes['{:}'.format(i)]['crds'])
    #         self.Nodes.add_node('{:}'.format(int(i)), pos=self.nodesA['{:}'.format(i)]['crds'])
    #
    #     for i in self.nodesA.keys():
    #         #            print(self.nodes['{:}'.format(i)].keys())
    #         for j in self.nodesA['{:}'.format(i)]['net']:
    #             self.Nodes.add_edge('{:}'.format(int(i)), '{:}'.format(int(j)))
    #
    #     for i in self.dualA.keys():
    #         self.Dual.add_node('{:}'.format(int(i)), pos=self.dualA['{:}'.format(i)]['crds'])
    #     for i in self.dualA.keys():
    #         for j in self.dualA['{:}'.format(i)]['net']:
    #             self.Dual.add_edge('{:}'.format(int(i)), '{:}'.format(int(j)))
    #
    #     return self.Nodes, self.Dual
    #
    # def update_Nodes_B(self, ):
    #     self.Nodes.clear()
    #     self.Dual.clear()
    #     for i in self.nodesB.keys():
    #         #            print(self.nodes['{:}'.format(i)].keys())
    #         #            print(self.nodes['{:}'.format(i)]['crds'])
    #         self.Nodes.add_node('{:}'.format(i), pos=self.nodesB['{:}'.format(i)]['crds'])
    #     for i in self.nodesB.keys():
    #         #            print(self.nodes['{:}'.format(i)].keys())
    #         for j in self.nodesB['{:}'.format(i)]['net']:
    #             self.Nodes.add_edge('{:}'.format(i), '{:}'.format(j))
    #
    #     for i in self.dualB.keys():
    #         self.Dual.add_node('{:}'.format(i), pos=self.dualB['{:}'.format(i)]['crds'])
    #     for i in self.dualB.keys():
    #         for j in self.dualB['{:}'.format(i)]['net']:
    #             self.Dual.add_edge('{:}'.format(i), '{:}'.format(j))
    #
    #     return self.Nodes, self.Dual


#     def refresh(self):
# #        self.Nodes, self.Dual = self.update_Nodes(self)
#         self.update_Nodes()
#         node_pos = nx.get_node_attributes(self.Nodes, 'pos')
#         for node in node_pos:
#             center_coordinates = (int(self.scale*node_pos[node][0]+self.x_offset), int(self.scale*node_pos[node][1]+self.y_offset))
#             radius = int(0.1*self.scale)
#             color = (255,0,0)
#             thickness = 1
#             cv2.circle(self.clone, center_coordinates, radius, color, thickness)
#
#         ring_pos = nx.get_node_attributes(self.Dual,  'pos')
#         for ring in ring_pos:
#             center_coordinates = (int(self.scale*ring_pos[ring][0]+self.x_offset), int(self.scale*ring_pos[ring][1]+self.y_offset))
#             radius = int(0.1*self.scale)
#             color = (0,255,0)
#             thickness = 1
#             cv2.circle(self.clone, center_coordinates, radius, color, thickness)
#
#
#         for node in self.Nodes:
#             edges = self.Nodes.edges(node)
#             for edge0, edge1 in edges:
#                 edge0, edge1 = int(float(edge0)), int(float(edge1))
#                 if edge0 < edge1 and '{:}'.format(edge0) in self.Nodes.nodes and '{:}'.format(edge1) in self.Nodes.nodes:
#                     crd0, crd1 =  (int(self.scale*node_pos['{:}'.format(edge0)][0]+self.x_offset), int(self.scale*node_pos['{:}'.format(edge0)][1]+self.y_offset)), \
#                                   (int(self.scale*node_pos['{:}'.format(edge1)][0]+self.x_offset), int(self.scale*node_pos['{:}'.format(edge1)][1]+self.y_offset))
#                     (x0,y0) = crd0
#                     (x1,y1) = crd1
#                     dx = x1-x0
#                     dy = y1-y0
#                     if abs(dx) < 200 and abs(dy) < 200:
#                         cv2.line(self.clone, crd0, crd1, (255,36,12), 2)
# #            cv2.imshow("image", self.clone)
#
#         for ring in self.Dual:
#             edges = self.Dual.edges(ring)
#             for edge0, edge1 in edges:
#                 edge0, edge1 = int(float(edge0)), int(float(edge1))
#                 if edge0 < edge1:
#                     crd0, crd1 =  (int(self.scale*ring_pos['{:}'.format(edge0)][0]+self.x_offset), int(self.scale*ring_pos['{:}'.format(edge0)][1]+self.y_offset)), \
#                                   (int(self.scale*ring_pos['{:}'.format(edge1)][0]+self.x_offset), int(self.scale*ring_pos['{:}'.format(edge1)][1]+self.y_offset))
#                     (x0,y0) = crd0
#                     (x1,y1) = crd1
#                     dx = x1-x0
#                     dy = y1-y0
#                     if abs(dx) < 200 and abs(dy) < 200:
#                         cv2.line(self.clone, crd0, crd1, (255,36,12), 1)
#
#         for i in self.undercoordinated:
#             if '{:}'.format(i) in self.nodes.keys():
#                 x_uncoord, y_uncoord = self.scale * self.nodes['{:}'.format(i)]['crds'][
#                    0] + self.x_offset, self.scale * self.nodes['{:}'.format(i)]['crds'][1] + self.y_offset
#                 print(x_uncoord, y_uncoord)
#                 cv2.circle(self.clone, (int(x_uncoord), int(y_uncoord)), 25, (36, 255, 12), -1)
#
# #        for ring in Dual:
# #            edges = Dual.edges(ring)
# #            print(edges)
#
#         return
    def refresh_new_cnxs(self, atoms):
        #        self.Nodes, self.Dual = self.update_Nodes(self)
        self.update_Nodes()
        node_pos = nx.get_node_attributes(self.Nodes, 'pos')
        for node in node_pos:
            center_coordinates = (
            int(self.scale * node_pos[node][0] + self.x_offset), int(self.scale * node_pos[node][1] + self.y_offset))
            radius = int(0.1 * self.scale)
            color = (255, 0, 0)
            thickness = 1
            cv2.circle(self.clone, center_coordinates, radius, color, thickness)

        ring_pos = nx.get_node_attributes(self.Dual, 'pos')
        for ring in ring_pos:
            center_coordinates = (
            int(self.scale * ring_pos[ring][0] + self.x_offset), int(self.scale * ring_pos[ring][1] + self.y_offset))
            radius = int(0.1 * self.scale)
            color = (0, 255, 0)
            thickness = 1
            cv2.circle(self.clone, center_coordinates, radius, color, thickness)

        for node in self.Nodes:
            edges = self.Nodes.edges(node)
            for edge0, edge1 in edges:
                edge0, edge1 = int(float(edge0)), int(float(edge1))
                if edge0 < edge1 and '{:}'.format(edge0) in self.Nodes.nodes and '{:}'.format(edge1) in self.Nodes.nodes:
                    crd0, crd1 = (int(self.scale * node_pos['{:}'.format(edge0)][0] + self.x_offset),
                                  int(self.scale * node_pos['{:}'.format(edge0)][1] + self.y_offset)), \
                                 (int(self.scale * node_pos['{:}'.format(edge1)][0] + self.x_offset),
                                  int(self.scale * node_pos['{:}'.format(edge1)][1] + self.y_offset))
                    (x0, y0) = crd0
                    (x1, y1) = crd1
                    dx = x1 - x0
                    dy = y1 - y0
                    if abs(dx) < 200 and abs(dy) < 200:
                        cv2.line(self.clone, crd0, crd1, (255, 36, 12), 2)
        #            cv2.imshow("image", self.clone)

        for ring in self.Dual:
            edges = self.Dual.edges(ring)
            for edge0, edge1 in edges:
                edge0, edge1 = int(float(edge0)), int(float(edge1))
                if edge0 < edge1:
                    crd0, crd1 = (int(self.scale * ring_pos['{:}'.format(edge0)][0] + self.x_offset),
                                  int(self.scale * ring_pos['{:}'.format(edge0)][1] + self.y_offset)), \
                                 (int(self.scale * ring_pos['{:}'.format(edge1)][0] + self.x_offset),
                                  int(self.scale * ring_pos['{:}'.format(edge1)][1] + self.y_offset))
                    (x0, y0) = crd0
                    (x1, y1) = crd1
                    dx = x1 - x0
                    dy = y1 - y0
                    if abs(dx) < 200 and abs(dy) < 200:
                        cv2.line(self.clone, crd0, crd1, (255, 36, 12), 1)

        for i in self.undercoordinated:
            if '{:}'.format(i) in self.nodes.keys():
                x_uncoord, y_uncoord = self.scale * self.nodes['{:}'.format(i)]['crds'][
                    0] + self.x_offset, self.scale * self.nodes['{:}'.format(i)]['crds'][1] + self.y_offset
                #print(x_uncoord, y_uncoord)
                cv2.circle(self.clone, (int(x_uncoord), int(y_uncoord)), 5, (36, 255, 12), -1)
            else:
                print("Uncoordinated Atoms Doesnt Exist")
        #        for ring in Dual:
        #            edges = Dual.edges(ring)
        #            print(edges)
        for i in atoms:
            print(i, atoms.index(i))
            if '{:}'.format(i) in self.nodes.keys():
                x_uncoord, y_uncoord = self.scale * self.nodes['{:}'.format(i)]['crds'][
                    0] + self.x_offset, self.scale * self.nodes['{:}'.format(i)]['crds'][1] + self.y_offset
                r,g,b =  (5+atoms.index(i)*20)%255, 36, abs(255-atoms.index(i)*20)
                #print(x_uncoord, y_uncoord)
                cv2.circle(self.clone, (int(x_uncoord), int(y_uncoord)), 10, (r, g, b), -1)
            else:
                print("Starting From atom doesn't Exist!")

        for i in range(0, len(atoms)-1, 2):
            atom0 = atoms[i]
            atom1 = atoms[i+1]
            x_uncoord_0, y_uncoord_0 = self.scale * self.nodes['{:}'.format(atom0)]['crds'][
                    0] + self.x_offset, self.scale * self.nodes['{:}'.format(atom0)]['crds'][1] + self.y_offset
            x_uncoord_1, y_uncoord_1 = self.scale * self.nodes['{:}'.format(atom1)]['crds'][
                    0] + self.x_offset, self.scale * self.nodes['{:}'.format(atom1)]['crds'][1] + self.y_offset
            r, g, b = 1,1,1
            cv2.line(self.clone, (int(x_uncoord_0), int(y_uncoord_0)), (int(x_uncoord_1), int(y_uncoord_1)), (r,g,b), 5)


        return

#     def refresh_A(self, atoms):
#         #        self.Nodes, self.Dual = self.update_Nodes(self)
#         self.Nodes, self.Dual = self.update_Nodes_A()
#         self.clone = self.original_image
#         #cv2.imshow("image", self.original_image)
#         #self.show_image()
#         #time.sleep(10)
# #        self.show_image()
#
#         node_pos = nx.get_node_attributes(self.Nodes, 'pos')
#         for node in node_pos:
#             center_coordinates = (
#             int(self.scale * node_pos[node][0] + self.x_offset), int(self.scale * node_pos[node][1] + self.y_offset))
#             radius = int(0.1 * self.scale)
#             color = (255, 0, 0)
#             thickness = 1
#             cv2.circle(self.clone, center_coordinates, radius, color, thickness)
#
#         ring_pos = nx.get_node_attributes(self.Dual, 'pos')
#         for ring in ring_pos:
#             center_coordinates = (
#             int(self.scale * ring_pos[ring][0] + self.x_offset), int(self.scale * ring_pos[ring][1] + self.y_offset))
#             radius = int(0.1 * self.scale)
#             color = (0, 255, 0)
#             thickness = 1
#             cv2.circle(self.clone, center_coordinates, radius, color, thickness)
#
# #        print('Node Count : ', self.Nodes.number_of_nodes())
# #        print('Ring Count : ', self.Dual.number_of_nodes())
#         print(node_pos.keys())
#         print(self.Nodes.nodes)
#         print(len(node_pos.keys()))
#
#         for node in self.Nodes:
#             edges = self.Nodes.edges(node)
#             for edge0, edge1 in edges:
#                 edge0, edge1 = int(float(edge0)), int(float(edge1))
# #                if edge0 < edge1 and '{:}'.format(edge0) in self.Nodes.nodes and '{:}'.format(
# #                        edge1) in self.Nodes.nodes:
#                 if edge0 < edge1 and '{:}'.format(edge0) in node_pos.keys() and '{:}'.format(
#                          edge1) in node_pos.keys():
#                     crd0, crd1 = (int(self.scale * node_pos['{:}'.format(edge0)][0] + self.x_offset),
#                                   int(self.scale * node_pos['{:}'.format(edge0)][1] + self.y_offset)), \
#                                  (int(self.scale * node_pos['{:}'.format(edge1)][0] + self.x_offset),
#                                   int(self.scale * node_pos['{:}'.format(edge1)][1] + self.y_offset))
#                     (x0, y0) = crd0
#                     (x1, y1) = crd1
#                     dx = x1 - x0
#                     dy = y1 - y0
#                     if abs(dx) < 200 and abs(dy) < 200:
#                         cv2.line(self.clone, crd0, crd1, (255, 36, 12), 2)
#         #            cv2.imshow("image", self.clone)
#
#         for ring in self.Dual:
#             edges = self.Dual.edges(ring)
#             for edge0, edge1 in edges:
#                 edge0, edge1 = int(float(edge0)), int(float(edge1))
#                 if edge0 < edge1:
#                     crd0, crd1 = (int(self.scale * ring_pos['{:}'.format(edge0)][0] + self.x_offset),
#                                   int(self.scale * ring_pos['{:}'.format(edge0)][1] + self.y_offset)), \
#                                  (int(self.scale * ring_pos['{:}'.format(edge1)][0] + self.x_offset),
#                                   int(self.scale * ring_pos['{:}'.format(edge1)][1] + self.y_offset))
#                     (x0, y0) = crd0
#                     (x1, y1) = crd1
#                     dx = x1 - x0
#                     dy = y1 - y0
#                     if abs(dx) < 200 and abs(dy) < 200:
#                         cv2.line(self.clone, crd0, crd1, (255, 36, 12), 1)
#
#         #        for ring in Dual:
#         #            edges = Dual.edges(ring)
#         #            print(edges)
#
#         for i in self.undercoordinated:
#             if '{:}'.format(i) in self.nodes.keys():
#                 x_uncoord, y_uncoord = self.scale * self.nodes['{:}'.format(i)]['crds'][
#                     0] + self.x_offset, self.scale * self.nodes['{:}'.format(i)]['crds'][1] + self.y_offset
#                 #print(x_uncoord, y_uncoord)
#                 cv2.circle(self.clone, (int(x_uncoord), int(y_uncoord)), 25, (36, 255, 12), -1)
#             else:
#                 print("Uncoordinated Atoms Doesnt Exist")
#         #        for ring in Dual:
#         #            edges = Dual.edges(ring)
#         #            print(edges)
#         for i in atoms:
#             print(i, atoms.index(i))
#             if '{:}'.format(i) in self.nodes.keys():
#                 x_uncoord, y_uncoord = self.scale * self.nodes['{:}'.format(i)]['crds'][
#                     0] + self.x_offset, self.scale * self.nodes['{:}'.format(i)]['crds'][1] + self.y_offset
#                 r,g,b =  (5+atoms.index(i)*20)%255, 36, abs(255-atoms.index(i)*20)
#                 #print(x_uncoord, y_uncoord)
#                 cv2.circle(self.clone, (int(x_uncoord), int(y_uncoord)), 15, (r, g, b), -1)
#             else:
#                 print("Starting From atom doesn't Exist!")
#
#         for i in range(0, len(atoms)-1, 2):
#             atom0 = atoms[i]
#             atom1 = atoms[i+1]
#             x_uncoord_0, y_uncoord_0 = self.scale * self.nodes['{:}'.format(atom0)]['crds'][
#                     0] + self.x_offset, self.scale * self.nodes['{:}'.format(atom0)]['crds'][1] + self.y_offset
#             x_uncoord_1, y_uncoord_1 = self.scale * self.nodes['{:}'.format(atom1)]['crds'][
#                     0] + self.x_offset, self.scale * self.nodes['{:}'.format(atom1)]['crds'][1] + self.y_offset
#             r, g, b = 255,255,255
#             cv2.line(self.clone, (int(x_uncoord_0), int(y_uncoord_0)), (int(x_uncoord_1), int(y_uncoord_1)), (r,g,b), 5)
#
#         return
#
#     def refresh_B(self):
#         #        self.Nodes, self.Dual = self.update_Nodes(self)
#         self.update_Nodes_B()
#         node_pos = nx.get_node_attributes(self.Nodes, 'pos')
#         for node in node_pos:
#             center_coordinates = (
#             int(self.scale * node_pos[node][0] + self.x_offset), int(self.scale * node_pos[node][1] + self.y_offset))
#             radius = int(0.1 * self.scale)
#             color = (255, 0, 0)
#             thickness = 1
#             cv2.circle(self.clone, center_coordinates, radius, color, thickness)
#
#         ring_pos = nx.get_node_attributes(self.Dual, 'pos')
#         for ring in ring_pos:
#             center_coordinates = (
#             int(self.scale * ring_pos[ring][0] + self.x_offset), int(self.scale * ring_pos[ring][1] + self.y_offset))
#             radius = int(0.1 * self.scale)
#             color = (0, 255, 0)
#             thickness = 1
#             cv2.circle(self.clone, center_coordinates, radius, color, thickness)
#
#         for node in self.Nodes:
#             edges = self.Nodes.edges(node)
#             for edge0, edge1 in edges:
#                 edge0, edge1 = int(float(edge0)), int(float(edge1))
#                 if edge0 < edge1 and '{:}'.format(edge0) in self.Nodes.nodes and '{:}'.format(
#                         edge1) in self.Nodes.nodes:
#                     crd0, crd1 = (int(self.scale * node_pos['{:}'.format(edge0)][0] + self.x_offset),
#                                   int(self.scale * node_pos['{:}'.format(edge0)][1] + self.y_offset)), \
#                                  (int(self.scale * node_pos['{:}'.format(edge1)][0] + self.x_offset),
#                                   int(self.scale * node_pos['{:}'.format(edge1)][1] + self.y_offset))
#                     (x0, y0) = crd0
#                     (x1, y1) = crd1
#                     dx = x1 - x0
#                     dy = y1 - y0
#                     if abs(dx) < 200 and abs(dy) < 200:
#                         cv2.line(self.clone, crd0, crd1, (255, 36, 12), 2)
#         #            cv2.imshow("image", self.clone)
#
#         for ring in self.Dual:
#             edges = self.Dual.edges(ring)
#             for edge0, edge1 in edges:
#                 edge0, edge1 = int(float(edge0)), int(float(edge1))
#                 if edge0 < edge1:
#                     crd0, crd1 = (int(self.scale * ring_pos['{:}'.format(edge0)][0] + self.x_offset),
#                                   int(self.scale * ring_pos['{:}'.format(edge0)][1] + self.y_offset)), \
#                                  (int(self.scale * ring_pos['{:}'.format(edge1)][0] + self.x_offset),
#                                   int(self.scale * ring_pos['{:}'.format(edge1)][1] + self.y_offset))
#                     (x0, y0) = crd0
#                     (x1, y1) = crd1
#                     dx = x1 - x0
#                     dy = y1 - y0
#                     if abs(dx) < 200 and abs(dy) < 200:
#                         cv2.line(self.clone, crd0, crd1, (255, 36, 12), 1)
#
#         #        for ring in Dual:
#         #            edges = Dual.edges(ring)
#         #            print(edges)
#
#         return
#
#     def check_A(self):
#         print("---checking ...")
#         for node in self.nodesA.keys():
#             for net in [int(i) for i in self.nodesA[node]['net']]:
#                 #print(node, net)
#                 if int(node) in [int(i) for i in self.nodesA.keys()] and int(net) in [int(i) for i in self.nodesA.keys()]:
#                     #print([int(i) for i in self.nodesA[node]['net']],[int(i) for i in self.nodesA['{:}'.format(int(net))]['net']])
#                     skip = 0
#                 else:
#                     print('UNAVALIABLE NODES !! ')
#                     if int(node) in [int(i) for i in self.nodesA.keys()]: print(node, [int(i) for i in self.nodesA[node]['net']])
#                     if int(net)  in [int(i) for i in self.nodesA.keys()]: print(net, [int(i) for i in self.nodesA[net]['net']])
#
#                     if int(node) not in [int(i) for i in self.nodesA.keys()]: print(node)
#                     if int(net)  not in [int(i) for i in self.nodesA.keys()]: print(net)
#                 if int(node) not in [int(i) for i in self.nodesA['{:}'.format(int(net))]['net']]:
#                     print('Broken Node-Node')
#                     time.sleep(100)
#         for node in self.nodesA.keys():
#             for dual in self.nodesA[node]['dual']:
#                 if int(node) not in self.dualA['{:}'.format(int(dual))]['dual']:
#                     print('Broken Node-Dual')
#                     time.sleep(100)
#         print("---...checked")


    def write_local(self, local_nodes, local_dual, which_ring):
        
        key = {}
        for node in local_nodes.keys():
            node_val = int(node)
            for k in self.deleted_nodes:
                if node_val >= k:
                    node_val -= 1
            key['{:}'.format(node)] = node_val



        folder = "Results_"
        maxRingSize = max([local_dual[i]['net'].shape[0] for i in local_dual.keys()])
        dimension = len(local_nodes.keys())
        folder += "{:}_".format(maxRingSize)
        folder += "{:}_".format(dimension)
        for i in local_dual.keys():
            if local_dual[i]['net'].shape[0] < 6:
                folder += "{:}".format(int(local_dual[i]['net'].shape[0]))
        if self.lj==True:
            folder += "_LJ"
        self.folder = folder

        print("FOLDER NAME !!!")
        print(folder+"\n\n\n\n")



        if os.path.isdir(folder)==False:
            os.mkdir(folder)

        with open(folder+'/key.dat', 'w') as f:
            for i in self.deleted_nodes:
                f.write('{:<5}'.format(i))
            f.write('\n')
            for node in local_nodes.keys():
                node_val = int(node)
                for k in self.deleted_nodes:
                    if node_val >= k:
                        node_val -= 1
                f.write('{:<10}{:<10}\n'.format(int(node), int(node_val)))

        def ordered_cnxs_dual_to_node(dual_dict, node_dict):
            for ring in dual_dict.keys():
                print("Ring : ", ring)
                cnxs_list = dual_dict[ring]['dual']
                if not isinstance(cnxs_list, list):
                    cnxs_list = cnxs_list.tolist()
                new_cnxs_list = []
                new_crd_list = []
                new_cnxs_list.append(cnxs_list[0])
                new_crd_list.append(node_dict['{:}'.format(int(cnxs_list[0]))]['crds'])
                i = 0
                added = False
                print("Connections List : ", cnxs_list, len(cnxs_list), new_cnxs_list)
                while i < len(cnxs_list) - 1:
                    print("     Node count ", i)
                    node0 = int(new_cnxs_list[i])
                    print("     Node : ", node0)
                    connected_to_0 = node_dict['{:}'.format(node0)]['net'].tolist()
                    print("     Node-Node connections : ", connected_to_0, " vs ", cnxs_list)

                    options = set(connected_to_0).intersection(cnxs_list)
                    print(options)
                    for val in new_cnxs_list:
                        if val in options:
                            options.remove(val)
                    print(options)
                    options = list(options)
                    new_cnxs_list.append(options[0])
                    new_crd_list.append(node_dict['{:}'.format(int(options[0]))]['crds'])
                    i += 1

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
                    x0, y0, x1, y1 = new_crd_list[i - 1][0], new_crd_list[i - 1][1], new_crd_list[i][0], \
                                     new_crd_list[i][1]
                    area += (x0 * y1 - x1 * y0)
                if area > 0:
                    new_cnxs_list.reverse()
                dual_dict[ring]['dual'] = np.asarray(new_cnxs_list)
            return

        ordered_cnxs_dual_to_node(local_dual, local_nodes)

        def ordered_cnxs_dual_to_dual(dual_dict, node_dict):



            for ring in dual_dict.keys():
#                if int(ring) !=0:
                print('Ring : ', ring)
                cnxs_list = dual_dict[ring]['net']
                print('Ring connected to ', cnxs_list)
                if not isinstance(cnxs_list, list):
                    cnxs_list = cnxs_list.tolist()


                new_cnxs_list = []
                new_crd_list = []
                new_cnxs_list.append(cnxs_list[0])
                new_crd_list.append(dual_dict['{:}'.format(int(cnxs_list[0]))]['crds'])
                i = 0
                added = False
                print('Rings Size : ', len(cnxs_list))

                while i < len(cnxs_list):

                    print(i, '/', len(cnxs_list))
                    ring0 = int(new_cnxs_list[i])
                    print('         Cnx to ', ring0)
                    #connected_to_0 = dual_dict['{:}'.format(ring0)]['net'].tolist()
                    connected_to_0 = dual_dict['{:}'.format(ring0)]['net'].tolist()
                    print('         Connected to neighbour : ', connected_to_0)

                    options = set(connected_to_0).intersection(cnxs_list)
                    print('         Options : ', options)
                    for val in new_cnxs_list:
                        if val in options:
                            options.remove(val)
                        #else:
                        #    print(val, options)
                    print('     _Ring0 : ', new_cnxs_list, cnxs_list, [item for item in cnxs_list if item not in new_cnxs_list])
                    print('     _Options : ', options)
                    options = list(options)
                    if len(options)>0:
                        new_cnxs_list.append(options[0])
                        new_crd_list.append(dual_dict['{:}'.format(int(options[0]))]['crds'])
                    elif len([item for item in cnxs_list if item not in new_cnxs_list])==1:
                        options = [item for item in cnxs_list if item not in new_cnxs_list]
                        new_cnxs_list.append(options[0])
                        new_crd_list.append(dual_dict['{:}'.format(int(options[0]))]['crds'])
#                     else:
#                         for node in local_nodes:
#                             x, y =local_nodes[node]['crds'][0], local_nodes[node]['crds'][1]
#                             plt.scatter(x,y, color='b', s=0.5)
#                             for cnx in local_nodes[node]['net']:
#                                 #print(int(cnx), int(node))
#                                 if int(cnx)<int(node):
#                                     cnx = '{:}'.format(int(cnx))
#                                     x1, y1 = local_nodes[cnx]['crds'][0], local_nodes[cnx]['crds'][1]
#                                     if (x1-x)> A_pbc[0]/2: x1 -= A_pbc[0]
#                                     elif (x1-x)<-A_pbc[0]/2: x1 += A_pbc[0]
#                                     if (y1-y)> A_pbc[1]/2: y1 -= A_pbc[1]
#                                     elif (y1-y)<-A_pbc[1]/2: y1 += A_pbc[1]
#
#                                     plt.plot([x,x1], [y,y1], color='k')
#
# #                        plt.show()
#
#                         options = set(connected_to_0).intersection(cnxs_list)
#                         print(options)
#                         x, y = dual_dict['{:}'.format(int(ring[0]))]['crds'][0], \
#                                dual_dict['{:}'.format(int(ring[0]))]['crds'][1]
#                         plt.scatter(x, y, color='r', marker='x')
#                         for node in options:
#                             x,y = dual_dict['{:}'.format(int(node))]['crds'][0], dual_dict['{:}'.format(int(node))]['crds'][1]
#                             plt.scatter(x,y, color='k', marker='x')
#                         #plt.show()
#
#                         for node in [item for item in cnxs_list if item not in new_cnxs_list]:
#                             x, y = dual_dict['{:}'.format(int(node))]['crds'][0], dual_dict['{:}'.format(int(node))]['crds'][1]
#                             plt.scatter(x, y, color='g')
#                         plt.show()
                    i += 1


                #            time.sleep(100)
                #
                #            for node1 in cnxs_list:
                #                print(node1)
                #                if node1 in connected_to_0 and node1 not in new_cnxs_list and added == False:
                #                    new_cnxs_list.append(node1)
                #                    i += 1
                #                    added = True

                # if len(new_cnxs_list)!=6:
                #     for node in local_dual.keys():
                #         x,y = local_dual[node]['crds'][0], local_dual[node]['crds'][1]
                #         plt.scatter(x,y, color='k')
                #
                #     color_list = ['r', 'g', 'b', 'c', 'y', 'k', 'purple', 'pink','r', 'g', 'b', 'c', 'y', 'k', 'purple', 'pink','r', 'g', 'b', 'c', 'y', 'k', 'purple', 'pink','r', 'g', 'b', 'c', 'y', 'k', 'purple', 'pink','r', 'g', 'b', 'c', 'y', 'k', 'purple', 'pink','r', 'g', 'b', 'c', 'y', 'k', 'purple', 'pink']
                #     print('\n\n\n\n', new_crd_list, [i for i in new_crd_list])
                #     for i in range(len(new_crd_list)):
                #         print(new_crd_list[i])
                #         plt.scatter(new_crd_list[i][0], new_crd_list[i][1], color=color_list[i])
                #         plt.plot([new_crd_list[i-1][0], new_crd_list[i][0]], [new_crd_list[i-1][1], new_crd_list[i][1]], color='r')
                #     plt.show()



                area = 0
                print(new_cnxs_list, new_crd_list)
                print(len(new_cnxs_list), len(new_crd_list))
                for i in range(len(cnxs_list)):

                    x0, y0, x1, y1 = new_crd_list[i - 1][0], new_crd_list[i - 1][1], new_crd_list[i][0], \
                                     new_crd_list[i][1]
                    area += (x0 * y1 - x1 * y0)
                if area > 0:
                    new_cnxs_list.reverse()
                dual_dict[ring]['net'] = np.asarray(new_cnxs_list)
            return

        # for node in local_nodes:
        #     x, y =local_nodes[node]['crds'][0], local_nodes[node]['crds'][1]
        #     plt.scatter(x,y, color='k', s=0.5)
        #     for cnx in local_nodes[node]['net']:
        #         #print(int(cnx), int(node))
        #         if int(cnx)<int(node):
        #             cnx = '{:}'.format(int(cnx))
        #             x1, y1 = local_nodes[cnx]['crds'][0], local_nodes[cnx]['crds'][1]
        #             if (x1-x)> A_pbc[0]/2: x1 -= A_pbc[0]
        #             elif (x1-x)<-A_pbc[0]/2: x1 += A_pbc[0]
        #             if (y1-y)> A_pbc[1]/2: y1 -= A_pbc[1]
        #             elif (y1-y)<-A_pbc[1]/2: y1 += A_pbc[1]
        #
        #             plt.plot([x,x1], [y,y1], color='k')
        #
        # plt.show()
        # for node in local_dual:
        #     x, y =local_dual[node]['crds'][0], local_dual[node]['crds'][1]
        #     plt.scatter(x,y, color='r', s=0.5)
        #     for cnx in local_dual[node]['net']:
        #         if int(cnx)<int(node):
        #             cnx = '{:}'.format(int(cnx))
        #             x1, y1 = local_dual[cnx]['crds'][0], local_dual[cnx]['crds'][1]
        #
        #             if (x1-x)> A_pbc[0]/2: x1 -= A_pbc[0]
        #             elif (x1-x)<-A_pbc[0]/2: x1 += A_pbc[0]
        #             if (y1-y)> A_pbc[1]/2: y1 -= A_pbc[1]
        #             elif (y1-y)<-A_pbc[1]/2: y1 += A_pbc[1]
        #             plt.plot([x,x1], [y,y1], color='r')
        # plt.show()

        ordered_cnxs_dual_to_dual(local_dual, local_nodes)
        
        ################################################################################################################

        deleted_nodes = self.deleted_nodes
        deleted_nodes.sort(reverse=True)
        print(deleted_nodes)
        maxNodeSize = max([local_nodes[i]['net'].shape[0] for i in local_nodes.keys()])
        with open(folder_name + '/test_A_aux.dat', 'r') as f:
            pbc = np.genfromtxt(f, skip_header=3)
        with open(folder+'/test_A_aux.dat', 'w') as f:
            f.write('{:}\n'.format(len(local_nodes.keys())))
            f.write('{:<10}{:<10}\n'.format(maxNodeSize, maxNodeSize))  #
            f.write('2DE\n')
            f.write('{:<26}{:<26}\n'.format(pbc[0, 0], pbc[0, 1]))
            f.write('{:<26}{:<26}\n'.format(pbc[1, 0], pbc[1, 1]))

        with open(folder+'/test_A_crds.dat', 'w') as f:
            for node in local_nodes.keys():
                for j in range(2):
                    f.write('{:<10.4f}'.format(local_nodes[node]['crds'][j]))
                f.write('\n')
        with open(folder+'/test_A_net.dat', 'w') as f:
            for node in local_nodes.keys():
                for j in range(3):
                    ConnectedNode = int(local_nodes[node]['net'][j])
                    # time.sleep(100)
                    for k in deleted_nodes:
                        if ConnectedNode >= k:
                            ConnectedNode -= 1
                    if ConnectedNode < 0:
                        print("Error in Atom Repositioning")
                    f.write('{:<10}'.format(int(ConnectedNode)))
                f.write('\n')

        deleted_rings = self.rings_to_remove
        deleted_rings.sort(reverse=True)

        with open(folder+'/test_A_dual.dat', 'w') as f:
            for node in local_nodes.keys():
                for j in range(3):
                    ConnectedRing = int(local_nodes[node]['dual'][j])
                    for k in deleted_rings:
                        if ConnectedRing >= k:
                            ConnectedRing -= 1
                    if ConnectedRing < 0:
                        print("Error in Ring Repositioning")
                    f.write('{:<10}'.format(int(ConnectedRing)))
                f.write('\n')
        maxRingSize = max([local_dual[i]['net'].shape[0] for i in local_dual.keys()])
        with open(folder_name + '/test_B_aux.dat', 'r') as f:
            pbc = np.genfromtxt(f, skip_header=3)
        with open(folder+'/test_B_aux.dat', 'w') as f:
            f.write('{:}\n'.format(len(local_dual.keys())))
            f.write('{:<10}{:<10}\n'.format(maxRingSize, maxRingSize))  #
            f.write('2DE\n')
            f.write('{:<26}{:<26}\n'.format(pbc[0, 0], pbc[0, 1]))
            f.write('{:<26}{:<26}\n'.format(pbc[1, 0], pbc[1, 1]))

        with open(folder+'/test_B_crds.dat', 'w') as f:
            for ring in local_dual.keys():
                for j in range(2):
                    f.write('{:<10.4f}'.format(local_dual[ring]['crds'][j]))
                f.write('\n')
        with open(folder+'/test_B_net.dat', 'w') as f:
            for ring in local_dual.keys():
                for j in range(local_dual[ring]['net'].shape[0]):
                    ConnectedRing = int(local_dual[ring]['net'][j])
                    for k in deleted_rings:
                        if ConnectedRing >= k:
                            ConnectedRing -= 1
                    if ConnectedRing < 0:
                        print("Error in Ring Repositioning")
                    if ConnectedRing >= len(local_dual.keys()):
                        print('Including Illegal Connections')
                    #                    if int(ConnectedRing)==1599:
                    #                        print('Fucked here')
                    #                    if int(ring)==0:
                    #                        print(ConnectedRing)
                    f.write('{:<10}'.format(int(ConnectedRing)))
                f.write('\n')
        with open(folder+'/test_B_dual.dat', 'w') as f:
            for ring in local_dual.keys():
                for j in range(local_dual[ring]['dual'].shape[0]):
                    ConnectedNode = int(local_dual[ring]['dual'][j])
                    for k in deleted_nodes:
                        if ConnectedNode >= k:
                            ConnectedNode -= 1
                    if ConnectedNode < 0:
                        print("Error in Atom Repositioning")

                    f.write('{:<10}'.format(int(ConnectedNode)))
                f.write('\n')

        with open(folder+'/fixed_rings.dat', 'w') as f:
            f.write('{:}\n'.format(1))
            f.write('{:}\n'.format(self.new_ring))

        old_make_crds_marks_bilayer(folder, self.lj, True, True)
        print('Completed Lammps Scripts')
        with open('next_folder.txt', 'w') as f:
           f.write('{:}'.format(folder))

        print(folder)
        sys.exit(0)

        ################################################################################################################
        
        
        
        
        
        
    def write(self):

        key = {}
        for node in self.nodesA.keys():
            node_val = int(node)
            for k in self.deleted_nodes:
                if node_val >= k:
                    node_val -= 1
            key['{:}'.format(node)] = node_val
        with open('Results/key.dat', 'w') as f:
            for i in self.deleted_nodes:
                f.write('{:<5}'.format(i))
            f.write('\n')
            for node in self.nodesA.keys():
                node_val = int(node)
                for k in self.deleted_nodes:
                    if node_val >= k:
                        node_val -= 1
                f.write('{:<10}{:<10}\n'.format(int(node), int(node_val)))


        deleted_nodes = []
        maxNodeSize = max([self.nodesA[i]['net'].shape[0] for i in self.nodesA.keys()])
        with open(folder_name + '/test_A_aux.dat', 'r') as f:
            pbc = np.genfromtxt(f, skip_header=3)
        with open('Results/testD_A_aux.dat', 'w') as f:
            f.write('{:}\n'.format(len(self.nodesA.keys())))
            f.write('{:<10}{:<10}\n'.format(maxNodeSize, maxNodeSize))  #
            f.write('2DE\n')
            f.write('{:<26}{:<26}\n'.format(pbc[0, 0], pbc[0, 1]))
            f.write('{:<26}{:<26}\n'.format(pbc[1, 0], pbc[1, 1]))

        with open('Results/testD_A_crds.dat', 'w') as f:
            for node in self.nodesA.keys():
                for j in range(2):
                    f.write('{:<10.4f}'.format(self.nodesA[node]['crds'][j]))
                f.write('\n')
        with open('Results/testD_A_net.dat', 'w') as f:
            for node in self.nodesA.keys():
                for j in range(3):
                    ConnectedNode = int(self.nodesA[node]['net'][j])
                    #time.sleep(100)
                    for k in deleted_nodes:
                        if ConnectedNode >= k:
                            ConnectedNode -= 1
                    if ConnectedNode < 0 :
                        print("Error in Atom Repositioning")
                    f.write('{:<10}'.format(int(ConnectedNode)))
                f.write('\n')



        with open('Results/test_AD_dual.dat', 'w') as f:
            for node in self.nodesA.keys():
                for j in range(3):
                    ConnectedRing = int(self.nodesA[node]['dual'][j])
                    for k in self.rings_to_remove:
                        if ConnectedRing >= k:
                            ConnectedRing -= 1
                    if ConnectedRing < 0 :
                        print("Error in Ring Repositioning")
                    f.write('{:<10}'.format(int(ConnectedRing)))
                f.write('\n')
        maxRingSize = max([self.dualA[i]['net'].shape[0] for i in self.dualA.keys()])
        with open(folder_name+'/test_B_aux.dat', 'r') as f:
            pbc = np.genfromtxt(f, skip_header=3)
        with open('Results/testD_B_aux.dat', 'w') as f:
            f.write('{:}\n'.format(len(self.dualA.keys())))
            f.write('{:<10}{:<10}\n'.format(maxRingSize, maxRingSize))#
            f.write('2DE\n')
            f.write('{:<26}{:<26}\n'.format(pbc[0,0], pbc[0,1]))
            f.write('{:<26}{:<26}\n'.format(pbc[1,0], pbc[1,1]))

        with open('Results/testD_B_crds.dat', 'w') as f:
            for ring in self.dualA.keys():
                for j in range(2):
                    f.write('{:<10.4f}'.format(self.dualA[ring]['crds'][j]))
                f.write('\n')
        with open('Results/testD_B_net.dat', 'w') as f:
            for ring in self.dualA.keys():
                for j in range(self.dualA[ring]['net'].shape[0]):
                    ConnectedRing = int(self.dualA[ring]['net'][j])
                    for k in self.rings_to_remove:
                        if ConnectedRing >= k:
                            ConnectedRing -= 1
                    if ConnectedRing < 0 :
                        print("Error in Ring Repositioning")
                    if ConnectedRing >= len(self.dualA.keys()):
                        print('Including Illegal Connections')
                    if int(ConnectedRing)==1599:
                        print('Fucked here')
                    if int(ring)==0:
                        print(ConnectedRing)
                    f.write('{:<10}'.format(int(ConnectedRing)))
                f.write('\n')
        with open('Results/testD_B_dual.dat', 'w') as f:
            for ring in self.dualA.keys():
                for j in range(self.dualA[ring]['dual'].shape[0]):
                    ConnectedNode = int(self.dualA[ring]['dual'][j])
                    for k in self.deleted_nodes:
                        if ConnectedNode >= k:
                            ConnectedNode -= 1
                    if ConnectedNode < 0 :
                        print("Error in Atom Repositioning")

                    f.write('{:<10}'.format(int(ConnectedNode)))
                f.write('\n')

        with open('Results/fixed_rings.dat', 'w') as f:
            f.write('{:}\n'.format(1))
            f.write('{:}\n'.format(self.new_ring))

    def write_A(self):
        print('Writing A ')
#        shutil.copy(folder_name+'/test_A_aux.dat', 'test_A_aux.dat')

        key = {}
        for node in self.nodesA.keys():
            node_val = int(node)
            for k in self.deleted_nodes:
                if node_val >= k:
                    node_val -= 1
            key['{:}'.format(node)] = node_val
        with open('Results/key.dat', 'w') as f:
            for i in self.deleted_nodes:
                f.write('{:<5}'.format(i))
            f.write('\n')
            for node in self.nodesA.keys():
                node_val = int(node)
                for k in self.deleted_nodes:
                    if node_val >= k:
                        node_val -= 1
                f.write('{:<10}{:<10}\n'.format(int(node), int(node_val)))




        nodesAA = {}

        for node in self.nodesA.keys():
            nodesAA['{:}'.format(key['{:}'.format(int(node))])] = {}
            nodesAA['{:}'.format(key['{:}'.format(int(node))])]['crds'] = self.nodesA[node]['crds']
            nodesAA['{:}'.format(key['{:}'.format(int(node))])]['net'] = []
            for val in self.nodesA[node]['net']:
                nodesAA['{:}'.format(key['{:}'.format(int(node))])]['net'].append(key['{:}'.format(int(val))])

        for node in nodesAA.keys():
            for net in [int(i) for i in nodesAA[node]['net']]:
                # print(node, net)
                if int(node) in [int(i) for i in nodesAA.keys()] and int(net) in [int(i) for i in nodesAA.keys()]:
                    # print([int(i) for i in self.nodesAAA[node]['net']],[int(i) for i in self.nodesAAA['{:}'.format(int(net))]['net']])
                    skip = 0
                else:
                    print('UNAVALIABLE NODES !! ')
                    if int(node) in [int(i) for i in nodesAA.keys()]: print(node, [int(i) for i in nodesAA[node]['net']])
                    if int(net) in [int(i) for i in nodesAA.keys()]: print(net, [int(i) for i in nodesAA[net]['net']])

                    if int(node) not in [int(i) for i in nodesAA.keys()]: print(node)
                    if int(net) not in [int(i) for i in nodesAA.keys()]: print(net)
                if int(node) not in [int(i) for i in nodesAA['{:}'.format(int(net))]['net']]:
                    print('########################################')
                    print(node)
                    print(nodesAA['{:}'.format(int(node))]['net'])
                    print(net)
                    print(nodesAA['{:}'.format(int(net))]['net'])
                    print('Broken Node-Node')


        #time.sleep(100)

        def ordered_cnxs_dual_to_node(dual_dict, node_dict):
            for ring in dual_dict.keys():
                print(ring)
                cnxs_list = dual_dict[ring]['dual']
                if not isinstance(cnxs_list, list):
                    cnxs_list = cnxs_list.tolist()
                new_cnxs_list = []
                new_crd_list = []
                new_cnxs_list.append(cnxs_list[0])
                new_crd_list.append(node_dict['{:}'.format(int(cnxs_list[0]))]['crds'])
                i = 0
                added = False
                print(len(cnxs_list))
                while i < len(cnxs_list) - 1:
                    print(i)
                    node0 = int(new_cnxs_list[i])
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
                    new_crd_list.append(node_dict['{:}'.format(int(options[0]))]['crds'])
                    i += 1

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
                    x0, y0, x1, y1 = new_crd_list[i - 1][0], new_crd_list[i - 1][1], new_crd_list[i][0], \
                                     new_crd_list[i][1]
                    area += (x0 * y1 - x1 * y0)
                if area > 0:
                    new_cnxs_list.reverse()
                dual_dict[ring]['dual'] = np.asarray(new_cnxs_list)
            return

        ordered_cnxs_dual_to_node(self.dualA, self.nodesA)

        def ordered_cnxs_dual_to_dual(dual_dict, node_dict):
            for ring in dual_dict.keys():
                print(ring)
                cnxs_list = dual_dict[ring]['net']
                if not isinstance(cnxs_list, list):
                    cnxs_list = cnxs_list.tolist()
                new_cnxs_list = []
                new_crd_list = []
                new_cnxs_list.append(cnxs_list[0])
                new_crd_list.append(dual_dict['{:}'.format(int(cnxs_list[0]))]['crds'])
                i = 0
                added = False
                print(len(cnxs_list))
                while i < len(cnxs_list) - 1:
                    print(i)
                    ring0 = int(new_cnxs_list[i])
                    print(new_cnxs_list)
                    connected_to_0 = dual_dict['{:}'.format(ring0)]['net'].tolist()
                    print(connected_to_0)

                    options = set(connected_to_0).intersection(cnxs_list)
                    print(options)
                    for val in new_cnxs_list:
                        if val in options:
                            options.remove(val)
                    print(options)
                    options = list(options)
                    new_cnxs_list.append(options[0])
                    new_crd_list.append(dual_dict['{:}'.format(int(options[0]))]['crds'])
                    i += 1

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
                    x0, y0, x1, y1 = new_crd_list[i - 1][0], new_crd_list[i - 1][1], new_crd_list[i][0], \
                                     new_crd_list[i][1]
                    area += (x0 * y1 - x1 * y0)
                if area > 0:
                    new_cnxs_list.reverse()
                dual_dict[ring]['net'] = np.asarray(new_cnxs_list)
            return

        ordered_cnxs_dual_to_dual(self.dualA, self.nodesA)

        deleted_nodes = self.deleted_nodes
        deleted_nodes.sort(reverse=True)
        print(deleted_nodes)
        maxNodeSize = max([self.nodesA[i]['net'].shape[0] for i in self.nodesA.keys()])
        with open(folder_name + '/test_A_aux.dat', 'r') as f:
            pbc = np.genfromtxt(f, skip_header=3)
        with open('Results/test_A_aux.dat', 'w') as f:
            f.write('{:}\n'.format(len(self.nodesA.keys())))
            f.write('{:<10}{:<10}\n'.format(maxNodeSize, maxNodeSize))  #
            f.write('2DE\n')
            f.write('{:<26}{:<26}\n'.format(pbc[0, 0], pbc[0, 1]))
            f.write('{:<26}{:<26}\n'.format(pbc[1, 0], pbc[1, 1]))

        with open('Results/test_A_crds.dat', 'w') as f:
            for node in self.nodesA.keys():
                for j in range(2):
                    f.write('{:<10.4f}'.format(self.nodesA[node]['crds'][j]))
                f.write('\n')
        with open('Results/test_A_net.dat', 'w') as f:
            for node in self.nodesA.keys():
                for j in range(3):
                    ConnectedNode = int(self.nodesA[node]['net'][j])
                    #time.sleep(100)
                    for k in deleted_nodes:
                        if ConnectedNode >= k:
                            ConnectedNode -= 1
                    if ConnectedNode < 0 :
                        print("Error in Atom Repositioning")
                    f.write('{:<10}'.format(int(ConnectedNode)))
                f.write('\n')

        deleted_rings = self.rings_to_remove
        deleted_rings.sort(reverse=True)

        with open('Results/test_A_dual.dat', 'w') as f:
            for node in self.nodesA.keys():
                for j in range(3):
                    ConnectedRing = int(self.nodesA[node]['dual'][j])
                    for k in deleted_rings:
                        if ConnectedRing >= k:
                            ConnectedRing -= 1
                    if ConnectedRing < 0 :
                        print("Error in Ring Repositioning")
                    f.write('{:<10}'.format(int(ConnectedRing)))
                f.write('\n')
        maxRingSize = max([self.dualA[i]['net'].shape[0] for i in self.dualA.keys()])
        with open(folder_name+'/test_B_aux.dat', 'r') as f:
            pbc = np.genfromtxt(f, skip_header=3)
        with open('Results/test_B_aux.dat', 'w') as f:
            f.write('{:}\n'.format(len(self.dualA.keys())))
            f.write('{:<10}{:<10}\n'.format(maxRingSize, maxRingSize))#
            f.write('2DE\n')
            f.write('{:<26}{:<26}\n'.format(pbc[0,0], pbc[0,1]))
            f.write('{:<26}{:<26}\n'.format(pbc[1,0], pbc[1,1]))

        with open('Results/test_B_crds.dat', 'w') as f:
            for ring in self.dualA.keys():
                for j in range(2):
                    f.write('{:<10.4f}'.format(self.dualA[ring]['crds'][j]))
                f.write('\n')
        with open('Results/test_B_net.dat', 'w') as f:
            for ring in self.dualA.keys():
                for j in range(self.dualA[ring]['net'].shape[0]):
                    ConnectedRing = int(self.dualA[ring]['net'][j])
                    for k in deleted_rings:
                        if ConnectedRing >= k:
                            ConnectedRing -= 1
                    if ConnectedRing < 0 :
                        print("Error in Ring Repositioning")
                    if ConnectedRing >= len(self.dualA.keys()):
                        print('Including Illegal Connections')
#                    if int(ConnectedRing)==1599:
#                        print('Fucked here')
#                    if int(ring)==0:
#                        print(ConnectedRing)
                    f.write('{:<10}'.format(int(ConnectedRing)))
                f.write('\n')
        with open('Results/test_B_dual.dat', 'w') as f:
            for ring in self.dualA.keys():
                for j in range(self.dualA[ring]['dual'].shape[0]):
                    ConnectedNode = int(self.dualA[ring]['dual'][j])
                    for k in deleted_nodes:
                        if ConnectedNode >= k:
                            ConnectedNode -= 1
                    if ConnectedNode < 0 :
                        print("Error in Atom Repositioning")

                    f.write('{:<10}'.format(int(ConnectedNode)))
                f.write('\n')

        with open('Results/fixed_rings.dat', 'w') as f:
            f.write('{:}\n'.format(1))
            f.write('{:}\n'.format(self.new_ring))

        make_crds_marks_bilayer()
        print('Completed Lammps Scripts')
        print()

    # def write_B(self):
    #
    #     with open('testB_A_crds.dat', 'w') as f:
    #         for node in self.nodesB.keys():
    #             for j in range(2):
    #                 f.write('{:<10.4f}'.format(self.nodesB[node]['crds'][j]))
    #             f.write('\n')
    #     with open('testB_A_net.dat', 'w') as f:
    #         for node in self.nodesB.keys():
    #             for j in range(3):
    #                 f.write('{:<10}'.format(int(self.nodesB[node]['net'][j])))
    #             f.write('\n')
    #     with open('testB_A_dual.dat', 'w') as f:
    #         for node in self.nodesB.keys():
    #             for j in range(3):
    #                 f.write('{:<10}'.format(int(self.nodesB[node]['dual'][j])))
    #             f.write('\n')
    #
    #     with open('testB_B_crds.dat', 'w') as f:
    #         for ring in self.dualB.keys():
    #             for j in range(2):
    #                 f.write('{:<10.4f}'.format(self.dualB[ring]['crds'][j]))
    #             f.write('\n')
    #     with open('testB_B_net.dat', 'w') as f:
    #         for ring in self.dualB.keys():
    #             for j in range(self.dualB[ring]['net'].shape[0]):
    #                 f.write('{:<10}'.format(int(self.dualB[ring]['net'][j])))
    #             f.write('\n')
    #     with open('testB_B_dual.dat', 'w') as f:
    #         for ring in self.dualB.keys():
    #             for j in range(self.dualB[ring]['dual'].shape[0]):
    #                 f.write('{:<10}'.format(int(self.dualB[ring]['dual'][j])))
    #             f.write('\n')

#    def convert_Removed(self):
#        self.nodesA = {}
#        for node in self.nodes.keys():
#            for k in self.deleted_nodes:
#                if node




    ####################################################################################################################

    def left_click(self, x,y):
        self.image_coordinates = x, y
        print('Clicked Coords')
        x0, y0 = self.image_coordinates

        ## Setup Variables
        Recognised = False
        RanOutOfOptions=False
        Recognised_Val = -1

        print('Checking for Duplicates')

####        r0_list = []
        ## Import node coordinates
        node_pos = nx.get_node_attributes(self.Nodes, 'pos')
        while Recognised==False and RanOutOfOptions==False:
            for node in node_pos:
                center_coordinates = np.array([int(self.scale * node_pos[node][0] + self.x_offset),
                                               int(self.scale * node_pos[node][1] + self.y_offset)])

                r0 = np.linalg.norm(np.subtract(center_coordinates, np.array([x0, y0])))
####            r0_list.append(r0)

                if r0 < self.scale * 2 / 3:
                    Recognised = True
                    Recognised_Val = int(node)
                    print("Recognised : ", Recognised_Val)
            RanOutOfOptions=True


        if Recognised == True:
            #cv2.circle(self.clone, (x0, y0), 15, (255, 36, 12), 1)

            ########################################################################################################
            merge_rings = False

            print('Deleted : ', Recognised_Val)
            print('Nodes --- Connected to ', [int(node) for node in self.nodes['{:}'.format(Recognised_Val)]['net']])
            print('Rings --- Connected to ', [int(node) for node in self.nodes['{:}'.format(Recognised_Val)]['dual']])

            ## add deleted node to list
            self.deleted_nodes.append(Recognised_Val)

            ## show these rings as broken
            for ring in self.nodes['{:}'.format(Recognised_Val)]['dual']:
                if ring not in self.broken_rings:
                    self.broken_rings.append(int(ring))

            ## add newly broken rings to list
            for ring in self.broken_rings:
                if Recognised_Val in self.dual['{:}'.format(ring)]['dual']:
                    self.dual['{:}'.format(ring)]['dual'] = self.dual['{:}'.format(ring)]['dual'].tolist()
                    self.dual['{:}'.format(ring)]['dual'].remove(Recognised_Val)
                    self.dual['{:}'.format(ring)]['dual'] = np.asarray(self.dual['{:}'.format(ring)]['dual'])

            ## add the newly undercoordinated nodes to list
            for node in self.nodes['{:}'.format(Recognised_Val)]['net']:
                self.undercoordinated.append(int(node))
                node = int(node)
                self.nodes['{:}'.format(node)]['net'] = self.nodes['{:}'.format(node)]['net'].tolist()
                self.nodes['{:}'.format(node)]['net'].remove(Recognised_Val)
                self.nodes['{:}'.format(node)]['net'] = np.asarray(self.nodes['{:}'.format(node)]['net'])

                if node in self.deleted_nodes:
                    self.undercoordinated.remove(node)
            ### check nodes
            for node in self.nodes.keys():
                for deleted_node in self.deleted_nodes:
                    #                        print(self.nodes[node]['net'].tolist())
                    if int(deleted_node) in [int(i) for i in self.nodes[node]['net'].tolist()]:
                        print('Broken')
            print('########')

            del self.nodes['{:}'.format(Recognised_Val)]

            self.clone = self.original_image.copy()
            self.refresh_new_cnxs([])
            cv2.imshow("image", self.clone)
            print("Waiting...")

    ####################################################################################################################

    def merge_rings_A(self, rings_to_merge):
        # ids of merged ring
        merged_ring = min(rings_to_merge)
        # we define the new ring as the lowest ring count of all rings to merge
        print('New Ring id   : ', merged_ring)
        # Rings connected to new merged ring
        connected_rings = []
        for ring in rings_to_merge:
            for connected in self.dualA['{:}'.format(int(ring))]['net']:
                if int(connected) not in rings_to_merge and int(connected) not in connected_rings:
                    connected_rings.append(int(connected))
        print("Connected Rings : ", connected_rings)

        ########################################################################################################################
        # update merged ring connections
        self.dualA['{:}'.format(merged_ring)]['net'] = np.asarray(connected_rings)

        self.rings_to_remove = rings_to_merge.copy()
        self.rings_to_remove.remove(merged_ring)

        # remove connections to unmerged rings
        for ring in connected_rings:
            for vals in self.rings_to_remove:
                if vals in self.dualA['{:}'.format(ring)]['net']:

                    self.dualA['{:}'.format(ring)]['net'] = self.dualA['{:}'.format(ring)]['net'].tolist()
                    self.dualA['{:}'.format(ring)]['net'].remove(vals)
                    if merged_ring not in self.dualA['{:}'.format(ring)]['net']:
                        self.dualA['{:}'.format(ring)]['net'].append(merged_ring)
                    self.dualA['{:}'.format(ring)]['net'] = np.asarray(self.dualA['{:}'.format(ring)]['net'])

        connected_nodes = []

        # replace all ring-node connections
        for ring in rings_to_merge:
            for node in self.dualA['{:}'.format(ring)]['dual']:
                if node not in connected_nodes:
                    connected_nodes.append(node)
        self.dualA['{:}'.format(merged_ring)]['dual'] = np.asarray(connected_nodes)

        # replace all node-ring connections
        for node in self.nodesA.keys():
            for ring in self.nodesA[node]['dual']:
                if ring in rings_to_merge:
                    index = np.where(self.nodesA[node]['dual'] == ring)
                    self.nodesA[node]['dual'][index] = merged_ring

        ########################################################################################################################
        # update in networkx

        new_ring_crds = self.dualA['{:}'.format(merged_ring)]['crds']
        for ring in rings_to_merge:
            if ring != merged_ring:
                new_ring_crds = np.add(new_ring_crds, self.dualA['{:}'.format(ring)]['crds'])

        new_crds = np.divide(new_ring_crds, len(rings_to_merge))
        self.dualA['{:}'.format(merged_ring)]['crds'] = new_crds

        for ring in rings_to_merge:
            if ring != merged_ring:
                print('deleting : ', int(ring))
                del self.dualA['{:}'.format(int(ring))]

        print("Merged Rings : ", rings_to_merge)
        return merged_ring


    def local_merge_rings(self, rings_to_merge, local_nodes, local_dual):
        # ids of merged ring
        merged_ring = min(rings_to_merge)
        # we define the new ring as the lowest ring count of all rings to merge
        print('New Ring id   : ', merged_ring)
        # Rings connected to new merged ring
        connected_rings = []
        for ring in rings_to_merge:
            for connected in local_dual['{:}'.format(int(ring))]['net']:
                if int(connected) not in rings_to_merge and int(connected) not in connected_rings:
                    connected_rings.append(int(connected))
        print("Connected Rings : ", connected_rings)

        ########################################################################################################################
        # update merged ring connections
        local_dual['{:}'.format(merged_ring)]['net'] = np.asarray(connected_rings)

        self.rings_to_remove = rings_to_merge.copy()
        self.rings_to_remove.remove(merged_ring)

        # remove connections to unmerged rings
        for ring in connected_rings:
            for vals in self.rings_to_remove:
                if vals in local_dual['{:}'.format(ring)]['net']:

                    local_dual['{:}'.format(ring)]['net'] = local_dual['{:}'.format(ring)]['net'].tolist()
                    local_dual['{:}'.format(ring)]['net'].remove(vals)
                    if merged_ring not in local_dual['{:}'.format(ring)]['net']:
                        local_dual['{:}'.format(ring)]['net'].append(merged_ring)
                    local_dual['{:}'.format(ring)]['net'] = np.asarray(local_dual['{:}'.format(ring)]['net'])

        connected_nodes = []

        # replace all ring-node connections
        for ring in rings_to_merge:
            for node in local_dual['{:}'.format(ring)]['dual']:
                if node not in connected_nodes:
                    connected_nodes.append(node)
        local_dual['{:}'.format(merged_ring)]['dual'] = np.asarray(connected_nodes)

        # replace all node-ring connections
        for node in local_nodes.keys():
            for ring in local_nodes[node]['dual']:
                if ring in rings_to_merge:
                    index = np.where(local_nodes[node]['dual'] == ring)
                    local_nodes[node]['dual'][index] = merged_ring

        ########################################################################################################################
        # update in networkx

        new_ring_crds = local_dual['{:}'.format(merged_ring)]['crds']
        for ring in rings_to_merge:
            if ring != merged_ring:
                new_ring_crds = np.add(new_ring_crds, local_dual['{:}'.format(ring)]['crds'])

        new_crds = np.divide(new_ring_crds, len(rings_to_merge))
        local_dual['{:}'.format(merged_ring)]['crds'] = new_crds

        for ring in rings_to_merge:
            if ring != merged_ring:
                print('deleting : ', int(ring))
                del local_dual['{:}'.format(int(ring))]

        print("Merged Rings : ", rings_to_merge)
        return merged_ring


    def check_undercoordinated_deleted(self):
        ## Check no 'undercoordinated' atoms are also deleted
        print('Overlap : ', set(self.deleted_nodes).intersection(self.undercoordinated))
        overlap = set(self.deleted_nodes).intersection(self.undercoordinated)

        while len(set(self.deleted_nodes).intersection(self.undercoordinated)) > 0:
            for val in set(self.deleted_nodes).intersection(self.undercoordinated):
                self.undercoordinated.remove(val)
        print('Overlap : ', set(self.deleted_nodes).intersection(self.undercoordinated))

    def rekey(self):
        # Deleting nodes changes the ordering
        key = {}
        for node in self.nodesA.keys():
            node_val = int(node)
            for k in self.deleted_nodes:
                if node_val >= k:
                    node_val -= 1
            key['{:}'.format(node)] = node_val
        return key

    def find_shared_cnxs_list(self, atom0):
        ## Find Nodes associated with rings0
        rings0 = self.nodes['{:}'.format(atom0)]['dual']
        ####print('Rings attached to atom 0 : ', rings0)
        ## Check which nodes share these rings
        shared_cnxs_list = [0 for i in range(len(self.undercoordinated))]
        for i in range(len(self.undercoordinated)):
            atom1 = int(self.undercoordinated[i])
            if int(atom1) not in [int(i) for i in self.nodes.keys()]:
                print('This atom is deleted, code breaks here')
                time.sleep(100)
            shared_cnxs_list[i] = len(set(rings0).intersection(self.nodes['{:}'.format(atom1)]['dual']))
            ####print("Rings attatched to ", atom1, " : ", self.nodes['{:}'.format(atom1)]['dual'])

        ## 0 connections - More than one ring apart
        ## 1 connection  - One ring apart
        ## 2 connections - share an edge
        ## 3 connections - same node!

        shared_cnxs_list = np.asarray(shared_cnxs_list)

        paths = np.where(shared_cnxs_list == 1)[0]

        if len(paths) == 1:
            print("One Way Round the Ring...")
            return paths
        elif len(paths) == 2:
            print("Two Ways Round the Ring...")
            return paths
        elif len(paths) == 3:
            print("Three Ways Round the Ring...")
            return paths
        elif len(paths) == 0:
            paths = np.where(shared_cnxs_list == 2)[0]
            if len(paths) ==1:
                print("One Way Round the Ring via shared edge ...")
                return paths
            else:
                print("No Cross Ring Connections")
                exit(1)
                
    def local_find_shared_cnxs_list(self, atom0, local_nodes, local_undercoordinated):
        ## Find Nodes associated with rings0
        rings0 = local_nodes['{:}'.format(atom0)]['dual']
        ####print('Rings attached to atom 0 : ', rings0)
        ## Check which nodes share these rings
        shared_cnxs_list = [0 for i in range(len(local_undercoordinated))]
        for i in range(len(local_undercoordinated)):
            atom1 = int(local_undercoordinated[i])
            if int(atom1) not in [int(i) for i in local_nodes.keys()]:
                print('This atom is deleted, code breaks here')
                time.sleep(100)
            shared_cnxs_list[i] = len(set(rings0).intersection(local_nodes['{:}'.format(atom1)]['dual']))
            ####print("Rings attatched to ", atom1, " : ", local_nodes['{:}'.format(atom1)]['dual'])

        ## 0 connections - More than one ring apart
        ## 1 connection  - One ring apart
        ## 2 connections - share an edge
        ## 3 connections - same node!

        shared_cnxs_list = np.asarray(shared_cnxs_list)

        paths = np.where(shared_cnxs_list == 1)[0]

        if len(paths) == 1:
            print("One Way Round the Ring...")
            return paths
        elif len(paths) == 2:
            print("Two Ways Round the Ring...")
            return paths
        elif len(paths) == 3:
            print("Three Ways Round the Ring...")
            return paths
        elif len(paths) == 0:
            paths = np.where(shared_cnxs_list == 2)[0]
            if len(paths) ==1:
                print("One Way Round the Ring via shared edge ...")
                return paths
            elif len(paths)==0:
                print("No Cross Ring Connections")
                exit(1)
            else:
                print("Multiple Ways Round the Ring via shared edge ...")


    def check_path(self, atom0, atomA):
        precheck_undercoordinated = copy.deepcopy(self.undercoordinated)
        precheck_undercoordinated.remove(atom0)
        precheck_undercoordinated.remove(atomA)

        ## check for 3 memebered rings
        intersection = list(set(self.nodesA['{:}'.format(atom0)]['net'].tolist()).intersection(
            self.nodesA['{:}'.format(atomA)]['net'].tolist()))
        print(intersection, self.nodesA['{:}'.format(atom0)]['net'].tolist(),
              self.nodesA['{:}'.format(atomA)]['net'].tolist())

        if len(intersection) == 0:
            return True
        else:
            return False

    def check_path_split(self, atom0, paths):
        atomA, atomB, atomC = -1, -1, -1
        # atomA = self.undercoordinated[paths[0]]

        if self.check_path(atom0, self.undercoordinated[paths[0]]):
            atomA = self.undercoordinated[paths[0]]
        if len(paths) > 1:
            if self.check_path(atom0, self.undercoordinated[paths[1]]):
                if atomA == -1:
                    atomA = self.undercoordinated[paths[1]]
                elif atomA != -1:
                    atomB = self.undercoordinated[paths[1]]
        if len(paths) > 2:
            if self.check_path(atom0, self.undercoordinated[paths[2]]):
                if atomA == -1:
                    atomA = self.undercoordinated[paths[2]]
                elif atomB == -1:
                    atomB = self.undercoordinated[paths[2]]
                else:
                    atomC = self.undercoordinated[paths[2]]

    ####################################################################################################################


    def extract_coordinates(self, event, x, y, flags, parameters):

        if event == cv2.EVENT_LBUTTONDOWN:
            self.left_click(x,y)
        ################################################################################################################
        if event == cv2.EVENT_RBUTTONDOWN:
            print('\n\n#######################################################################\n\n')
            print('Recombining')

            def merge_rings_A(rings_to_merge):
                # ids of merged ring
                merged_ring = min(rings_to_merge)
                print('New Ring id   : ', merged_ring)
                # rings connected to new merged ring
                connected_rings = []
                for ring in rings_to_merge:
                    for connected in self.dualA['{:}'.format(int(ring))]['net']:
                        if int(connected) not in rings_to_merge and int(connected) not in connected_rings:
                            connected_rings.append(int(connected))
                print('\n\n\n')
                print('Connected Rings : ', connected_rings)
                print(len(connected_rings))
                ########################################################################################################################
                # update merged ring connections
                self.dualA['{:}'.format(merged_ring)]['net'] = np.asarray(connected_rings)


                self.rings_to_remove = rings_to_merge.copy()
                self.rings_to_remove.remove(merged_ring)
                # replace all ring-ring connections

########                for ring in connected_rings:
########                    self.dualA['{:}'.format(ring)]['net'] = self.dualA['{:}'.format(ring)]['net'].tolist()
########
########                    for vals in self.dualA['{:}'.format(ring)]['net']:
########                        if vals in rings_to_remove:
########                            self.dualA['{:}'.format(ring)]['net'].remove(vals)
########
########                    if merged_ring not in self.dualA['{:}'.format(ring)]['net']:
########                        self.dualA['{:}'.format(ring)]['net'].append(merged_ring)
########                    self.dualA['{:}'.format(ring)]['net'] = np.asarray(self.dualA['{:}'.format(ring)]['net'])
########                    print('Ring ', ring, ' --> ', merged_ring)
                    #print(self.dualA['{:}'.format(ring)]['net'])

                for ring in connected_rings:
                    for vals in self.rings_to_remove:
                        if vals in self.dualA['{:}'.format(ring)]['net']:

                            self.dualA['{:}'.format(ring)]['net'] = self.dualA['{:}'.format(ring)]['net'].tolist()
                            self.dualA['{:}'.format(ring)]['net'].remove(vals)
                            if merged_ring not in self.dualA['{:}'.format(ring)]['net']:
                               self.dualA['{:}'.format(ring)]['net'].append(merged_ring)
                            self.dualA['{:}'.format(ring)]['net'] = np.asarray(self.dualA['{:}'.format(ring)]['net'])


#                    if int(ring) not in rings_to_merge:
#                        for ring_cnxs in self.dualA[ring]['net']:
#                            if merged_ring in self.dualA[ring]['net']:
#                                ## if our new merged ring is there, remove any old references
#                                if ring_cnxs in rings_to_merge and ring_cnxs != merged_ring:
#                                    self.dualA[ring]['net'] = self.dualA[ring]['net'].tolist()
#                                    self.dualA[ring]['net'].remove(ring_cnxs)
#                                    self.dualA[ring]['net'] = np.asarray(self.dualA[ring]['net'])
#                            else:
#                                if ring_cnxs in rings_to_merge:
#                                    index = np.where(self.dualA[ring]['net'] == ring_cnxs)
#                                    self.dualA[ring]['net'][index] = merged_ring

                connected_nodes = []
                # replace all ring-node connections
                for ring in rings_to_merge:
                    for node in self.dualA['{:}'.format(ring)]['dual']:
                        connected_nodes.append(node)
#                for ring in self.dualA.keys():
#                    if int(ring) in rings_to_merge:
#                        for node in self.dualA[ring]['dual']:
#                            connected_nodes.append(node)
                self.dualA['{:}'.format(merged_ring)]['dual'] = np.asarray(connected_nodes)

                # replace all node-ring connections
                for node in self.nodesA.keys():
                    for ring in self.nodesA[node]['dual']:
                        if ring in rings_to_merge:
                            index = np.where(self.nodesA[node]['dual'] == ring)
                            self.nodesA[node]['dual'][index] = merged_ring

                # update in networkx

                ########################################################################################################################
                new_ring_crds = self.dualA['{:}'.format(merged_ring)]['crds']
                for ring in rings_to_merge:
                    if ring != merged_ring:
                        new_ring_crds = np.add(new_ring_crds, self.dualA['{:}'.format(ring)]['crds'])

                new_crds = np.divide(new_ring_crds, len(rings_to_merge))
                self.dualA['{:}'.format(merged_ring)]['crds'] = new_crds

                for ring in rings_to_merge:
                    if ring != merged_ring:
                        print('deleting : ', int(ring))
                        del self.dualA['{:}'.format(int(ring))]



                print("Merged Rings : ", rings_to_merge)
                return merged_ring

            print('Deleted Nodes to recombine = ', self.deleted_nodes)
            print('Uncoordinated Nodes          ', self.undercoordinated)

            ## Check that these two lists don't overlap!
            self.check_undercoordinated_deleted()

            #there are always two connection patterns
            self.nodesA = copy.deepcopy(self.nodes)
            self.dualA  = copy.deepcopy(self.dual)
            self.nodesB = copy.deepcopy(self.nodes)
            self.dualB  = copy.deepcopy(self.dual)

            key = self.rekey()

            ##  There is more than one route round a ring !
            ## Pick Random Start Point
            atom0 = self.undercoordinated[0]
#            atom0 = self.undercoordinated[1]

            print('Starting from ', atom0)

            ## Add a graphical aid to show new connections
            atoms = []
            atoms.append(atom0)

            ## Visualise
            self.clone = self.original_image.copy()
            self.refresh_new_cnxs(atoms)
            cv2.imshow("image", self.clone)

#             def find_shared_cnxs_list_A(atom0):
#                 rings0 = self.nodesA['{:}'.format(atom0)]['dual']
#                 print("Ring0 : ", rings0)
#                 shared_cnxs_list = [0 for i in range(len(self.undercoordinatedA))]
#                 for i in range(len(self.undercoordinatedA)):
#                     atom1 = int(self.undercoordinatedA[i])
# #                    print(self.nodesA['{:}'.format(atom1)]['dual'])
#                     shared_cnxs_list[i] = len(set(rings0).intersection(self.nodesA['{:}'.format(atom1)]['dual']))
# #                    print("Rings attatched to ", atom1, " : ", self.nodes['{:}'.format(atom1)]['dual'])
#                 shared_cnxs_list = np.asarray(shared_cnxs_list)
#                 paths = np.where(shared_cnxs_list == 1)[0]
#                 if len(paths)==1:
#                     print("One remaining connection...")
#                     return paths[0]
#                 elif len(paths)==2:
#                     print("Two options")
#                     print(shared_cnxs_list)
#                     print(paths)
# #                    exit(1)
#                     return paths[0]
#                 elif len(paths)==0:
#                     print("Zero options")
#                     paths = np.where(shared_cnxs_list == 2)[0]
#                     if len(paths)==0:
#                         exit(1)
#                     else:
#                         return paths[0]
#
#             def find_shared_cnxs_list_B(atom0):
#                 rings0 = self.nodesB['{:}'.format(atom0)]['dual']
#                 print("Rings0 : ", rings0)
#                 shared_cnxs_list = [0 for i in range(len(self.undercoordinatedB))]
#                 for i in range(len(self.undercoordinatedB)):
#                     atom1 = int(self.undercoordinatedB[i])
# #                    print(self.nodesB['{:}'.format(atom1)]['dual'])
#                     shared_cnxs_list[i] = len(set(rings0).intersection(self.nodesB['{:}'.format(atom1)]['dual']))
#                 shared_cnxs_list = np.asarray(shared_cnxs_list)
#                 paths = np.where(shared_cnxs_list == 1)[0]
#                 if len(paths)==1:
#                     print("One remaining connection...")
#                     return paths[0]
#                 else:
#                     print("Two options")
#
#                     print(shared_cnxs_list)
#                     print(paths)
#                     exit(1)

#            for i in range(len(self.undercoordinated[1:])):
#                atom1 = int(self.undercoordinated[i+1])
#                print(atom1)
    #                print('Node0 Rings  : ', rings0)
    #                print('Node1 Rings  : ', self.nodes['{:}'.format(atom1)]['dual'])
    #                print('Node 0-1 Shared : ', len(set(rings0).intersection(self.nodes['{:}'.format(atom1)]['dual'])))
#                shared_cnxs_list[i] = len(set(rings0).intersection(self.nodes['{:}'.format(atom1)]['dual']))

#            print(shared_cnxs_list)
#            print('Done')
#            shared_cnxs_list = np.asarray(shared_cnxs_list)
#            paths = np.where(shared_cnxs_list==1)


            print('\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')

            paths = self.find_shared_cnxs_list(atom0)

            print('\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n')
            atomA, atomB, atomC = -1,-1,-1
            #atomA = self.undercoordinated[paths[0]]
            print(atom0,self.undercoordinated, paths)
            if self.check_path(atom0, self.undercoordinated[paths[0]]):
                atomA = self.undercoordinated[paths[0]]
            if len(paths)>1:
                if self.check_path(atom0, self.undercoordinated[paths[1]]):
                    if atomA==-1:
                        atomA = self.undercoordinated[paths[1]]
                    elif atomA!=-1:
                        atomB = self.undercoordinated[paths[1]]
            if len(paths)>2:
                if self.check_path(atom0, self.undercoordinated[paths[2]]):
                    if atomA==-1:
                        atomA = self.undercoordinated[paths[2]]
                    elif atomB==-1:
                        atomB = self.undercoordinated[paths[2]]
                    else:
                        atomC = self.undercoordinated[paths[2]]




            # print(paths)


            # if len(paths) == 2:
            #     atomA = self.undercoordinated[paths[0]]
            #     atomB = self.undercoordinated[paths[1]]
            # else:
            #     print(paths)
            #     atomA = self.undercoordinated[paths[0]]
            #     atomB = self.undercoordinated[paths[1]]
            #     time.sleep(20)
            # def check_path(atom0, atomA):
            #     precheck_undercoordinated = copy.deepcopy(self.undercoordinated)
            #     precheck_undercoordinated.remove(atom0)
            #     precheck_undercoordinated.remove(atomA)
            #
            #     ## check for 3 memebered rings
            #     intersection = list(set(self.nodesA['{:}'.format(atom0)]['net'].tolist()).intersection(self.nodesA['{:}'.format(atomA)]['net'].tolist()))
            #     print(intersection,     self.nodesA['{:}'.format(atom0)]['net'].tolist(), self.nodesA['{:}'.format(atomA)]['net'].tolist())
            #
            #     if len(intersection)==0:
            #         return True
            #     else:
            #         return False
            # if check_path(atom0, atomA) == False:
            #     atomA=atomB


            ############################################################################################################



#            atoms.append(atomA)

            self.clone = self.original_image.copy()
            self.refresh_new_cnxs(atoms)
            cv2.imshow("image", self.clone)
            cv2.imshow('image', draw_line_widget.show_image())
            key = cv2.waitKey(1)

            print('############ Initial Broken Rings : ', self.broken_rings)
            print('>>>>>>>>>>>> Initial Undercoordinated : ', self.undercoordinated)


            ## SPLIT HERE TO N OPTIONS

            self.undercoordinatedA  = self.undercoordinated.copy()
            self.broken_ringsA      = self.broken_rings.copy()

            self.undercoordinatedB  = self.undercoordinated.copy()
            self.broken_ringsB      = self.broken_rings.copy()

            self.cloneA = self.original_image.copy()
            self.cloneB = self.original_image.copy()

            print('Atom A : ', atomA, '    Atom B : ', atomB)



            ### PATH A
            def create_initial_path(atom0, atomA):
                ### FIND INITIAL CONNECTION
                ### VS
                ### FIND SECONDARY CONNECTION

                local_undercoordinated = self.undercoordinated.copy()
                local_broken_rings = self.broken_rings.copy()

                local_nodes = copy.deepcopy(self.nodes)
                local_dual = copy.deepcopy(self.dual)

                local_nodes['{:}'.format(atomA)]['net'] = local_nodes['{:}'.format(atomA)]['net'].tolist()
                local_nodes['{:}'.format(atomA)]['net'].append(atom0)
                local_nodes['{:}'.format(atomA)]['net'] = np.asarray(local_nodes['{:}'.format(atomA)]['net'])

                local_nodes['{:}'.format(atom0)]['net'] = local_nodes['{:}'.format(atom0)]['net'].tolist()
                local_nodes['{:}'.format(atom0)]['net'].append(atomA)
                local_nodes['{:}'.format(atom0)]['net'] = np.asarray(local_nodes['{:}'.format(atom0)]['net'])

                local_undercoordinated.remove(int(atom0))
                local_undercoordinated.remove(int(atomA))

                for ring in local_broken_rings:
                    if atom0 in local_dual['{:}'.format(ring)]['dual'] and atomA in local_dual['{:}'.format(ring)][
                        'dual']:
                        local_broken_rings.remove(ring)


                atoms.append(atomA)

                self.clone = self.original_image.copy()
                self.refresh_new_cnxs(atoms)
                cv2.imshow("image", self.clone)
                cv2.imshow('image', draw_line_widget.show_image())
                key = cv2.waitKey(1)


                print('############ One Connection Broken Rings : ', local_broken_rings)
                print('>>>>>>>>>>>> One Connection Undercoordinated : ', local_undercoordinated)

                #time.sleep(10)

                return local_undercoordinated, local_broken_rings, local_nodes, local_dual

            def check_undercoordinated(local_undercoordinated, local_nodes):
                for i in local_undercoordinated:
                    if len(local_nodes['{:}'.format(int(i))]['net'].tolist()) == 3:
                        print(i, " is not Undercoordinated !!!!")
                        print(i, local_nodes['{:}'.format(i)]['net'].tolist())
                        time.sleep(100)
                    elif len(local_nodes['{:}'.format(int(i))]['net'].tolist()) > 3:
                        print(i, " is Overcoordinated !!!!")
                        print(i, local_nodes['{:}'.format(i)]['net'].tolist())
                        time.sleep(100)

            def create_secondary_path(atom0, atomA, local_undercoordinated, local_broken_rings, local_nodes, local_dual):

                ## Check if the newly formed connection is to a site with no further connections
                if atomA not in local_undercoordinated:
                    ## If so, we travel around to the next undercoordinated atom ...
                    paths = self.local_find_shared_cnxs_list(atomA, local_nodes, local_undercoordinated)
                    print("**** ", paths, " ****")
#                    if not paths:
                    if len(paths)==0:
                        ## If there are no further atoms, we break here
                        paths = self.local_find_shared_cnxs_list(atom0, local_nodes, local_undercoordinated)
                        if not paths:
                            print("Not Working")
                            exit(1)
                    else:
                        ## Otherwise, we continue
                        if len(paths)==1:
                            atomA = local_undercoordinated[paths[0]]
                        else:
                            atomA = local_undercoordinated[paths[0]]

                while len(local_undercoordinated) > 0:
                    if atomA not in local_undercoordinated:
                        print("*********************")
                        print("atomA : ", atomA)
                        print("local_undercoordinated : ", local_undercoordinated)
                        paths = self.local_find_shared_cnxs_list(atomA, local_nodes, local_undercoordinated)
                        if len(paths)!=0:
                            atomA = local_undercoordinated[paths[0]]
                        else:
                            "Ran Out of Connections"
                    ## Check we haven't made an error!
                    check_undercoordinated(local_undercoordinated, local_nodes)

                    paths = self.local_find_shared_cnxs_list(atomA, local_nodes, local_undercoordinated)

                    print("Paths : ", paths)
                    print("local undercoordinated : ", local_undercoordinated)
                    ## Check if our new atom is connected to any further atoms
                    if len(paths)==0:

                        print("Atoms : ", atoms)
                        print("Uncoordinated Atoms : ", local_undercoordinated)

                        ## If it isn't, code broken
                        print("Still Not Working")
                        exit(1)
                    atomZ = local_undercoordinated[paths[0]]


                    ####################################################################################################

                    if atomZ not in local_nodes['{:}'.format(atomA)]['net'] and atomA not in \
                            local_nodes['{:}'.format(atomZ)]['net']:

                        local_nodes['{:}'.format(atomA)]['net'] = local_nodes['{:}'.format(atomA)]['net'].tolist()
                        local_nodes['{:}'.format(atomA)]['net'].append(atomZ)
                        local_nodes['{:}'.format(atomA)]['net'] = np.asarray(local_nodes['{:}'.format(atomA)]['net'])

                        local_nodes['{:}'.format(atomZ)]['net'] = local_nodes['{:}'.format(atomZ)]['net'].tolist()
                        local_nodes['{:}'.format(atomZ)]['net'].append(atomA)
                        local_nodes['{:}'.format(atomZ)]['net'] = np.asarray(local_nodes['{:}'.format(atomZ)]['net'])

                        local_undercoordinated.remove(atomA)
                        local_undercoordinated.remove(atomZ)

                        atoms.append(atomA)
                        atoms.append(atomZ)

                        self.clone = self.original_image.copy()
                        self.refresh_new_cnxs(atoms)
                        cv2.imshow("image", self.clone)
                        cv2.imshow('image', draw_line_widget.show_image())
                        key = cv2.waitKey(1)

                        for ring in local_broken_rings:
                            if atomA in [int(i) for i in local_dual['{:}'.format(ring)]['dual']] and atomZ in [int(i)
                                                                                                               for i in
                                                                                                               local_dual[
                                                                                                                   '{:}'.format(
                                                                                                                           ring)][
                                                                                                                   'dual']]:
                                local_broken_rings.remove(ring)
                    else:
                        print("Nodes Already Connected!")

                    atomA = atomZ


                print('############ Remaining Broken Rings : ', local_broken_rings)
                new_ring = self.local_merge_rings(local_broken_rings, local_nodes, local_dual)
                self.new_ring = new_ring
                print("Done A ! ")



                return new_ring

            ############################################################################################################
            
            def do(atom0, proposed_atom, proposed_string):
                
                if self.check_path(atom0, proposed_atom):
                    local_undercoordinated, local_broken_rings, local_nodes, local_dual = create_initial_path(atom0, proposed_atom)
                    create_secondary_path(atom0, proposed_atom, local_undercoordinated, local_broken_rings, local_nodes, local_dual)

                    self.refresh_new_cnxs(atoms)
                    cv2.imshow("image", self.clone)
                    cv2.imshow('image', draw_line_widget.show_image())
                    key = cv2.waitKey(1)

                    self.write_local(local_nodes, local_dual, proposed_string)

                return    

            do(atom0, atomA, "A")
            

#             def create_path_A(atom0, atomA):
# 
#                 ### FIND INITIAL CONNECTION
#                 ### VS
#                 ### FIND SECONDARY CONNECTION
# 
#                 local_undercoordinated = self.undercoordinated.copy()
#                 local_broken_rings     = self.broken_rings.copy()
#             
#                 local_nodes = copy.deepcopy(self.nodes)
#                 local_dual  = copy.deepcopy(self.dual)
#                 
#                 
#                 local_nodes['{:}'.format(atomA)]['net'] = local_nodes['{:}'.format(atomA)]['net'].tolist()
#                 local_nodes['{:}'.format(atomA)]['net'].append(atom0)
#                 local_nodes['{:}'.format(atomA)]['net'] = np.asarray(local_nodes['{:}'.format(atomA)]['net'])
# 
#                 local_nodes['{:}'.format(atom0)]['net'] = local_nodes['{:}'.format(atom0)]['net'].tolist()
#                 local_nodes['{:}'.format(atom0)]['net'].append(atomA)
#                 local_nodes['{:}'.format(atom0)]['net'] = np.asarray(local_nodes['{:}'.format(atom0)]['net'])
# 
#                 local_undercoordinated.remove(int(atom0))
#                 local_undercoordinated.remove(int(atomA))
# 
#                 for ring in local_broken_rings:
#                     if atom0 in local_dual['{:}'.format(ring)]['dual'] and atomA in local_dual['{:}'.format(ring)]['dual']:
#                         local_broken_rings.remove(ring)
# 
# 
#                 print('############ One Connection Broken Rings : ', local_broken_rings)
#                 print('>>>>>>>>>>>> One Connection Undercoordinated : ', local_undercoordinated)
# 
# #                connect = False
#                 connect = True
#                 atomZ = atomA
# 
#                 while len(local_undercoordinated) > 0:
#                     for i in local_undercoordinated:
#                         if len(local_nodes['{:}'.format(int(i))]['net'].tolist())>2:
#                             print(i, " is not Undercoordinated !!!!")
#                             print(i, local_nodes['{:}'.format(i)]['net'].tolist())
#                             time.sleep(100)
# 
#                     #print(len(local_undercoordinated), local_undercoordinated)
#                     paths = self.find_shared_cnxs_list(atomA)
#                     print("Paths : ", paths)
# 
#                     if not paths and atomA!=atomZ:
#                         paths = self.find_shared_cnxs_list(atomZ)
#                         print("Paths : ", paths)
#                     if not paths:
#                         atomA = local_undercoordinated[-1]
#                         paths = find_shared_cnxs_list_A(atomA)
#                         if not paths:
#                             print("Still not working")
#                             print(local_undercoordinated)
#                             print(atoms)
#                         else:
#                             print("Paths : ", paths)
# 
#                     atomZ = local_undercoordinated[paths]
# 
#                     if connect==False:
#                         connect=True
#                         atomA = atomZ
#                     else:
#                         if atomZ not in local_nodes['{:}'.format(atomA)]['net'] and atomA not in  local_nodes['{:}'.format(atomZ)]['net']:
# #                            connect=False
# 
#                             local_nodes['{:}'.format(atomA)]['net'] = local_nodes['{:}'.format(atomA)]['net'].tolist()
#                             local_nodes['{:}'.format(atomA)]['net'].append(atomZ)
#                             local_nodes['{:}'.format(atomA)]['net'] = np.asarray(local_nodes['{:}'.format(atomA)]['net'])
# 
#                             local_nodes['{:}'.format(atomZ)]['net'] = local_nodes['{:}'.format(atomZ)]['net'].tolist()
#                             local_nodes['{:}'.format(atomZ)]['net'].append(atomA)
#                             local_nodes['{:}'.format(atomZ)]['net'] = np.asarray(local_nodes['{:}'.format(atomZ)]['net'])
# 
#                             if len(local_nodes['{:}'.format(atomA)]['net'].tolist())==3:
#                                 local_undercoordinated.remove(atomA)
#                             else:
#                                 print("Not removing atom as not fully coordinated", local_nodes['{:}'.format(atomA)]['net'].tolist())
#                             if len(local_nodes['{:}'.format(atomZ)]['net'].tolist())==3:
#                                 local_undercoordinated.remove(atomZ)
#                             else:
#                                 print("Not removing atom as not fully coordinated", local_nodes['{:}'.format(atomZ)]['net'].tolist())
# 
#                             atoms.append(atomA)
#                             atoms.append(atomZ)
# 
#                             self.clone = self.original_image.copy()
#                             self.refresh_new_cnxs(atoms)
#                             cv2.imshow("image", self.clone)
# 
#                             cv2.imshow('image', draw_line_widget.show_image())
#                             key = cv2.waitKey(1)
# 
#                             for ring in self.local_broken_rings:
#                                 if atomA in [int(i) for i in local_dual['{:}'.format(ring)]['dual']] and atomZ in [int(i) for i in local_dual['{:}'.format(ring)]['dual']]:
#                                     self.local_broken_rings.remove(ring)
#                         else:
#                             print("Nodes Already Connected!")
#                             exit(1)
# 
# 
#                         atomA = atomZ
#                 print('############ Remaining Broken Rings : ', self.local_broken_rings)
#                 new_ring = merge_rings_A(self.local_broken_rings)
#                 self.new_ring = new_ring
#                 print("Done A ! ")
#                 return new_ring ## check size!

            # def create_path_B(atom0, atomB):
            #
            #     self.nodesB['{:}'.format(atomB)]['net'] = self.nodesB['{:}'.format(atomB)]['net'].tolist()
            #     self.nodesB['{:}'.format(atomB)]['net'].append(atom0)
            #     self.nodesB['{:}'.format(atomB)]['net'] = np.asarray(self.nodesB['{:}'.format(atomB)]['net'])
            #
            #     self.nodesB['{:}'.format(atom0)]['net'] = self.nodesB['{:}'.format(atom0)]['net'].tolist()
            #     self.nodesB['{:}'.format(atom0)]['net'].append(atomB)
            #     self.nodesB['{:}'.format(atom0)]['net'] = np.asarray(self.nodesB['{:}'.format(atom0)]['net'])
            #
            #
            #     self.undercoordinatedB.remove(atom0)
            #     self.undercoordinatedB.remove(atomB)
            #
            #
            #
            #     for ring in self.broken_ringsB:
            #         if atom0 in self.dualB['{:}'.format(ring)]['dual'] and atomA in self.dualB['{:}'.format(ring)]['dual']:
            #             self.broken_ringsB.remove(ring)
            #
            #     connect = False
            #     while len(self.undercoordinatedB) > 0:
            #         paths = find_shared_cnxs_list_B(atomB)
            #         print(paths)
            #         atomZ = self.undercoordinatedB[paths]
            #
            #         if connect == False:
            #             connect = True
            #             atomB = atomZ
            #         else:
            #             connect = False
            #
            #             self.nodesB['{:}'.format(atomB)]['net'] = self.nodesB['{:}'.format(atomB)]['net'].tolist()
            #             self.nodesB['{:}'.format(atomB)]['net'].append(atomZ)
            #             self.nodesB['{:}'.format(atomB)]['net'] = np.asarray(self.nodesB['{:}'.format(atomB)]['net'])
            #
            #             self.nodesB['{:}'.format(atomZ)]['net'] = self.nodesB['{:}'.format(atomZ)]['net'].tolist()
            #             self.nodesB['{:}'.format(atomZ)]['net'].append(atomB)
            #             self.nodesB['{:}'.format(atomZ)]['net'] = np.asarray(self.nodesB['{:}'.format(atomZ)]['net'])
            #
            #             self.undercoordinatedB.remove(atomB)
            #             self.undercoordinatedB.remove(atomZ)
            #
            #             for ring in self.broken_ringsB:
            #                 print(atomA, atomZ)
            #                 print(self.dualB['{:}'.format(ring)]['dual'])
            #
            #                 if atomA in [int(i) for i in self.dualB['{:}'.format(ring)]['dual']] and atomZ in [int(i) for i in self.dualB['{:}'.format(ring)]['dual']]:
            #                     self.broken_ringsB.remove(ring)
            #
            #
            #
            #             atomB = atomZ
            #     print('############ Remaining Broken Rings : ', self.broken_ringsB)
            #     merge_rings_B(self.broken_ringsB)
            #     print("Done B ! ")


#             def do_A():
#                 #self.check_A()
#                 print('CLEAN')
#                 #time.sleep(100)
#                 if check_path(atom0, atomA)==True:
#                     new_ring = create_path_A(atom0, atomA)
#                 else:
#                     new_ring = create_path_A(atom0, atomB)
#
#                 cv2.imshow("image", self.clone)
# #                self.refresh_new_cnxs(atoms)
#                 self.refresh_A(atoms)
#                 cv2.imshow("image", self.clone)
#                 cv2.imshow('image', draw_line_widget.show_image())
#                 key = cv2.waitKey(1)
#
#                 #self.check_A()
#                 self.write()
#                 self.write_A()
#
#
#                 cv2.imshow("image", self.clone)
#                 cv2.imshow('image', draw_line_widget.show_image())
#                 key = cv2.waitKey(1)

            # def do_B():
            #     create_path_B(atom0, atomB)
            #     cv2.imshow("image", self.cloneB)
            #     self.refresh_B()
            #     self.write_B()
            #     cv2.imshow("image", self.cloneB)

            #do_A()
#            do_B()
#            time.sleep(1)
#            print('\n\n\n\n\n\n')
#            print('Initial Node : ')
##            print(self.dualB['{:}'.format(int(new_ring))]['net'])
#
#            print('Deleted Nodes to recombine = ', self.deleted_nodes)
#
#            print('Starting from ', atom0)
#
#            print('Atom A : ', atomA, '    Atom B : ', atomB)
#            print('############ Initial Broken Rings : ', self.broken_rings)



            ### PATH B


    ########################################################################################################################
#        if event == cv2.EVENT_LBUTTONDOWN:
#            self.image_coordinates = [(x,y)]
#
#        # Record ending (x,y) coordintes on left mouse bottom release
#        elif event == cv2.EVENT_LBUTTONUP:
#
#            self.image_coordinates.append((x,y))
#            print('Starting: {}, Ending: {}'.format(self.image_coordinates[0], self.image_coordinates[1]))
#
#            x0,y0 = self.image_coordinates[0]
#            x1,y1 = self.image_coordinates[1]
#
#            print('Number of nodes : ', len(nodes.keys()))
#
#            if '{:}'.format(0) not in nodes.keys():
#                node_0 = 0
#                node_1 = 1
#
#                nodes['{:}'.format(node_0)] = {}
#                nodes['{:}'.format(node_1)] = {}
#
#                nodes['{:}'.format(node_0)]['crds'] = np.array([x0,y0])
#                nodes['{:}'.format(node_1)]['crds'] = np.array([x1,y1])
#
#
#                nodes['{:}'.format(node_0)]['cnxs'] = []
#                nodes['{:}'.format(node_1)]['cnxs'] = []
#
#                nodes['{:}'.format(node_0)]['cnxs'].append(node_1)
#                nodes['{:}'.format(node_1)]['cnxs'].append(node_0)
#
#                nodes['{:}'.format(node_0)]['rings'] = []
#                nodes['{:}'.format(node_1)]['rings'] = []
#
#
#
#                node_cnxs.append(np.array([0,1]))
#
#                cv2.circle(self.clone, self.image_coordinates[0], 15, (12,36,255), 1)
#                cv2.circle(self.clone, self.image_coordinates[1], 15, (12,36,255), 1)
#
#
#
#            else:
#
#                duplicate_0 = False
#                duplicate_1 = False
#                duplicate_0_val = 1
#                duplicate_1_val = 1
#
#                print('Checking for Duplicates')
#
#                r0_list = []
#                r1_list = []
#
#                for other_nodes in nodes.keys():
#                    print('    ---- ', int(other_nodes))
#
#                    r0 = np.linalg.norm(np.subtract(nodes[other_nodes]['crds'], np.array([x0,y0])))
#                    r1 = np.linalg.norm(np.subtract(nodes[other_nodes]['crds'], np.array([x1,y1])))
#                    r0_list.append(r0)
#                    r1_list.append(r1)
##                    print('         ', r0, ' ' , r1)
#
#
#                    if r0<20:
#                        print('duplicate node 0')
##                        nodes[other_nodes]['cnxs'].append(node_1)
#                        duplicate_0 = True
#                        duplicate_0_val = int(other_nodes)
##                        cv2.circle(self.clone, self.image_coordinates[0], 15, (255,36,12), 1)
##                    else:
##                        cv2.circle(self.clone, self.image_coordinates[0], 15, (12,36,255), 1)
#
#
#                    if r1<20:
#                        print('duplicate node 1')
##                        nodes[other_nodes]['cnxs'].append(node_0)
#                        duplicate_1 = True
#                        duplicate_1_val = int(other_nodes)
##                        cv2.circle(self.clone, self.image_coordinates[1], 15, (255,36,12), 1)
##                    else:
##                        cv2.circle(self.clone, self.image_coordinates[1], 15, (12,36,255), 1)
#
#                print(min(r0_list), min(r1_list))
#                print(duplicate_0, duplicate_1)
#
#                if duplicate_0 == True and duplicate_1 == True:
#                    print('both duplicated')
#
#                    node_0 = duplicate_0_val
#                    node_1 = duplicate_1_val
#                    nodes['{:}'.format(node_0)]['cnxs'].append(node_1)
#                    nodes['{:}'.format(node_1)]['cnxs'].append(node_0)
#
#                    cv2.circle(self.clone, self.image_coordinates[0], 15, (255,36,12), 1)
#                    cv2.circle(self.clone, self.image_coordinates[1], 15, (255,36,12), 1)
#
#
#
#
##                    node_0 =
# #                   node_1 =
#
#                elif duplicate_0 == True:
#
#
#                    cv2.circle(self.clone, self.image_coordinates[0], 15, (255,36,12), 1)
#                    cv2.circle(self.clone, self.image_coordinates[1], 15, (12,36,255), 1)
#
#
#                    node_0 = duplicate_0_val
#                    node_1 = len(nodes.keys())
#
#                    print('\nDuplicate 0 True!')
#                    print('Node ', node_1, ' created')
#                    print('Node ', node_0, ' reused')
#
#                    nodes['{:}'.format(node_1)] = {}
#                    nodes['{:}'.format(node_1)]['crds'] = np.array([x1,y1])
#                    nodes['{:}'.format(node_1)]['cnxs'] = []
#                    nodes['{:}'.format(node_1)]['cnxs'].append(node_0)
#                    nodes['{:}'.format(node_1)]['rings'] = []
#
#                    nodes['{:}'.format(node_0)]['cnxs'].append(node_1)
#
#
#                elif duplicate_1 == True:
#
#
#                    cv2.circle(self.clone, self.image_coordinates[1], 15, (255,36,12), 1)
#                    cv2.circle(self.clone, self.image_coordinates[0], 15, (12,36,255), 1)
#
#
#                    node_0 = len(nodes.keys())
#                    node_1 = duplicate_1_val
#                    print('\nDuplicate 1 True!')
#                    print('Node ', node_0, ' created')
#                    print('Node ', node_1, ' reused')
#
#                    nodes['{:}'.format(node_0)] = {}
#                    nodes['{:}'.format(node_0)]['crds'] = np.array([x1,y1])
#                    nodes['{:}'.format(node_0)]['cnxs'] = []
#                    nodes['{:}'.format(node_0)]['cnxs'].append(node_1)
#                    nodes['{:}'.format(node_0)]['rings'] = []
#
#                    nodes['{:}'.format(node_1)]['cnxs'].append(node_0)
#
#
#                else:
#
#
#                    cv2.circle(self.clone, self.image_coordinates[0], 15, (12,36,255), 1)
#                    cv2.circle(self.clone, self.image_coordinates[1], 15, (12,36,255), 1)
#
#
#                    node_0 = len(nodes.keys())
#                    node_1 = node_0+1
#                    print('\nNo Duplicated Found')
#                    print('Node ', node_0, ' created')
#                    print('Node ', node_1, ' created')
#
#                    nodes['{:}'.format(node_0)] = {}
#                    nodes['{:}'.format(node_0)]['crds'] = np.array([x1,y1])
#                    nodes['{:}'.format(node_0)]['cnxs'] = []
#                    nodes['{:}'.format(node_0)]['cnxs'].append(node_1)
#                    nodes['{:}'.format(node_0)]['rings'] = []
#
#                    nodes['{:}'.format(node_1)] = {}
#                    nodes['{:}'.format(node_1)]['crds'] = np.array([x1,y1])
#                    nodes['{:}'.format(node_1)]['cnxs'] = []
#                    nodes['{:}'.format(node_1)]['cnxs'].append(node_0)
#                    nodes['{:}'.format(node_1)]['rings'] = []
#
#
#
##                nodes['{:}'.format(node_0)] = {}
##                nodes['{:}'.format(node_1)] = {}
##
##
##                for other_nodes in nodes.keys():
##                    if int(other_nodes)==node_0 or
##
##
##                nodes['{:}'.format(node_0)]['crds'] = np.array([x0,y0])
##                nodes['{:}'.format(node_1)]['crds'] = np.array([x1,y1])
##
##
##                nodes['{:}'.format(node_0)]['cnxs'] = node_1
##                nodes['{:}'.format(node_1)]['cnxs'] = node_0
##
#                node_cnxs.append(np.array([node_0,node_1]))
#
#
#
#
#            list_x.append(np.array([x0,x1]))
#            list_y.append(np.array([y0,y1]))
#
#            # Draw line
#            cv2.line(self.clone, self.image_coordinates[0], self.image_coordinates[1], (36,255,12), 2)
#            cv2.imshow("image", self.clone)
#
#        # Clear drawing boxes on right mouse button click
#        elif event == cv2.EVENT_RBUTTONDOWN:
#            self.clone = self.original_image.copy()

    def show_image(self):
        return self.clone




def old_make_crds_marks_bilayer(folder, intercept_2, triangle_raft, bilayer):
    Delete_Files = True
#    with open('area.dat', 'r') as f:
#        array = np.genfromtxt(f)
#    area = float(array[0])
#    intercept_1 = int(array[1])
#    intercept_2 = int(array[2])
    area = 1.00
    intercept_1 = intercept_2
    intercept_2 = intercept_2


    #### NAMING


    AREA_SCALING  = np.sqrt(area)
    UNITS_SCALING = 1/0.52917721090380
    si_si_distance      = UNITS_SCALING * 1.609 * np.sqrt((32.0 / 9.0))
    si_o_distance       = UNITS_SCALING * si_si_distance / 2.0
    si_o_length         = UNITS_SCALING * 1.609
    o_o_distance        = UNITS_SCALING * 1.609 * np.sqrt((8.0 / 3.0))
    h                   = UNITS_SCALING * np.sin((19.5 / 180) * np.pi) * 1.609

    B_N_distance        = UNITS_SCALING * 1.44


    displacement_vectors_norm       = np.asarray([[1,0], [-0.5, np.sqrt(3)/2], [-0.5, -np.sqrt(3)/3]])
    displacement_vectors_factored   = np.multiply(displacement_vectors_norm, 0.5)

    with open(folder+'/test_A_aux.dat', 'r') as f:
        n_nodes = np.genfromtxt(f, max_rows=1)
        n_nodes = int(n_nodes)
    with open(folder+'/test_A_aux.dat', 'r') as f:
        dims = np.genfromtxt(f, skip_header=3, skip_footer=1)
        dim_x, dim_y = dims[0], dims[1]
    #dim_x *= si_si_distance*AREA_SCALING
    #dim_y *= si_si_distance*AREA_SCALING


    dim = np.array([dim_x, dim_y, 30])
    with open(folder+'/test_A_net.dat', 'r') as f:
        net = np.genfromtxt(f)

    with open(folder+'/test_A_crds.dat', 'r') as f:
        node_crds = np.genfromtxt(f)

    with open(folder+'/test_B_crds.dat', 'r') as f:
        dual_crds = np.genfromtxt(f)
    number_scaling = np.sqrt(dual_crds.shape[0]/B_crds.shape[0])
    print(dim_x, dim_y)
    dim_x, dim_y = number_scaling*dim_x, number_scaling*dim_y
    print(dim_x, dim_y)
    print(dual_crds.shape[0], B_crds.shape[0])
    print(number_scaling)
    dim = np.array([dim_x, dim_y, 30])

#    time.sleep(100)

    node_crds = np.multiply(node_crds, number_scaling)



    #############################################################################

    def pbc_v(i,j):
        v = np.subtract(j, i)
        for dimension in range(2):
            if v[dimension] < -dim[dimension]/2:
                v[dimension] += dim[dimension]
            elif v[dimension] > dim[dimension]/2:
                v[dimension] -= dim[dimension]

        return v
#        return np.add(i, v)

    ############################################################################
    ## Monolayer
    #monolayer_crds = np.multiply(node_crds, si_si_distance*AREA_SCALING)
    monolayer_crds = np.multiply(node_crds, 1)

    for i in range(n_nodes):
        atom_1 = i
        for j in range(3):
            atom_2 = net[i,j]

            if i==0 and j==0:
                monolayer_harmpairs = np.asarray([int(atom_1), int(atom_2)])
            else:
                if atom_2>atom_1:
                    monolayer_harmpairs = np.vstack((monolayer_harmpairs, np.asarray([int(atom_1), int(atom_2)])))

    for i in range(n_nodes):
        atom_1 = i
        if atom_1==0:
            monolayer_angles = np.asarray([[net[i,0], i, net[i,1]],
                                           [net[i,0], i, net[i,2]],
                                           [net[i,1], i, net[i,2]]])
        else:
            monolayer_angles = np.vstack((monolayer_angles, np.asarray([[net[i,0], i, net[i,1]],
                                                                        [net[i,0], i, net[i,2]],
                                                                        [net[i,1], i, net[i,2]]])))

    print('Monolayer n {:}'.format(monolayer_crds.shape[0]))
    print('Monolayer harmpairs {:}'.format(monolayer_harmpairs.shape[0]))

    def plot_monolayer():
        plt.scatter(monolayer_crds[:,0], monolayer_crds[:,1], color='k', s=0.4)
        for i in range(monolayer_crds.shape[0]):
            atom_1_crds = monolayer_crds[int(monolayer_harmpairs[i,0]),:]
            atom_2_crds = monolayer_crds[int(monolayer_harmpairs[i,1]),:]
            atom_2_crds = np.add(atom_1_crds, pbc_v(atom_1_crds, atom_2_crds))
            plt.plot([atom_1_crds[0], atom_2_crds[0]], [atom_1_crds[1], atom_2_crds[1]], color='k')
        plt.show()

        print('plotting...?')
    #plot_monolayer()

    with open(folder+'/PARM_Si.lammps', 'w') as f:
        f.write('bond_style harmonic        \n')
        #f.write('bond_coeff 1 {:<.4f} {:}  \n'.format(1.001/(si_si_distance**2),si_si_distance))
        f.write('bond_coeff 1 0.800 1.000  \n')
        f.write('angle_style cosine/squared       \n')
        f.write('angle_coeff 1 0.200 120   \n')

    with open(folder+'/Si.data', 'w') as f:
        f.write('DATA FILE Produced from netmc results (cf David Morley)\n')
        f.write('{:} atoms\n'.format(monolayer_crds.shape[0]))
        f.write('{:} bonds\n'.format(monolayer_harmpairs.shape[0]))
        f.write('{:} angles\n'.format(monolayer_angles.shape[0]))
        f.write('0 dihedrals\n')
        f.write('0 impropers\n')
        f.write('1 atom types\n')
        f.write('1 bond types\n')
        f.write('1 angle types\n')
        f.write('0 dihedral types\n')
        f.write('0 improper types\n')
        f.write('0.00000 {:<5} xlo xhi\n'.format(dim[0]))
        f.write('0.00000 {:<5} ylo yhi\n'.format(dim[1]))
#        f.write('0.0000 20.0000 zlo zhi\n')
        f.write('\n')
        f.write('# Pair Coeffs\n')
        f.write('#\n')
        f.write('# 1  Si\n')
        f.write('\n')
        f.write('# Bond Coeffs\n')
        f.write('# \n')
        f.write('# 1  Si-Si\n')
        f.write('\n')
        f.write('# Angle Coeffs\n')
        f.write('# \n')
        f.write('# 1  Si-Si-Si\n')
        f.write('\n')
        f.write(' Masses\n')
        f.write('\n')
        f.write('1 28.085500 # Si\n')
        f.write('\n')
        f.write(' Atoms # molecular\n')
        f.write('\n')
        for i in range(monolayer_crds.shape[0]):
            f.write('{:<4} {:<4} {:<4} {:<24} {:<24} {:<24}# Si\n'.format(int(i + 1), int(i + 1), 1, monolayer_crds[i, 0], monolayer_crds[i, 1], 0.0))
        f.write('\n')
        f.write(' Bonds\n')
        f.write('\n')
        for i in range(monolayer_harmpairs.shape[0]):
            f.write('{:} {:} {:} {:}\n'.format(int(i + 1), 1, int(monolayer_harmpairs[i, 0]+1), int(monolayer_harmpairs[i, 1]+1)))
        f.write('\n')
        f.write(' Angles\n')
        f.write('\n')
        for i in range(monolayer_angles.shape[0]):
            f.write('{:} {:} {:} {:} {:}\n'.format(int(i + 1), 1, int(monolayer_angles[i, 0]+1), int(monolayer_angles[i, 1]+1), int(monolayer_angles[i,2]+1)))

    with open(folder+'/Si.in', 'w') as f:
        #f.write('log Si.log\n')
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
        f.write('atom_style              molecular                                                  \n')
        f.write('read_data               Si.data                                                  \n')
        f.write('timestep ${time}                                                                   \n')
        f.write('\n')
        f.write('#####################################################################              \n')
        f.write('\n')
        f.write('#potential                                                                         \n')
        f.write('include                 PARM_Si.lammps                                                \n')
        f.write('\n')

        #        f.write('#####################################################################              \n')
        #        f.write('\n')
        #        f.write('pair_write 1 1 50 r 2.0 6.0 OO_pair.dat OO_Pair                                    \n')
        #        f.write('pair_write 2 2 50 r 2.0 6.0 SiSi_pair.dat SiSi_Pair                                \n')
        #        f.write('bond_write 1 50 2.0 6.0 OO_bond.dat OO_bond                                        \n')
        #        f.write('bond_write 2 50 2.0 6.0 SiSi_bond.dat SiSi_bond                                    \n')
        #        f.write('\n')
        f.write('#####################################################################              \n')
        f.write('variable xscale equal 1.0\n')
        f.write('variable yscale equal 1.0\n')
        f.write('change_box all x scale ${xscale} y scale ${yscale} remap\n')
        f.write('#####################################################################\n')

        f.write('\n')
        f.write('#outputs                                                                           \n')
        f.write('thermo                  0                                                       \n')
        f.write('thermo_style            custom step pe ke epair ebond etotal vol temp              \n')
        f.write('\n')
        f.write('#####################################################################              \n')
        f.write('\n')
        f.write('dump                    1 all custom 1000000000 Si_dump.lammpstrj id element type x y z     \n')
        f.write('dump_modify             1 element Si                                             \n')
        f.write('thermo_modify           line yaml                                                  \n')
        f.write('\n')
        f.write('#####################################################################              \n')
        f.write('\n')
        f.write('#initial minimisation                                                              \n')
        f.write('\n')
        #f.write('min_style               cg                                                         \n')
        #f.write('minimize        1.0e-6 0.0 1000000 10000000                                       \n')
        #f.write('\n')
        f.write('min_style               sd                                                         \n')
        f.write('minimize        1.0e-6 0.0 1000000 10000000                                       \n')
        f.write('\n')
#        f.write('#####################################################################              \n')
#        f.write('\n')
#        f.write('fix                            1 all nvt temp 0.0000001 0.0000001 1                \n')
#        f.write('\n')
#        f.write('#####################################################################              \n')
#        f.write('\n')
#        f.write('run                             1000                                               \n')
#        f.write('unfix                   1                                                          \n')
#        f.write('\n')
        f.write('#####################################################################              \n')
        f.write('\n')
        f.write('#write_data              Si_results.dat                                              \n')
        f.write('#write_restart  C_results.rest                                                     \n')

    ############################################################################
    ## Tersoff Graphene

    print("########### Tersoff Graphene ###############")
    tersoff_crds = np.multiply(node_crds, 1.42)
    with open(folder+'/PARM_C.lammps', 'w') as f:
        f.write('pair_style tersoff\n')
        f.write('pair_coeff * * Results/BNC.tersoff C\n')

    #

    with open(folder+'/C.in', 'w') as f:
            f.write('log C.log\n')
            f.write('units                   metal                                                   \n')
            f.write('dimension               2                                                          \n')
            f.write('processors              * * *                                                        \n')
            f.write('boundary                p p p                                                      \n')
            f.write('\n')
            f.write('#####################################################################              \n')
            f.write('\n')
            f.write('variable time equal 1800.0                                               \n')
            f.write('\n')
            f.write('#####################################################################              \n')
            f.write('\n')
            f.write('#read data\n')
            f.write('atom_style              atomic                                                  \n')
            f.write('read_data               Results/C.data                                                  \n')
            f.write('timestep 0.001                                                                   \n')
            f.write('\n')
            f.write('#####################################################################              \n')
            f.write('\n')
            f.write('#potential                                                                         \n')
            f.write('include                 Results/PARM_C.lammps                                                \n')
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
            f.write('dump                    1 all custom 1000000000 C_dump.lammpstrj id element type x y z     \n')
            f.write('dump_modify             1 element C                                             \n')
            f.write('thermo_modify           line yaml                                                  \n')
            f.write('\n')
            f.write('#####################################################################              \n')
            f.write('\n')
            f.write('#initial minimisation                                                              \n')
            f.write('\n')
            #f.write('min_style               cg                                                         \n')
            #f.write('minimize        1.0e-6 0.0 1000000 10000000                                       \n')
            #f.write('\n')
            f.write('min_style               sd                                                         \n')
            f.write('minimize        1.0e-6 0.0 1000000 10000000                                       \n')
            f.write('\n')
            #        f.write('#####################################################################              \n')
            #        f.write('\n')
            #        f.write('fix                            1 all nvt temp 0.0000001 0.0000001 1                \n')
            #        f.write('\n')
            #        f.write('#####################################################################              \n')
            #        f.write('\n')
            #        f.write('run                             1000                                               \n')
            #        f.write('unfix                   1                                                          \n')
            #        f.write('\n')
            f.write('#####################################################################              \n')
            f.write('\n')
            f.write('#write_data              C_results.dat                                              \n')
            f.write('#write_restart  C_results.rest                                                     \n')

    with open(folder+'/C.data', 'w') as f:
            f.write('DATA FILE Produced from netmc results (cf David Morley)\n')
            f.write('{:} atoms\n'.format(tersoff_crds.shape[0]))
            f.write('1 atom types\n')
            f.write('0.00000 {:<5} xlo xhi\n'.format(dim[0]*1.42))
            f.write('0.00000 {:<5} ylo yhi\n'.format(dim[1]*1.42))
            #        f.write('0.0000 20.0000 zlo zhi\n')
            f.write('\n')
            f.write(' Masses\n')
            f.write('\n')
            f.write('1 12.0000 # Si\n')
            f.write('\n')
            f.write(' Atoms # molecular\n')
            f.write('\n')
            for i in range(tersoff_crds.shape[0]):
                f.write('{:<4} {:<4} {:<24} {:<24} {:<24}# C\n'.format(int(i + 1), 1,
                                                                              tersoff_crds[i, 0],
                                                                              tersoff_crds[i, 1], 0.0))
            f.write('\n')



    ############################################################################


    ############################################################################
    ## Triangle Raft

    if triangle_raft:

        print("########### Triangle Raft ##############")
        dim[0] *= si_si_distance*AREA_SCALING
        dim[1] *= si_si_distance*AREA_SCALING

        dim_x *= si_si_distance*AREA_SCALING
        dim_y *= si_si_distance*AREA_SCALING
        triangle_raft_si_crds = np.multiply(monolayer_crds, si_si_distance*AREA_SCALING)
        dict_sio = {}
        for i in range(int(n_nodes*3/2), int(n_nodes*5/2)):
            dict_sio['{:}'.format(i)] = []
        for i in range(monolayer_harmpairs.shape[0]):
            atom_1 = int(monolayer_harmpairs[i,0])
            atom_2 = int(monolayer_harmpairs[i,1])
            atom_1_crds = triangle_raft_si_crds[atom_1,:]
            atom_2_crds = triangle_raft_si_crds[atom_2,:]


            v       = pbc_v(atom_1_crds, atom_2_crds)
    #        v       = np.subtract(atom_2_crds, atom_1_crds)
            norm_v  = np.divide(v, np.linalg.norm(v))

            grading     = [abs(np.dot(norm_v, displacement_vectors_norm[i,:]))    for i in range(displacement_vectors_norm.shape[0])]
            selection = grading.index(min(grading))
            if abs(grading[selection])<0.1:

                unperturbed_oxygen_0_crds = np.add(atom_1_crds, np.divide(v,2))
            #oxygen_0_crds = unperturbed_oxygen_0_crds
                oxygen_0_crds = np.add(unperturbed_oxygen_0_crds, displacement_vectors_factored[selection, :])

            else:
                oxygen_0_crds =   np.add(atom_1_crds, np.divide(v,2))

    #        unperturbed_oxygen_0_crds = np.add(atom_1_crds, np.divide(v,2))
    #        #oxygen_0_crds = unperturbed_oxygen_0_crds
    #        oxygen_0_crds = np.add(unperturbed_oxygen_0_crds, displacement_vectors_factored[selection, :])

            #        oxygen_0_crds = np.add(np.divide(np.add(atom_1_crds, atom_2_crds), 2), displacement_vectors_factored[selection, :])

            if oxygen_0_crds[0]>dim_x:  oxygen_0_crds[0]-=dim_x
            elif  oxygen_0_crds[0]<0:   oxygen_0_crds[0]+=dim_x
            if oxygen_0_crds[1]>dim_y:  oxygen_0_crds[1]-=dim_y
            elif  oxygen_0_crds[1]<0:   oxygen_0_crds[1]+=dim_y

            if i==0:
                triangle_raft_o_crds = np.asarray(oxygen_0_crds)
                triangle_raft_harmpairs = np.asarray([[i,atom_1+n_nodes*3/2],
                                                      [i,atom_2+n_nodes*3/2]])
                dict_sio['{:}'.format(int(atom_1 + n_nodes * 3 / 2))].append(i)
                dict_sio['{:}'.format(int(atom_2 + n_nodes * 3 / 2))].append(i)
            else:
                triangle_raft_o_crds    = np.vstack((triangle_raft_o_crds,      oxygen_0_crds))
                triangle_raft_harmpairs = np.vstack((triangle_raft_harmpairs,   np.asarray([[i, atom_1 + n_nodes * 3 / 2],
                                                                                            [i, atom_2 + n_nodes * 3 / 2]])))
                dict_sio['{:}'.format(int(atom_1+n_nodes*3/2))].append(i)
                dict_sio['{:}'.format(int(atom_2+n_nodes*3/2))].append(i)



        triangle_raft_si_harmpairs = triangle_raft_harmpairs


        for i in range(int(n_nodes*3/2), int(n_nodes*5/2)):
            for j in range(2):
                for k in range(j+1,3):
                    #print(i,j,k,len(dict_sio.keys()), dict_sio['{:}'.format(i)])
                    #new_harmpair = np.array([dict_sio['{:}'.format(i)][j], dict_sio['{:}'.format(i)][k]])
                    if i==int(n_nodes*3/2) and j==0 and k==1:
                        triangle_raft_o_harmpairs =  np.array([dict_sio['{:}'.format(i)][j], dict_sio['{:}'.format(i)][k]])
                    else:
                        triangle_raft_o_harmpairs = np.vstack((triangle_raft_o_harmpairs, np.array([dict_sio['{:}'.format(i)][j], dict_sio['{:}'.format(i)][k]])))
                    triangle_raft_harmpairs = np.vstack((triangle_raft_harmpairs, np.array([dict_sio['{:}'.format(i)][j], dict_sio['{:}'.format(i)][k]])))



        triangle_raft_crds = np.vstack((triangle_raft_o_crds, triangle_raft_si_crds))

        for i in range(triangle_raft_crds.shape[0]):
            for j in range(2):
                if triangle_raft_crds[i,j] > dim[j] or triangle_raft_crds[i,j] < 0:
                    print('FUCK')

        print('Triangle Raft n {:}    si {:}    o {:}'.format(triangle_raft_crds.shape[0], triangle_raft_si_crds.shape[0], triangle_raft_o_crds.shape[0]))
        print('Triangle Raft harmpairs : {:}'.format(triangle_raft_harmpairs.shape[0]))

        def plot_triangle_raft():
            plt.scatter(triangle_raft_si_crds[:,0], triangle_raft_si_crds[:,1], color='y', s=0.4)
            plt.scatter(triangle_raft_o_crds[:,0],  triangle_raft_o_crds[:,1], color='r', s=0.4)
            plt.savefig('triangle_raft atoms')
            plt.clf()
            plt.scatter(triangle_raft_si_crds[:,0], triangle_raft_si_crds[:,1], color='y', s=0.6)
            plt.scatter(triangle_raft_o_crds[:,0],  triangle_raft_o_crds[:,1], color='r', s=0.6)
            #for i in range(triangle_raft_harmpairs.shape[0]):
            print(triangle_raft_harmpairs.shape)
            for i in range(triangle_raft_harmpairs.shape[0]):

                #print(i, ' : ', triangle_raft_harmpairs[i,:])
                atom_1 = int(triangle_raft_harmpairs[i,0])
                atom_2 = int(triangle_raft_harmpairs[i,1])
                if atom_1 < triangle_raft_o_crds.shape[0] and atom_2 < triangle_raft_o_crds.shape[0]:
                    atom_1_crds = triangle_raft_crds[atom_1,:]
                    atom_2_crds = triangle_raft_crds[atom_2,:]
                    atom_2_crds = np.add(atom_1_crds, pbc_v(atom_1_crds, atom_2_crds))
                    plt.plot([atom_1_crds[0], atom_2_crds[0]], [atom_1_crds[1], atom_2_crds[1]], color='k')
            for i in range(triangle_raft_harmpairs.shape[0]):

                #print(i, ' : ', triangle_raft_harmpairs[i,:])
                atom_1 = int(triangle_raft_harmpairs[i,0])
                atom_2 = int(triangle_raft_harmpairs[i,1])
                if atom_1 < triangle_raft_o_crds.shape[0] and atom_2 < triangle_raft_o_crds.shape[0]:
                    atom_1_crds = np.add(triangle_raft_crds[atom_1,:], np.array([0,dim[1]]))
                    atom_2_crds = np.add(triangle_raft_crds[atom_2,:], np.array([0,dim[1]]))
                    atom_2_crds = np.add(atom_1_crds, pbc_v(atom_1_crds, atom_2_crds))
                    plt.plot([atom_1_crds[0], atom_2_crds[0]], [atom_1_crds[1], atom_2_crds[1]], color='k')

            plt.savefig('triangle raft bonds')
            plt.clf()
        #plot_triangle_raft()

    #    print('Bonding Pairs')
    #    with open('pair_Si2O3.txt', 'w') as f:
    #        # Si-O bonds
    #        for i in range(triangle_raft_si_harmpairs.shape[0]):
    #            f.write('{:<6} {:<6} harmonic 1.001 {:} 100.0\n'.format(int(triangle_raft_si_harmpairs[i,0]+1), int(triangle_raft_si_harmpairs[i,1]+ 1),
    #                                                                            si_o_length))
    #        # O-O bonds
    #        for i in range(triangle_raft_o_harmpairs.shape[0]):
    #            f.write('{:<6} {:<6} harmonic 1.001 {:} 100.0\n'.format(int(triangle_raft_o_harmpairs[i, 0] + 1),
    #                                                                    int(triangle_raft_o_harmpairs[i, 1] + 1),
    #                                                                    o_o_distance))
        n_bonds = triangle_raft_harmpairs.shape[0]
    #    t0 = time.time()


        n_bond_types = 2

        with open(folder+'/PARM_Si2O3.lammps', 'w') as output_file:

            output_file.write('pair_style lj/cut {:}\n'.format(o_o_distance* intercept_1))
            output_file.write('pair_coeff * * 0.1 {:} {:}\n'.format(o_o_distance* intercept_1/2**(1/6), o_o_distance* intercept_1))
            output_file.write('pair_modify shift yes\n'.format())
            output_file.write('special_bonds lj 0.0 1.0 1.0\n'.format())

            output_file.write('bond_style harmonic\n')
            output_file.write('bond_coeff 2 1.001 2.86667626014\n')
            output_file.write('bond_coeff 1 1.001 4.965228931415713\n')

        with open(folder+'/Si2O3.in', 'w') as f:
            f.write('log Si2O3.log\n')
            f.write('units                   electron                                                   \n')
            f.write('dimension               2                                                          \n')
            f.write('processors              * * *                                                      \n')
            f.write('boundary                p p p                                                      \n')
            f.write('\n')
            f.write('#####################################################################              \n')
            f.write('\n')
            f.write('variable time equal 25*0.02418884326                                               \n')
            f.write('\n')
            f.write('#####################################################################              \n')
            f.write('\n')
            f.write('#read data\n')
            f.write('atom_style              molecular                                                  \n')
            f.write('read_data               Results/Si2O3.data                                                  \n')
            f.write('timestep ${time}                                                                   \n')
            f.write('\n')
            f.write('#####################################################################              \n')
            f.write('\n')
            f.write('#potential                                                                         \n')
            f.write('include                 Results/PARM_Si2O3.lammps                                                \n')
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
            f.write('dump                    1 all custom 1000000000 Si2O3_dump.lammpstrj id element type x y z     \n')
            f.write('dump_modify             1 element O Si                                             \n')
            f.write('thermo_modify           line yaml                                                  \n')
            f.write('\n')
            f.write('#####################################################################              \n')
            f.write('\n')
            f.write('#initial minimisation                                                              \n')
            f.write('\n')
            #f.write('min_style               cg                                                         \n')
            #f.write('minimize        1.0e-6 1.0e-6 1000000 10000000                                       \n')
            #f.write('\n')
            f.write('min_style               sd                                                         \n')
            f.write('minimize        1.0e-6 1.0e-6 1000000 10000000                                       \n')
            f.write('\n')
    #        f.write('#####################################################################              \n')
    #        f.write('\n')
    #        f.write('fix                            1 all nvt temp 0.0000001 0.0000001 1                \n')
    #        f.write('\n')
    #        f.write('#####################################################################              \n')
    #        f.write('\n')
    #        f.write('run                             1000                                               \n')
    #        f.write('unfix                   1                                                          \n')
    #        f.write('\n')
            f.write('#####################################################################              \n')
            f.write('\n')
            f.write('#write_data              Si2O3_results.dat                                              \n')
            f.write('#write_restart  C_results.rest                                                     \n')

        with open(folder+'/Si2O3.data', 'w') as f:
            f.write('DATA FILE Produced from netmc results (cf David Morley)\n')
            f.write('{:} atoms\n'.format(triangle_raft_crds.shape[0]))
            f.write('{:} bonds\n'.format(int(n_bonds)))
            #f.write('0 bonds\n'.format(triangle_raft_harmpairs.shape[0]))
            f.write('0 angles\n')
            f.write('0 dihedrals\n')
            f.write('0 impropers\n')
            f.write('2 atom types\n')
            f.write('{:} bond types\n'.format(int(n_bond_types)))
            f.write('0 angle types\n')
            f.write('0 dihedral types\n')
            f.write('0 improper types\n')
            f.write('0.00000 {:<5} xlo xhi\n'.format(dim[0]))
            f.write('0.00000 {:<5} ylo yhi\n'.format(dim[1]))
            #        f.write('0.0000 20.0000 zlo zhi\n')
            f.write('\n')
            f.write('# Pair Coeffs\n')
            f.write('#\n')
            f.write('# 1  O\n')
            f.write('# 2  Si\n')
            f.write('\n')
            f.write('# Bond Coeffs\n')
            f.write('# \n')
            f.write('# 1  O-O\n')
            f.write('# 2  Si-O\n')
            f.write('# 3  O-O rep\n')
            f.write('# 4  Si-Si rep\n')

            f.write('\n')
            f.write(' Masses\n')
            f.write('\n')
            f.write('1 28.10000 # O \n')
            f.write('2 32.01000 # Si\n')
            f.write('\n')
            f.write(' Atoms # molecular\n')
            f.write('\n')

            ##
            for i in range(triangle_raft_si_crds.shape[0]):
                f.write('{:<4} {:<4} {:<4} {:<24} {:<24} {:<24} # Si\n'.format(int(i + 1),
                                                                               int(i + 1),
                                                                               2, triangle_raft_si_crds[i, 0],
                                                                               triangle_raft_si_crds[i, 1], 5.0))
            ##
            for i in range(triangle_raft_o_crds.shape[0]):
                f.write('{:<4} {:<4} {:<4} {:<24} {:<24} {:<24} # O\n'.format(int(i + 1 + triangle_raft_si_crds.shape[0]),
                                                                              int(i + 1 + triangle_raft_si_crds.shape[0]),
                                                                              1, triangle_raft_o_crds[i, 0],
                                                                              triangle_raft_o_crds[i, 1], 5.0))
            ##

            f.write('\n')
            f.write(' Bonds\n')
            f.write('\n')
            for i in range(triangle_raft_harmpairs.shape[0]):
                pair1 = triangle_raft_harmpairs[i, 0]
                if pair1 < triangle_raft_o_crds.shape[0]:
                    pair1_ref = pair1 + 1 + triangle_raft_si_crds.shape[0]
                else:
                    pair1_ref = pair1 + 1 - triangle_raft_o_crds.shape[0]
                pair2 = triangle_raft_harmpairs[i, 1]
                if pair2 < triangle_raft_o_crds.shape[0]:
                    pair2_ref = pair2 + 1 + triangle_raft_si_crds.shape[0]
                else:
                    pair2_ref = pair2 + 1 - triangle_raft_o_crds.shape[0]

                if triangle_raft_harmpairs[i,0]<triangle_raft_o_crds.shape[0] and triangle_raft_harmpairs[i,1]<triangle_raft_o_crds.shape[0]:



                    f.write('{:} {:} {:} {:} \n'.format(int(i + 1), 1, int(pair1_ref),
                                                       int(pair2_ref)))
                else:

                    f.write('{:} {:} {:} {:} \n'.format(int(i + 1), 2, int(pair1_ref),
                                                       int(pair2_ref)))



    #        for i in range(triangle_raft_harmpairs.shape[0]):
    #            if triangle_raft_harmpairs[i,0]<triangle_raft_o_crds.shape[0] and triangle_raft_harmpairs[i,1]<triangle_raft_o_crds.shape[0]:
    #
    #                f.write('{:} {:} {:} {:} \n'.format(int(i + 1), 1, int(triangle_raft_harmpairs[i, 0] + 1),
    #                                                   int(triangle_raft_harmpairs[i, 1] + 1)))
    #            else:
    #
    #                f.write('{:} {:} {:} {:} \n'.format(int(i + 1), 2, int(triangle_raft_harmpairs[i, 0] + 1),
    #                                                   int(triangle_raft_harmpairs[i, 1] + 1)))


            f.write('\n')

        with open(folder+'/Si2O3_harmpairs.dat', 'w') as f:
            f.write('{:}\n'.format(triangle_raft_harmpairs.shape[0]))
            for i in range(triangle_raft_harmpairs.shape[0]):
                if triangle_raft_harmpairs[i,0]<triangle_raft_o_crds.shape[0] and triangle_raft_harmpairs[i,1]<triangle_raft_o_crds.shape[0]:
                    f.write('{:<10} {:<10} \n'.format(int(triangle_raft_harmpairs[i, 0] + 1),
                                                       int(triangle_raft_harmpairs[i, 1] + 1)))
                else:
                    f.write('{:<10} {:<10} \n'.format(int(triangle_raft_harmpairs[i, 0] + 1),
                                                       int(triangle_raft_harmpairs[i, 1] + 1)))

        ############################################################################

    if bilayer:
        def triangle_raft_to_bilayer(i):
            if i > 3 * n_nodes/2:
                ## Si atom
                si_ref = i - 3*n_nodes/2
                return [4*n_nodes + 2*si_ref, 4*n_nodes + 2*si_ref+1]
            else:
                ## O atom
                o_ref  = i
                return [n_nodes + 2*o_ref, n_nodes + 2*o_ref+1]


        ############################################################################
        ## Bilayer
        print("############ Bilayer ###############")

        # Si Atoms
        for i in range(triangle_raft_si_crds.shape[0]):
            if i==0:
                bilayer_si_crds = np.asarray([[triangle_raft_si_crds[i,0], triangle_raft_si_crds[i,1], 5],
                                              [triangle_raft_si_crds[i,0], triangle_raft_si_crds[i,1], 5+2*si_o_length]])
            else:
                bilayer_si_crds = np.vstack((bilayer_si_crds, np.asarray([[triangle_raft_si_crds[i,0], triangle_raft_si_crds[i,1], 5],
                                                                          [triangle_raft_si_crds[i,0], triangle_raft_si_crds[i,1], 5+2*si_o_length]])))
        # O ax Atoms
        for i in range(triangle_raft_si_crds.shape[0]):
            if i==0:
                bilayer_o_crds = np.asarray([triangle_raft_si_crds[i,0], triangle_raft_si_crds[i,1], 5+si_o_length])
    #            bilayer_harmpairs = np.asarray([[i, 3200+2*i], [i, 3200+2*i+1]])
            else:
                bilayer_o_crds = np.vstack((bilayer_o_crds, np.asarray([triangle_raft_si_crds[i,0], triangle_raft_si_crds[i,1], 5+si_o_length])))
    #            bilayer_harmpairs = np.vstack((bilayer_harmpairs, np.asarray([[i, 3200+2*i], [i, 3200+2*i+1]])))
        # O eq
        for i in range(triangle_raft_o_crds.shape[0]):
            bilayer_o_crds = np.vstack((bilayer_o_crds, np.asarray([triangle_raft_o_crds[i,0], triangle_raft_o_crds[i,1], 5-h])))
            bilayer_o_crds = np.vstack((bilayer_o_crds, np.asarray([triangle_raft_o_crds[i,0], triangle_raft_o_crds[i,1], 5+h+2*si_o_length])))

        bilayer_crds = np.vstack((bilayer_o_crds, bilayer_si_crds))

        dict_sio2 = {}


        # Harmpairs
        # O ax
        for i in range(triangle_raft_si_crds.shape[0]):
            if i==0:
                bilayer_harmpairs = np.asarray([[i,4*n_nodes+2*i],#3200
                                                [i,4*n_nodes+1+2*i],#3201
                                                [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][0])[0]],
                                                [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][0])[1]],
                                                [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][1])[0]],
                                                [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][1])[1]],
                                                [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][2])[0]],
                                                [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][2])[1]]]
                                               )
            else:
                bilayer_harmpairs = np.vstack((bilayer_harmpairs, np.asarray([[i,4*n_nodes+2*i],#3200
                                                                              [i,4*n_nodes+1+2*i],#3201
                                                                              [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][0])[0]],
                                                                              [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][0])[1]],
                                                                              [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][1])[0]],
                                                                              [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][1])[1]],
                                                                              [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][2])[0]],
                                                                              [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][2])[1]]])))
        # Si - O cnxs
        for i in range(triangle_raft_harmpairs.shape[0]):
            atom_1 = triangle_raft_to_bilayer(triangle_raft_harmpairs[i,0])
            atom_2 = triangle_raft_to_bilayer(triangle_raft_harmpairs[i,1])

            bilayer_harmpairs = np.vstack((bilayer_harmpairs, np.asarray([[atom_1[0], atom_2[0]], [atom_1[1], atom_2[1]]])))

        for vals in dict_sio.keys():
            dict_sio2['{:}'.format(int(vals)-3*n_nodes/2 + 4*n_nodes)] = [triangle_raft_to_bilayer(dict_sio["{:}".format(vals)][i]) for i in range(3)]

        def plot_bilayer():
            plt.scatter(bilayer_si_crds[:,0], bilayer_si_crds[:,1], color='y', s=0.4)
            plt.scatter(bilayer_o_crds[:,0],  bilayer_o_crds[:,1], color='r', s=0.4)
            plt.savefig('bilayer atoms')
            plt.clf()
            plt.scatter(bilayer_si_crds[:,0], bilayer_si_crds[:,1], color='y', s=0.4)
            plt.scatter(bilayer_o_crds[:,0],  bilayer_o_crds[:,1], color='r', s=0.4)
            #for i in range(triangle_raft_harmpairs.shape[0]):
            for i in range(bilayer_harmpairs.shape[0]):
                atom_1_crds = bilayer_crds[int(bilayer_harmpairs[i,0]),:]
                atom_2_crds = bilayer_crds[int(bilayer_harmpairs[i,1]),:]
                atom_2_crds = np.add(atom_1_crds, pbc_v(atom_1_crds, atom_2_crds))
                if  int(bilayer_harmpairs[i,0]) >= 4*n_nodes or int(bilayer_harmpairs[i,1]) >= 4*n_nodes:
                    plt.plot([atom_1_crds[0], atom_2_crds[0]], [atom_1_crds[1], atom_2_crds[1]], color='k')
            plt.title('Si-O')
            plt.savefig('bilayer SiO bond')
            plt.clf()
    #        plt.show()
            plt.scatter(bilayer_si_crds[:,0], bilayer_si_crds[:,1], color='y', s=0.4)
            plt.scatter(bilayer_o_crds[:,0],  bilayer_o_crds[:,1], color='r', s=0.4)
            #for i in range(triangle_raft_harmpairs.shape[0]):
            for i in range(bilayer_harmpairs.shape[0]):
                atom_1_crds = bilayer_crds[int(bilayer_harmpairs[i,0]),:]
                atom_2_crds = bilayer_crds[int(bilayer_harmpairs[i,1]),:]
                atom_2_crds = np.add(atom_1_crds, pbc_v(atom_1_crds, atom_2_crds))
                if  int(bilayer_harmpairs[i,0]) < 4*n_nodes and int(bilayer_harmpairs[i,1]) < 4*n_nodes:
                    plt.plot([atom_1_crds[0], atom_2_crds[0]], [atom_1_crds[1], atom_2_crds[1]], color='k')
            plt.title('O-O')
            plt.savefig('bilayer OO bond')
            plt.clf()
    #        plt.show()


            plt.scatter(bilayer_si_crds[:,0], bilayer_si_crds[:,2], color='y', s=0.4)
            plt.scatter(bilayer_o_crds[:,0],  bilayer_o_crds[:,2], color='r', s=0.4)
            for i in range(bilayer_harmpairs.shape[0]):
                atom_1_crds = bilayer_crds[int(bilayer_harmpairs[i,0]),:]
                atom_2_crds = bilayer_crds[int(bilayer_harmpairs[i,1]),:]
                atom_2_crds = np.add(atom_1_crds, pbc_v(atom_1_crds, atom_2_crds))
                plt.plot([atom_1_crds[0], atom_2_crds[0]], [atom_1_crds[2], atom_2_crds[2]], color='k')

            plt.savefig('bilayer all')
            plt.clf()
    #        plt.show()
            return
#        plot_bilayer()

    #    print('Bonding Pairs')
    #    with open('pair_SiO2.txt', 'w') as f:
    #        # Si-O bonds
    #        for i in range(bilayer_harmpairs.shape[0]):
    #            if bilayer_harmpairs[i,0]>=bilayer_o_crds.shape[0] or bilayer_harmpairs[i,1]>=bilayer_o_crds.shape[0]:
    #                f.write('{:<6} {:<6} harmonic 1.001 {:<10} 100.0\n'.format(int(bilayer_harmpairs[i, 0] + 1),
    #                                                                        int(bilayer_harmpairs[i, 1] + 1),
    #                                                                        si_o_length))
    #        for i in range(bilayer_harmpairs.shape[0]):
    #            if bilayer_harmpairs[i, 0] < bilayer_o_crds.shape[0] and bilayer_harmpairs[i, 1] < bilayer_o_crds.shape[0]:
    #                f.write('{:<6} {:<6} harmonic 1.001 {:<10} 100.0\n'.format(int(bilayer_harmpairs[i, 0] + 1),
    #                                                                        int(bilayer_harmpairs[i, 1] + 1),
    #                                                                        o_o_distance))
        n_bonds = bilayer_harmpairs.shape[0]



        with open(folder+'/PARM_SiO2.lammps', 'w') as output_file:
            output_file.write('pair_style lj/cut {:}\n'.format(o_o_distance* intercept_1))
            output_file.write('pair_coeff * * 0.1 {:} {:}\n'.format(o_o_distance* intercept_1/2**(1/6), o_o_distance* intercept_1))
            output_file.write('pair_modify shift yes\n'.format())
            output_file.write('special_bonds lj 0.0 1.0 1.0\n'.format())

            output_file.write('bond_style harmonic\n')
            output_file.write('bond_coeff 2 1.001 3.0405693345182674\n')
            output_file.write('bond_coeff 1 1.001 4.965228931415713\n')

        with open(folder+'/SiO2.data', 'w') as f:
            f.write('DATA FILE Produced from netmc results (cf David Morley)\n')
            f.write('{:} atoms\n'.format(bilayer_crds.shape[0]))
        #    f.write('0 bonds\n')
            f.write('{:} bonds\n'.format(int(n_bonds)))
            f.write('0 angles\n')
            f.write('0 dihedrals\n')
            f.write('0 impropers\n')
            f.write('2 atom types\n')
            f.write('0 bond types\n')
            f.write('{:} bond types\n'.format(int(n_bond_types)))
            f.write('0 angle types\n')
            f.write('0 dihedral types\n')
            f.write('0 improper types\n')
            f.write('0.00000 {:<5} xlo xhi\n'.format(dim[0]))
            f.write('0.00000 {:<5} ylo yhi\n'.format(dim[1]))
            f.write('0.0000 200.0000 zlo zhi\n')
            f.write('\n')
            f.write('# Pair Coeffs\n')
            f.write('#\n')
            f.write('# 1  O\n')
            f.write('# 2  Si\n')
            f.write('\n')
            f.write('# Bond Coeffs\n')
            f.write('# \n')
            f.write('# 1  O-O\n')
            f.write('# 2  Si-O\n')
            f.write('# 3  O-O rep\n')
            f.write('# 4  Si-Si rep\n')
            f.write('\n')
            f.write(' Masses\n')
            f.write('\n')
            f.write('1 28.10000 # O \n')
            f.write('2 32.01000 # Si\n')
            f.write('\n')
            f.write(' Atoms # molecular\n')
            f.write('\n')

            for i in range(bilayer_si_crds.shape[0]):
                f.write('{:<4} {:<4} {:<4} {:<24} {:<24} {:<24} # Si\n'.format(int(i + 1),
                                                                        int(i + 1),
                                                                               2,
                                                                        bilayer_si_crds[i, 0],
                                                                        bilayer_si_crds[i, 1],
                                                                        bilayer_si_crds[i, 2],
                                                                               ))
            for i in range(bilayer_o_crds.shape[0]):
                f.write('{:<4} {:<4} {:<4} {:<24} {:<24} {:<24} # O\n'.format(int(i + 1 + bilayer_si_crds.shape[0]),
                                                                              int(i + 1 + bilayer_si_crds.shape[0]),
                                                                              1,
                                                                       bilayer_o_crds[i, 0],
                                                                       bilayer_o_crds[i, 1],
                                                                       bilayer_o_crds[i, 2],
                                                                              ))


            f.write('\n')
            f.write(' Bonds\n')
            f.write('\n')
            for i in range(bilayer_harmpairs.shape[0]):

                pair1 = bilayer_harmpairs[i, 0]
                if pair1 < bilayer_o_crds.shape[0]:
                    pair1_ref = pair1 + 1 + bilayer_si_crds.shape[0]
                else:
                    pair1_ref = pair1 + 1 - bilayer_o_crds.shape[0]
                pair2 = bilayer_harmpairs[i, 1]
                if pair2 < bilayer_o_crds.shape[0]:
                    pair2_ref = pair2 + 1 + bilayer_si_crds.shape[0]
                else:
                    pair2_ref = pair2 + 1 - bilayer_o_crds.shape[0]


                if bilayer_harmpairs[i,0]<bilayer_o_crds.shape[0] and  bilayer_harmpairs[i,1]<bilayer_o_crds.shape[0]:
                    f.write('{:} {:} {:} {:}\n'.format(int(i + 1), 1, int(pair1_ref), int(pair2_ref)))
                else:
                    f.write('{:} {:} {:} {:}\n'.format(int(i + 1), 2, int(pair1_ref), int(pair2_ref)))



        with open(folder+'/SiO2_harmpairs.dat', 'w') as f:
            f.write('{:}\n'.format(bilayer_harmpairs.shape[0]))
            for i in range(bilayer_harmpairs.shape[0]):
                if bilayer_harmpairs[i,0]<bilayer_o_crds.shape[0] and  bilayer_harmpairs[i,1]<bilayer_o_crds.shape[0]:
                    f.write('{:<10} {:<10}\n'.format(int(bilayer_harmpairs[i, 0] + 1), int(bilayer_harmpairs[i, 1] + 1)))
                else:
                    f.write('{:<10} {:<10}\n'.format(int(bilayer_harmpairs[i, 0] + 1), int(bilayer_harmpairs[i, 1] + 1)))

        with open(folder+'/SiO2.in', 'w') as f:
            f.write('log SiO2.log\n')
            f.write('units                   electron                                                   \n')
            f.write('dimension               3                                                          \n')
            f.write('processors              * * *                                                       \n')
            f.write('boundary                p p p                                                      \n')
            f.write('\n')
            f.write('#####################################################################              \n')
            f.write('\n')
            f.write('variable time equal 25*0.02418884326                                               \n')
            f.write('\n')
            f.write('#####################################################################              \n')
            f.write('\n')
            f.write('#read data\n')
            f.write('atom_style              molecular                                                  \n')
            f.write('read_data               Results/SiO2.data                                                  \n')
            f.write('timestep ${time}                                                                   \n')
            f.write('\n')
            f.write('#####################################################################              \n')
            f.write('\n')
            f.write('#potential                                                                         \n')
            f.write('include                 Results/PARM_SiO2.lammps                                                \n')
            f.write('\n')
            f.write('#####################################################################              \n')
    #        f.write('\n')
    #        f.write('bond_write 1 50 2.0 6.0 OO_bond.dat OO_bond                                        \n')
    #        f.write('bond_write 2 50 2.0 6.0 SiO_bond.dat SiO_bond                                    \n')
    #        f.write('bond_write 3 50 2.0 6.0 pair_1.dat pair_1                                    \n')
    #        f.write('\n')
    #        f.write('#####################################################################              \n')
            f.write('\n')
            f.write('#outputs                                                                           \n')
            f.write('thermo                  0                                                       \n')
            f.write('thermo_style            custom step pe ke epair ebond etotal vol temp              \n')
            f.write('\n')
            f.write('#####################################################################              \n')
            f.write('\n')
            f.write('dump                    1 all custom 1000000000 SiO2_dump.lammpstrj id element type x y z     \n')
            f.write('dump_modify             1 element O Si                                             \n')
            f.write('thermo_modify           line yaml                                                  \n')
            f.write('\n')
            f.write('#####################################################################              \n')
            f.write('\n')
            f.write('#initial minimisation                                                              \n')
            f.write('\n')
            #f.write('min_style               cg                                                         \n')
            #f.write('minimize        1.0e-6 1.0e-6 1000000 10000000                                       \n')
            #f.write('\n')
            f.write('min_style               sd                                                         \n')
            f.write('minimize        1.0e-6 1.0e-6 1000000 10000000                                       \n')
            f.write('\n')
            f.write('#####################################################################              \n')
    #        f.write('\n')
    #        f.write('fix                            1 all nvt temp 0.0000001 0.0000001 1                \n')
    #        f.write('\n')
    #        f.write('#####################################################################              \n')
    #        f.write('\n')
    #        f.write('run                             1000                                               \n')
    #        f.write('unfix                   1                                                          \n')
    #        f.write('\n')
    #        f.write('#####################################################################              \n')
            f.write('\n')
            f.write('#write_data              SiO2_results.dat                                              \n')
            f.write('#write_restart  C_results.rest                                                     \n')

    ############################################################################

    print('Finished')
    return



if __name__ == '__main__':
    draw_line_widget = DrawLineWidget()
#    draw_line_widget.init()

    while True:
        cv2.imshow('image', draw_line_widget.show_image())
        key = cv2.waitKey(1)






#    while True:
#        cv2.imshow('image', draw_line_widget.show_image())
#        key = cv2.waitKey(1)
#
#        # Close program with keyboard 'q'
#        if key == ord('q'):
#            cv2.destroyAllWindows()
#
#
#
#
#            print(nodes)
#
#
#            for node in nodes.keys():
#                nodes[node]['cnxs'] = list(dict.fromkeys(nodes[node]['cnxs']))
#
#
#            for i in range(len(list_x)):
#                plt.plot(list_x[i], list_y[i])
#            plt.show()
#
#            for node in nodes.keys():
#                crds = nodes['{:}'.format(node)]['crds']
#                plt.scatter(crds[0], crds[1], color='r')
#                for cnx in nodes['{:}'.format(node)]['cnxs']:
#                    crds_1 = nodes['{:}'.format(cnx)]['crds']
#                    plt.plot([crds[0], crds_1[0]], [crds[1], crds_1[1]])
#            plt.show()
#
#            G = nx.Graph()
#            for node in nodes.keys():
##                if len(nodes[node]['cnxs'])>2:
#                G.add_node(node, pos=nodes[node]['crds'])
#            for node in nodes.keys():
##                if len(nodes[node]['cnxs'])>2:
#                for cnx in nodes[node]['cnxs']:
#                    G.add_edge(node, '{:}'.format(cnx))
#
#            H = nx.Graph()
#            rings = {}
#            ring_sizes = []
#            ring_count = 0
#            for c in nx.minimum_cycle_basis(G):
#                crd_x = []
#                crd_y = []
##                H.add_node('{:}'.format(ring_count), pos=[])
#                ring_sizes.append(len(c))
#                for node in c:
#                    nodes[node]['rings'].append(ring_count)
#                    crd_x.append(nodes[node]['crds'][0])
#                    crd_y.append(nodes[node]['crds'][1])
#                    crds = np.add(crds, nodes[node]['crds'])
#                print('crds : ', crds)
#                crds = np.divide(crds,len(c))
#                print('--', crds)
#                alt_crds = np.array([np.mean(crd_x), np.mean(crd_y)])
#                plt.scatter(crd_x, crd_y)
#                for k in range(len(crd_x)):
#                   plt.plot([crd_x[k-1], crd_x[k]], [crd_y[k-1], crd_y[k]])
#                plt.scatter(alt_crds[0], alt_crds[1])
#                #plt.show()
#
#                H.add_node('{:}'.format(ring_count), pos=alt_crds)
#                rings['{:}'.format(ring_count)] = {}
#                rings['{:}'.format(ring_count)]['crds'] = alt_crds
#                rings['{:}'.format(ring_count)]['cnxs'] = []
#                rings['{:}'.format(ring_count)]['net'] = c
#
#                ring_count += 1
#
#
#            plt.show()
#
#            for node in nodes.keys():
#                if len(nodes[node]['rings'])>1:
#                    ring_list =  nodes[node]['rings']
#                    for i in range(len(ring_list)-1):
#                        for j in range(i+1, len(ring_list)):
#                            ring_i = ring_list[i]
#                            ring_j = ring_list[j]
#
#                            if ring_j not in rings['{:}'.format(ring_i)]['cnxs'] and ring_i != ring_j:
#                                rings['{:}'.format(ring_i)]['cnxs'].append(ring_j)
#                            if ring_i not in rings['{:}'.format(ring_j)]['cnxs'] and ring_i != ring_j:
#                                rings['{:}'.format(ring_j)]['cnxs'].append(ring_i)
#
#            for ring in rings.keys():
#                for cnx in rings[ring]['cnxs']:
#                    H.add_edge(ring, '{:}'.format(cnx))
#            nx.draw(H)
#            plt.show()
#
#            print('\n\n\n########################\n')
#
#            print('< x > : ', np.mean(ring_sizes))
#            print('< x2> : ', np.var(ring_sizes))
#            print('assort: ', nx.degree_assortativity_coefficient(G))
#
#
#
#            print(nodes)
#            print(ring_sizes)
##            print([sorted(c) for c in nx.minimum_cycle_basis(G)])
#
#
#
#            nx.draw(G)
#            plt.show()
#
#
#
##            equivalent_nodes = []
##            for node_0 in range(len(nodes.keys())1):
##                for node_1 in range(node_0, len(nodes.keys())):
##                    print(node_0, node_1)
##
###                    print(nodes['{:}'.format(node_0)]['cnxs'])
##                    if int(nodes['{:}'.format(node_0)]['cnxs']) != node_1:
##                        r = np.linalg.norm(np.subtract(nodes['{:}'.format(node_0)]['crds'], nodes['{:}'.format(node_1)]['crds']))
##                        if r<5:
##                            equivalent_nodes.append(np.array([node_0,node_1]))
##            for i in range(len(equivalent_nodes)):
##                print(nodes['{:}'.format(equivalent_nodes[i][0])]['crds'])
##                crds_0 = nodes['{:}'.format(equivalent_nodes[i][0])]['crds']
##                crds_1 = nodes['{:}'.format(equivalent_nodes[i][1])]['crds']
##
##                plt.scatter(crds_0[0],crds_0[1])
##                plt.scatter(crds_1[0],crds_1[1])
##            plt.show()
##            for i in range(len(equivalent_nodes)):
##                print(nodes['{:}'.format(equivalent_nodes[i][0])]['crds'])
##                crds_0 = nodes['{:}'.format(equivalent_nodes[i][0])]['crds']
##                crds_1 = nodes['{:}'.format(equivalent_nodes[i][1])]['crds']
##
##                plt.scatter(crds_0[0],crds_0[1])
##                plt.scatter(crds_1[0],crds_1[1])
##
##            for i in range(len(list_x)):
##                plt.plot(list_x[i], list_y[i])
##
##
##            plt.show()
##
##
##            #####################################
##
##            equivalent_array = np.vstack(equivalent_nodes)
##
##            equivalent_dict = {}
##            count = 0
##            for i in range(len(equivalent_nodes)):
##                node_0 = equivalent_nodes[i][0]
##                node_1 = equivalent_nodes[i][1]
##                if '0' not in equivalent_dict:
##                    equivalent_dict['0'] = []
##                    equivalent_dict['0'].append(node_0)
##                    equivalent_dict['0'].append(node_1)
##                    count +=1
##                else:
##                    found = False
##                    for equivalent_points in equivalent_dict.keys():
##                        if node_0 in equivalent_dict[equivalent_points]:
##                            equivalent_dict[equivalent_points].append(node_1)
##                            found = True
##                        elif node_1 in equivalent_dict[equivalent_points]:
##                            equivalent_dict[equivalent_points].append(node_0)
##                            found = True
##                    if found == False:
##                        equivalent_dict['{:}'.format(count)] = []
##                        equivalent_dict['{:}'.format(count)].append(node_0)
##                        equivalent_dict['{:}'.format(count)].append(node_1)
##                        count +=1
##
##
##            print(equivalent_dict)
#
##            unique_nodes = {}
##            for node in nodes.keys():
##                if int(node) not in equivalent_array[:,0] and int(node) not in equivalent_array[:,1]:
##                    print(node, ' -- unique')
###                    if '{:}'.format(0) not in unique_nodes.keys():
###                        unique_nodes['{:}
##                else:
##                    print(node, ' -- duplicate')
##                    if '{:}'.format(0) not in unique_nodes.keys():
##                       node_0 = 0
##                    else:
##                       node_0 = len(unique_nodes.keys())
##
###                equivalent_node_0 = np.where()
##
##                unique_nodes['{:}'.format(node_0)] = {}
##
##                unique_nodes['{:}'.format(node_0)]['crds'] = np.average(nodes)
##
##
##                unique_nodes['{:}'.format(node_0)]['cnxs'] = []
##                unique_nodes['{:}'.format(node_0)]['cnxs'].append()
#
#
#            #####################################
#
#            crd_list = []
#            for node in nodes.keys():
#                crd_list.append(nodes[node]['crds'])
#            crds = np.vstack(crd_list)
#
#            dim_x = [min(crds[:,0]), max(crds[:,0])]
#            dim_y = [min(crds[:,1]), max(crds[:,1])]
#
#            reduced_dim_x = dim_x[1] - dim_x[0] + 1
#            reduced_dim_y = dim_y[1] - dim_y[0] + 1
#            print('########### NEW DIMS ##############')
#            print(reduced_dim_x, reduced_dim_y)
#
#            for node in nodes.keys():
#                print('initial : ', nodes[node]['crds'])
#                nodes[node]['crds'] = np.subtract(nodes[node]['crds'], np.array([dim_x[0], dim_y[0]]))
#                print('final   : ', nodes[node]['crds'])
#                print('\n')
#
#
#            for ring in rings.keys():
#                rings[ring]['crds'] = np.subtract(rings[ring]['crds'], np.array([dim_x[0], dim_y[0]]))
#
#
#
#
#            with open('test_A_aux.dat', 'w') as f:
#                node_coordination_stats = []
#                for node in nodes.keys():
#                    node_coordination_stats.append(len(nodes[node]['cnxs']))
#                f.write('{:}\n'.format(len(nodes.keys())))
#                f.write('{:<10} {:<10}\n'.format(min(node_coordination_stats), max(node_coordination_stats)))
#                f.write('2DE\n')
#                f.write('{:<10} {:<10}\n'.format(reduced_dim_x, reduced_dim_y))
#                f.write('{:<10} {:<10}\n'.format(float(1.0/reduced_dim_x), float(1.0/reduced_dim_y)))
#
#
#            with open('test_A_crds.dat', 'w') as f:
#                for node in nodes.keys():
#                    f.write('{:<10}{:<10}\n'.format(nodes[node]['crds'][0],nodes[node]['crds'][1]))
#
#            with open('test_A_net.dat', 'w') as f:
#                for node in nodes.keys():
#                    for j in nodes[node]['cnxs']:
#                        f.write('{:<10}'.format(j))
#                    f.write('\n')
#            with open('test_A_dual.dat', 'w') as f:
#                for node in nodes.keys():
#                    for j in nodes[node]['rings']:
#                        f.write('{:<10}'.format(j))
#                    f.write('\n')
#
#            #####################################
#
#
#            with open('test_B_aux.dat', 'w') as f:
#                ring_coordination_stats = []
#                for ring in rings.keys():
#                    ring_coordination_stats.append(len(rings[ring]['cnxs']))
#                f.write('{:}\n'.format(len(rings.keys())))
#                f.write('{:<10} {:<10}\n'.format(min(ring_coordination_stats), max(ring_coordination_stats)))
#                f.write('2DE\n')
#                f.write('{:<10} {:<10}\n'.format(reduced_dim_x, reduced_dim_y))
#                f.write('{:<10} {:<10}\n'.format(float(1.0/reduced_dim_x), float(1.0/reduced_dim_y)))
#
#
#
#            with open('test_B_crds.dat', 'w') as f:
#                for ring in rings.keys():
#                    f.write('{:.8f}  {:.8f}\n'.format(rings[ring]['crds'][0], rings[ring]['crds'][1],))
#
#            with open('test_B_net.dat', 'w') as f:
#                for ring in rings.keys():
#                    for j in rings[ring]['cnxs']:
#                        f.write('{:<10}'.format(j))
#                    f.write('\n')
#            with open('test_B_dual.dat', 'w') as f:
#                for ring in rings.keys():
#                    for j in rings[ring]['net']:
#                        f.write('{:<10}'.format(j))
#                    f.write('\n')
#
#
#
#
#
#
#
#            exit(1)
#
#
#
