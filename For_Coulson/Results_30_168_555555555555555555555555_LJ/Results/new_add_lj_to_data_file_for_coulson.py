import numpy as np
import matplotlib.pyplot as plt
def make_crds_marks_bilayer():
    Delete_Files = True
#    with open('area.dat', 'r') as f:
#        array = np.genfromtxt(f)
#    area = float(array[0])
#    intercept_1 = int(array[1])
#    intercept_2 = int(array[2])
    area = 1.00
    intercept_1 = 1
    intercept_2 = 1


    AREA_SCALING  = np.sqrt(area)
    UNITS_SCALING = 1/0.52917721090380
    si_si_distance      = UNITS_SCALING * 1.609 * np.sqrt((32.0 / 9.0))
    si_o_distance       = UNITS_SCALING * si_si_distance / 2.0
    si_o_length         = UNITS_SCALING * 1.609
    o_o_distance        = UNITS_SCALING * 1.609 * np.sqrt((8.0 / 3.0))
    h                   = UNITS_SCALING * np.sin((19.5 / 180) * np.pi) * 1.609


    displacement_vectors_norm       = np.asarray([[1,0], [-0.5, np.sqrt(3)/2], [-0.5, -np.sqrt(3)/3]])
    displacement_vectors_factored   = np.multiply(displacement_vectors_norm, 0.5)

    with open('test_A_aux.dat', 'r') as f:
        n_nodes = np.genfromtxt(f, max_rows=1)
        n_nodes = int(n_nodes)
    with open('test_A_aux.dat', 'r') as f:
        dims = np.genfromtxt(f, skip_header=3, skip_footer=1)
        dim_x, dim_y = dims[0], dims[1]
    C_dim_x = dim_x
    C_dim_y = dim_y
    dim_x *= si_si_distance*AREA_SCALING
    dim_y *= si_si_distance*AREA_SCALING
    dim = np.array([dim_x, dim_y, 30])
    with open('test_A_net.dat', 'r') as f:
        net = np.genfromtxt(f)

    with open('test_A_crds.dat', 'r') as f:
        node_crds = np.genfromtxt(f)

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
    monolayer_crds = np.multiply(node_crds, AREA_SCALING)

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
        plt.scatter(monolayer_crds[:,0], monolayer_crds[:,1], color='k')
        for i in range(100):
            atom_1_crds = monolayer_crds[int(monolayer_harmpairs[i,0]),:]
            atom_2_crds = monolayer_crds[int(monolayer_harmpairs[i,1]),:]
            atom_2_crds = np.add(atom_1_crds, pbc_v(atom_1_crds, atom_2_crds))
            plt.plot([atom_1_crds[0], atom_2_crds[0]], [atom_1_crds[1], atom_2_crds[1]], color='k')
        plt.show()
        print('plotting...?')

    with open('PARM_Si.lammps', 'w') as f:
        f.write('bond_style harmonic        \n')
        f.write('bond_coeff 1 {:<.4f} {:}  \n'.format(0.801,1.00))
        f.write('angle_style cosine/squared       \n')
        f.write('angle_coeff 1 0.2001 120   \n')

    with open('Si.data', 'w') as f:
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
        f.write('0.00000 {:<5} xlo xhi\n'.format(C_dim_x))
        f.write('0.00000 {:<5} ylo yhi\n'.format(C_dim_y))
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
        f.write('1 32.01000 # Si\n')
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

    with open('Si.in', 'w') as f:
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
        f.write('read_data               Results/Si.data                                                  \n')
        f.write('timestep ${time}                                                                   \n')
        f.write('\n')
        f.write('#####################################################################              \n')
        f.write('\n')
        f.write('#potential                                                                         \n')
        f.write('include                 Results/PARM_Si.lammps                                                \n')
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
        f.write('thermo                  1000                                                       \n')
        f.write('thermo_style            custom step pe ke epair ebond etotal vol temp              \n')
        f.write('\n')
        f.write('#####################################################################              \n')
        f.write('\n')
        f.write('dump                    1 all custom 1000 Si_dump.lammpstrj id element type x y z     \n')
        f.write('dump_modify             1 element Si                                             \n')
        f.write('thermo_modify           line yaml                                                  \n')
        f.write('\n')
        f.write('#####################################################################              \n')
        f.write('\n')
        f.write('#initial minimisation                                                              \n')
        f.write('\n')
        f.write('min_style               cg                                                         \n')
        f.write('minimize        1.0e-6 0.0 1000000 10000000                                       \n')
        f.write('\n')
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
    ## Triangle Raft
    monolayer_crds = np.multiply(monolayer_crds, si_si_distance)
    triangle_raft_si_crds = monolayer_crds
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
        plt.show()
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

        plt.show()
    plot_triangle_raft()
    print('#########################################')
    print('Triangle Raft')
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
#     if intercept_2==1:
#         print('Si LJ Pairs')
#         with open('lj_si_Si2O3.txt', 'w') as f:
#             # O - O bonds
#             for i in range(triangle_raft_si_crds.shape[0]-1):
#                 for j in range(i+1, triangle_raft_si_crds.shape[0]):
#                     atom_1_crds = triangle_raft_si_crds[i, :]
#                     atom_2_crds = triangle_raft_si_crds[j, :]
#                     r_ij = np.linalg.norm(pbc_v(atom_1_crds, atom_2_crds))
#                     if r_ij < 15.0:
#                         f.write('{:<6} {:<6}  \n'.format(i+1+triangle_raft_o_crds.shape[0],j+1+triangle_raft_o_crds.shape[0], ))
#         with open('lj_si_Si2O3.txt', 'r') as lj_si:
#             lj_si_array = np.genfromtxt(lj_si)
#         n_bonds += lj_si_array.shape[0]
#     if intercept_1==1:
#         print('O LJ Pairs')
#         with open('lj_o_Si2O3.txt', 'w') as f:
#             # O - O bonds
#             for i in range(triangle_raft_o_crds.shape[0]-1):
#
#                 atom_1_crds = triangle_raft_o_crds[i, :]
#
#                 bonds = []
#                 cnxs = np.where(triangle_raft_harmpairs==i)[0]
#                 for cnx in cnxs:
#                     cnx = int(cnx)
#                     for val in range(2):
#                         if int(triangle_raft_harmpairs[cnx,val]) != i:
#                             bonds.append(int(triangle_raft_harmpairs[cnx,val]))
#     #            print(bonds)
#
#                 for j in range(i+1, triangle_raft_o_crds.shape[0]):
#
#                     if j not in bonds:
#
#
#                         atom_2_crds = triangle_raft_o_crds[j, :]
#                         r_ij = np.linalg.norm(pbc_v(atom_1_crds, atom_2_crds))
#                         if r_ij < 15.0:
#                             f.write('{:<6} {:<6} \n'.format(i+1,j+1, ))
#         with open('lj_o_Si2O3.txt', 'r') as lj_o:
#             lj_o_array = np.genfromtxt(lj_o)
#         n_bonds+=lj_o_array.shape[0]
#         print('created list')
# #    t1 = time.time()

#    list_lj_si_Si2O3 = []
#    for i in range(triangle_raft_si_crds.shape[0] - 1):
#        for j in range(i + 1, triangle_raft_si_crds.shape[0]):
#            atom_1_crds = triangle_raft_si_crds[i, :]
#            atom_2_crds = triangle_raft_si_crds[j, :]
#            r_ij = np.linalg.norm(pbc_v(atom_1_crds, atom_2_crds))
#            if r_ij < 15.0:
#                list_lj_si_Si2O3.append(np.array([i + 1, j + 1]))
#    lj_si_array_new = np.array(list_lj_si_Si2O3)
#    list_lj_o_Si2O3 = []
#    for i in range(triangle_raft_o_crds.shape[0] - 1):
#        atom_1_crds = triangle_raft_o_crds[i, :]
#        bonds = []
#        cnxs = np.where(triangle_raft_harmpairs == i)[0]
#        for cnx in cnxs:
#            cnx = int(cnx)
#            for val in range(2):
#                if int(triangle_raft_harmpairs[cnx, val]) != i:
#                    bonds.append(int(triangle_raft_harmpairs[cnx, val]))
#        for j in range(i + 1, triangle_raft_o_crds.shape[0]):
#
#            if j not in bonds:
#
#                atom_2_crds = triangle_raft_o_crds[j, :]
#                r_ij = np.linalg.norm(pbc_v(atom_1_crds, atom_2_crds))
#                if r_ij < 15.0:
#                    list_lj_o_Si2O3.append(np.array([i + 1, j + 1]))
#    lj_o_array_new = np.array(list_lj_o_Si2O3)
#
#    t2 = time.time()
#
#    print('Initial Method : ', t1-t0)
#    print('Array Method   : ', t2-t1)
#    print((lj_si_array_new==lj_si_array).all())
#    print((lj_o_array_new==lj_o_array).all())

    n_bond_types = 2+intercept_1+intercept_2

    with open('Si2O3.in', 'w') as f:
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
        f.write('thermo                  10000000                                                       \n')
        f.write('thermo_style            custom step pe ke epair ebond etotal vol temp              \n')
        f.write('\n')
        f.write('#####################################################################              \n')
        f.write('\n')
        f.write('dump                    1 all custom 10000000000 Si2O3_dump.lammpstrj id element type x y z     \n')
        f.write('dump_modify             1 element O Si                                             \n')
        f.write('thermo_modify           line yaml                                                  \n')
        f.write('\n')
        f.write('#####################################################################              \n')
        f.write('\n')
        f.write('#initial minimisation                                                              \n')
        f.write('\n')
        #f.write('min_style               cg                                                         \n')
        #f.write('minimize        1.0e-6 1.0e-6 1000000 10000000                                       \n')
        f.write('\n')
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

    with open('PARM_Si2O3.lammps', 'w') as output_file:

        output_file.write('pair_style lj/cut {:}\n'.format(float(4.9624*intercept_2)))
        output_file.write('pair_coeff * * 0.1 {:} {:}\n'.format(float(4.9624*intercept_2/(2**(1/6))), float(4.9624*intercept_2)))
        output_file.write('pair_modify shift yes\n')
        output_file.write('special_bonds lj 0.0 1.0 1.0\n')

        output_file.write('\n')
        output_file.write('\n')
        output_file.write('bond_style harmonic\n')
        output_file.write('bond_coeff 2 1.001 2.86667626014\n')
        output_file.write('bond_coeff 1 1.001 4.965228931415713\n')

    with open('Si2O3.data', 'w') as f:
        f.write('DATA FILE Produced from netmc results (cf David Morley)\n')
        f.write('{:} atoms\n'.format(triangle_raft_crds.shape[0]))
        f.write('{:} bonds\n'.format(int(n_bonds)))
        #f.write('0 bonds\n'.format(triangle_raft_harmpairs.shape[0]))
        f.write('0 angles\n')
        f.write('0 dihedrals\n')
        f.write('0 impropers\n')
        f.write('2 atom types\n')
        f.write('2 bond types\n')
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


        f.write('\n')


        #        f.write('\n')
        #        f.write(' PairIJ Coeffs # harmonic/cut \n')
        #        f.write('\n')
        #        for i in range(triangle_raft_crds.shape[0]-1):
        #            for j in range(i+1, triangle_raft_crds.shape[0]):
        #                f.write('{:<6} {:<6} 1.001 4.9652\n'.format(i+1,j+1))

        #        for i in range(triangle_raft_o_harmpairs.shape[0]):
        #            f.write('{:} {:} {:} {:}\n'.format(int(i + 1), 1, int(triangle_raft_o_harmpairs[i, 0]+1), int(triangle_raft_o_harmpairs[i, 1]+1)))
        #        for i in range(triangle_raft_si_harmpairs.shape[0]):
        #            f.write('{:} {:} {:} {:}\n'.format(int(i + 1 + triangle_raft_o_harmpairs.shape[0]), 2, int(triangle_raft_si_harmpairs[i, 0]+1), int(triangle_raft_si_harmpairs[i, 1]+1)))

        f.write('\n')
    with open('Si2O3_harmpairs.dat', 'w') as f:
        f.write('{:}\n'.format(triangle_raft_harmpairs.shape[0]))
        for i in range(triangle_raft_harmpairs.shape[0]):
            if triangle_raft_harmpairs[i,0]<triangle_raft_o_crds.shape[0] and triangle_raft_harmpairs[i,1]<triangle_raft_o_crds.shape[0]:
                f.write('{:<10} {:<10} \n'.format(int(triangle_raft_harmpairs[i, 0] + 1),
                                                   int(triangle_raft_harmpairs[i, 1] + 1)))
            else:
                f.write('{:<10} {:<10} \n'.format(int(triangle_raft_harmpairs[i, 0] + 1),
                                                   int(triangle_raft_harmpairs[i, 1] + 1)))
    ############################################################################

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
            bilayer_harmpairs = np.asarray([[i,4*n_nodes+2*i],
                                            [i,4*n_nodes+1+2*i],
                                            [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][0])[0]],
                                            [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][0])[1]],
                                            [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][1])[0]],
                                            [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][1])[1]],
                                            [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][2])[1]],
                                            [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][2])[1]]]
                                           )
        else:
            bilayer_harmpairs = np.vstack((bilayer_harmpairs, np.asarray([[i,4*n_nodes+2*i],
                                                                          [i,4*n_nodes+1+2*i],
                                                                          [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][0])[0]],
                                                                          [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][0])[1]],
                                                                          [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][1])[0]],
                                                                          [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][1])[1]],
                                                                          [i, triangle_raft_to_bilayer(dict_sio['{:}'.format(int(3 * n_nodes / 2 + i))][2])[1]],
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
        plt.show()
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
        plt.show()
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
        plt.show()


        plt.scatter(bilayer_si_crds[:,0], bilayer_si_crds[:,2], color='y', s=0.4)
        plt.scatter(bilayer_o_crds[:,0],  bilayer_o_crds[:,2], color='r', s=0.4)
        for i in range(bilayer_harmpairs.shape[0]):
            atom_1_crds = bilayer_crds[int(bilayer_harmpairs[i,0]),:]
            atom_2_crds = bilayer_crds[int(bilayer_harmpairs[i,1]),:]
            atom_2_crds = np.add(atom_1_crds, pbc_v(atom_1_crds, atom_2_crds))
            plt.plot([atom_1_crds[0], atom_2_crds[0]], [atom_1_crds[2], atom_2_crds[2]], color='k')

        plt.show()
        return
    #plot_bilayer()
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print('Bilayer')
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
    #
    # if intercept_2==1:
    #     print('Si LJ Pairs')
    #     with open('lj_si_SiO2.txt', 'w') as f:
    #         # O - O bonds
    #         for i in range(bilayer_si_crds.shape[0] - 1):
    #             for j in range(i + 1, bilayer_si_crds.shape[0]):
    #                 atom_1_crds = bilayer_si_crds[i, :]
    #                 atom_2_crds = bilayer_si_crds[j, :]
    #                 r_ij = np.linalg.norm(pbc_v(atom_1_crds, atom_2_crds))
    #                 if r_ij < 15.0:
    #                     f.write('{:<6} {:<6}  \n'.format(i + 1 + bilayer_o_crds.shape[0], j + 1 + bilayer_o_crds.shape[0], ))
    #     with open('lj_si_SiO2.txt', 'r') as lj_si:
    #         lj_si_array = np.genfromtxt(lj_si)
    #     n_bonds += lj_si_array.shape[0]
    # if intercept_1==1:
    #     print('O LJ Pairs')
    #     with open('lj_o_SiO2.txt', 'w') as f:
    #         # O - O bonds
    #         for i in range(bilayer_o_crds.shape[0] - 1):
    #
    #             atom_1_crds = bilayer_o_crds[i, :]
    #
    #             bonds = []
    #             cnxs = np.where(bilayer_harmpairs == i)[0]
    #             for cnx in cnxs:
    #                 cnx = int(cnx)
    #                 for val in range(2):
    #                     if int(bilayer_harmpairs[cnx, val]) != i:
    #                         bonds.append(int(bilayer_harmpairs[cnx, val]))
    #             #            print(bonds)
    #
    #             for j in range(i + 1, bilayer_o_crds.shape[0]):
    #
    #                 if j not in bonds:
    #
    #                     atom_2_crds = bilayer_o_crds[j, :]
    #                     r_ij = np.linalg.norm(pbc_v(atom_1_crds, atom_2_crds))
    #                     if r_ij < 15.0:
    #                         f.write('{:<6} {:<6} \n'.format(i + 1, j + 1, ))
    #     print('created list')
    #     with open('lj_o_SiO2.txt', 'r') as lj_o:
    #         lj_o_array = np.genfromtxt(lj_o)
    #     n_bonds += lj_o_array.shape[0]

    with open('SiO2.data', 'w') as f:
        f.write('DATA FILE Produced from netmc results (cf David Morley)\n')
        f.write('{:} atoms\n'.format(bilayer_crds.shape[0]))
    #    f.write('0 bonds\n')
        f.write('{:} bonds\n'.format(int(n_bonds)))
        f.write('0 angles\n')
        f.write('0 dihedrals\n')
        f.write('0 impropers\n')
        f.write('2 atom types\n')
        f.write('0 bond types\n')
        f.write('2 bond types\n')
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
        for i in range(bilayer_o_crds.shape[0]):
            f.write('{:<4} {:<4} {:<4} {:<24} {:<24} {:<24} # O\n'.format(int(i + 1), int(i + 1), 1,
                                                                   bilayer_o_crds[i, 0],
                                                                   bilayer_o_crds[i, 1],
                                                                   bilayer_o_crds[i, 2],
                                                                          ))
        for i in range(bilayer_si_crds.shape[0]):
            f.write('{:<4} {:<4} {:<4} {:<24} {:<24} {:<24} # Si\n'.format(int(i + 1 + bilayer_o_crds.shape[0]),
                                                                    int(i + 1 + bilayer_o_crds.shape[0]), 2,
                                                                    bilayer_si_crds[i, 0],
                                                                    bilayer_si_crds[i, 1],
                                                                    bilayer_si_crds[i, 2],
                                                                           ))

        f.write('\n')
        f.write(' Bonds\n')
        f.write('\n')
        for i in range(bilayer_harmpairs.shape[0]):
            if bilayer_harmpairs[i,0]<bilayer_o_crds.shape[0] and  bilayer_harmpairs[i,1]<bilayer_o_crds.shape[0]:
                f.write('{:} {:} {:} {:}\n'.format(int(i + 1), 1, int(bilayer_harmpairs[i, 0] + 1), int(bilayer_harmpairs[i, 1] + 1)))
            else:
                f.write('{:} {:} {:} {:}\n'.format(int(i + 1), 2, int(bilayer_harmpairs[i, 0] + 1), int(bilayer_harmpairs[i, 1] + 1)))
        # if intercept_2==1 and intercept_1==1:
        #     for i in range(lj_si_array.shape[0]):
        #         f.write('{:} {:} {:} {:}\n'.format(int(i+1+bilayer_harmpairs.shape[0]),4,int(lj_si_array[i,0]), int(lj_si_array[i,1])))
        # elif intercept_2==1 and intercept_1==0:
        #     for i in range(lj_si_array.shape[0]):
        #         f.write('{:} {:} {:} {:}\n'.format(int(i+1+bilayer_harmpairs.shape[0]),3,int(lj_si_array[i,0]), int(lj_si_array[i,1])))
        # if intercept_1==1:
        #     for i in range(lj_o_array.shape[0]):
        #         f.write('{:} {:} {:} {:}\n'.format(int(i+1+bilayer_harmpairs.shape[0]+lj_si_array.shape[0]),3,int(lj_o_array[i,0]), int(lj_o_array[i,1])))
        #     f.write('\n')

    with open('SiO2_harmpairs.dat', 'w') as f:
        f.write('{:}\n'.format(bilayer_harmpairs.shape[0]))
        for i in range(bilayer_harmpairs.shape[0]):
            if bilayer_harmpairs[i,0]<bilayer_o_crds.shape[0] and  bilayer_harmpairs[i,1]<bilayer_o_crds.shape[0]:
                f.write('{:<10} {:<10}\n'.format(int(bilayer_harmpairs[i, 0] + 1), int(bilayer_harmpairs[i, 1] + 1)))
            else:
                f.write('{:<10} {:<10}\n'.format(int(bilayer_harmpairs[i, 0] + 1), int(bilayer_harmpairs[i, 1] + 1)))

    with open('PARM_SiO2.lammps', 'w') as output_file:
        output_file.write('pair_style lj/cut {:}\n'.format(float(4.9624 * intercept_2)))
        output_file.write('pair_coeff * * 0.1 {:} {:}\n'.format(float(4.9624 * intercept_2 / (2 ** (1 / 6))),
                                                      float(4.9624 * intercept_2)))
        output_file.write('pair_modify shift yes\n')
        output_file.write('special_bonds lj 0.0 1.0 1.0\n')

        output_file.write('\n')
        output_file.write('\n')
        output_file.write('bond_style harmonic\n')
        output_file.write('bond_coeff 2 1.001 3.0405693345182674\n')
        output_file.write('bond_coeff 1 1.001 4.965228931415713\n')


    with open('SiO2.in', 'w') as f:
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
        f.write('\n')
        #f.write('bond_write 1 50 2.0 6.0 OO_bond.dat OO_bond                                        \n')
        #f.write('bond_write 2 50 2.0 6.0 SiO_bond.dat SiO_bond                                    \n')
        #f.write('bond_write 3 50 2.0 6.0 pair_1.dat pair_1                                    \n')
        f.write('\n')
        f.write('#####################################################################              \n')
        f.write('\n')
        f.write('#outputs                                                                           \n')
        f.write('thermo                  100000                                                       \n')
        f.write('thermo_style            custom step pe ke epair ebond etotal vol temp              \n')
        f.write('\n')
        f.write('#####################################################################              \n')
        f.write('\n')
        f.write('dump                    1 all custom 100000 SiO2_dump.lammpstrj id element type x y z     \n')
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


    return

make_crds_marks_bilayer()










