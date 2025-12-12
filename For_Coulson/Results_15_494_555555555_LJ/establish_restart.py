import numpy as np
import os
import shutil

with open('netmc.inpt', 'r') as f:
    skip = f.readline()
    FinalFolder = f.readline().strip().split()
    skip = f.readline()
    skip = f.readline()
    skip = f.readline()
    InitialFolder = f.readline().strip().split()

InitialFolder = InitialFolder[0][2:]
FinalFolder   = FinalFolder[0][2:]

print(InitialFolder)
print(FinalFolder)

if os.path.isfile(InitialFolder+"/fixed_rings.dat")==True:
    shutil.copyfile(InitialFolder+"/fixed_rings.dat", FinalFolder+"/fixed_rings.dat")
else:
    with open( FinalFolder+"/fixed_rings.dat", 'w') as f:
        f.write('{:}'.format(0))
#shutil.copyfile(InitialFolder+"/PARM_BN.lammps", FinalFolder+"/PARM_BN.lammps")
shutil.copyfile(InitialFolder+"/PARM_C.lammps", FinalFolder+"/PARM_C.lammps")
shutil.copyfile(InitialFolder+"/PARM_Si2O3.lammps", FinalFolder+"/PARM_Si2O3.lammps")
shutil.copyfile(InitialFolder+"/PARM_Si.lammps", FinalFolder+"/PARM_Si.lammps")
#shutil.copyfile(InitialFolder+"/COULOMB.table", FinalFolder+"/COULOMB.table")
with open(InitialFolder+"/Si.in", 'r') as f:
    with open(FinalFolder+"/Si.in", 'w') as g:

        for i in range(13):
            g.write(f.readline())

        f.readline()
        g.write("read_restart               "+InitialFolder+"/Si_restart.restart\n")

        for i in range(45):
            g.write(f.readline())



#with open(InitialFolder+"/BN.in", 'r') as f:
#    with open(FinalFolder+"/BN.in", 'w') as g:
#
#        for i in range(13):
#            g.write(f.readline())
#
#        f.readline()
#        g.write("read_restart               "+InitialFolder+"/BN_restart.restart\n")
#
#        for i in range(45):
#            g.write(f.readline())


with open(InitialFolder+"/Si2O3.in", 'r') as f:
    with open(FinalFolder+"/Si2O3.in", 'w') as g:

        for i in range(13):
            g.write(f.readline())

        f.readline()
        g.write("read_restart               "+InitialFolder+"/Si2O3_restart.restart\n")
       
        for i in range(45):
            g.write(f.readline())
        


