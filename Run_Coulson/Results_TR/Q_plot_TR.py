import numpy as np
import matplotlib.pyplot as plt

count_r = 0
count_b = 0
for T in range(1000,3001,1000):
    for S in range(10,16,1):
        folder = 'T_-{:}/S_{:}/2500/'.format(T, S)
        folder_name = folder+'Run'
        with open(folder_name+'/Q_TR_engtot.out', 'r') as f:
           q_tr_array = np.genfromtxt(f)
        with open(folder_name+'/test_e_compare.out', 'r') as f:
           e_array = np.genfromtxt(f)
#        plt.scatter(10**(-T/1000), array[2])
        if count_r==0:
            plt.scatter(q_tr_array[2], e_array[-1,3], color='b', label='Triangle Raft')
        else:
            plt.scatter(q_tr_array[2], e_array[-1,3], color='b')
        count_r += 1
plt.legend()
plt.show()



