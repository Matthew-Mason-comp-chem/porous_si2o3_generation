import numpy as np
import matplotlib.pyplot as plt

# test 1 do the numbers in test_Si2O3_net correspond to row number in test_Si203_crds

crds = np.genfromtxt("pore_30_1232_1000_37_10000_example/Run/test_Si2O3_crds.dat")

net = np.genfromtxt("pore_30_1232_1000_37_10000_example/Run/test_Si2O3_net.dat", max_rows=1232, dtype=int)


print(net, net[1, 0])


for atom in net[1]:
    crd = crds[atom]

    print(crd)


# lets assume row 1 means that atom is bonded to numbers in file

row_1 = net[1]

for atom in row_1:
    crd = crds[atom]
    plt.scatter(crd[0], crd[1], color="black")

row_1_crds = crds[0]

plt.scatter(row_1_crds[0], row_1_crds[1], color="blue")

plt.show()


#for sets in net:
#    for s in sets:
#        crd = crds[s]
#        plt.scatter(crd[0], crd[1], marker='o', color='blue')
#
#plt.show()
