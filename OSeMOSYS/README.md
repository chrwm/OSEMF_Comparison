This folder contains the model files of the reference energy system (RES) "S1" and "TX" in OSeMOSYS.

The **RES "S1"** represents a simplified fictional energy system and is just including one fuel import technology, one energy conversion technology and one demand. It is applied to one timestep. \
It can be used to understand mathematical operating principles of OSeMOSYS in practice. \
Due to the RES's simplicity its linear programme is very reduced and easy to read and can be used to test new equations or modifications.

The **RES "TX"** represents the metropolitan region Berlin-Brandenburg. \
"TX" is a simple two-node model, which exists in three different temporal resolutions and in dispatch as well as investment mode. \
In total six model variations exist, which are specified below:

The "T" in the RES name is short for timesteps, and the "X" indicates: 
* the number of timesteps (1,16,8784); and
* the type of optimisation ("I" - investment mode and "absence of I" - dispatch mode). 

The following model names result:
* T1, T16, T8784 (1,16,8784 timesteps in dispatch mode); and
* TI1, TI16, TI8784 (1,16,8784 timesteps in investment mode), which assume no existing electricity production capacities in both regions.

\
For more details, please see: "An Open Source Energy Modelling Framework Comparison of OSeMOSYS and oemof", available at https://kth.diva-portal.org.
Master's thesis ID: TRITA-ITM-EX 2020:212
