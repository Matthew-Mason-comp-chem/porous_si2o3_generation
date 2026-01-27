# 2D SiO2 Bilayers
## Overview
This is a Markov Chain Monte Carlo code to generate amorphous 2D networks of physical systems.

## Setup
git clone https://github.com/Matthew-Mason-comp-chem/porous_si2o3_generation.git

set global paths within:
1. netmc_Pores.aux and netmc_Pores.sh
2. preprocess.sh
To match system

## Procedure 
Generating structures:
1. Run Create_Image.py within Pore_Evaporation and right click nodes to create desired Pore
2. Edit "folder_name" to adjust system size as desired
3. Run ./preprocess <Output from Create_Image.py>
4. Edit netmc_Pores.aux file (Natoms, Pore Size, seed, and temperature range, number of steps, runtype)
5. Run ./netmc_Pores.sh

Post Processing:
1. Run ./postprocess.sh

## Guide for parameters

Temperature:

Number of Bond switching steps:

Seeds:

## Guide for outputs 

