# PFC-TOUGH Interactive code
This repository provides the PFC-TOUGH interactive code.
The files have to be run in PFC3D 5.0.
The files provided in this repository is for simulating provided by ITASCA (https://docs.itascacg.com/pfc600/pfc/docproject/source/manual/optional_features/cfd_option/cfd_darcy.html?node2229) with modifications as follows:
1. Radius of particles is 0.00125 m instead of 0.0025 m. The number of particles in original problem was 16000. This modification results in 128000 particles in total.
2. Inflow rate is adjusted from 1e-5  cubic meters per second to 1e-3 cubic meters per second to accelerate the washout of particles.

# Why to use this code?
TOUGH2, as a commercialized software for fluid flow calculation in geomechanics, has undergone extensive validation over the years. TOUGH2 does not only support saturated-unsaturated flow, but also support multiphase flow and solute transport (using other EOS). TOUGH2 can be easily controlled as it takes text-based input file rather than requiring coding skill for research purpose. This ease of use makes TOUGH2 a strong choice for many geomechanics applications. The provided code can help researchers or practitioners who are interested in using PFC with TOUGH2 to simulate fluid-particle interactions, offering a clearer understanding of coupling mechanisms, which could lead to advancements in modeling more complex geomechanical processes.

# How to use this code
Three core files and a folder are provided as follows:
1. particles.p3dat: This file is for generating the initial setup of particles.
2. toughpfc_test1: The example of TOUGH2 input file.
3. darcy.py: This is the interactive code between TOUGH2 and PFC3D. This file has to be opened in PFC3D 5.00. After opening, user can simply run the file. CFD elements will be automatically created after running the code. With TOUGH2 EOS9, the simulation will be run automatically and the washout behavior will be recorded.
4. Other necessary files (in form of folder): This folder contains the files required for updating TOUGH2 input file.

To reproduce the simulation, user can follow in the following steps:
1. Put particles.p3dat, toughpfc_test1, darcy.py, and the files in "Other neccessary files" folder into the same folder
2. Download the EXT module (EXT.exe) of TOUGH2, which can be downloaded from (https://tough.lbl.gov/licensing-download/free-software-download/), and place it in the same folder. User needs TOUGH2 EOS9 to proceed further from this step. If user has TOUGH2 EOS9 available, copy it into the same folder.
3. Open PFC3D 5.00.
6. Within PFC3D 5.00, open darcy.py.
7. Run the code in darcy.py until the desired mechanical time. The code will generate the particles and CFD elements, couple PFC and TOUGH, and record the washout behavior.
