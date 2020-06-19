# -*- coding: utf-8 -*-

"""
General description
-------------------

A basic example to show how to model a simple energy system with oemof.solph.

The following energy system is modeled:

                input/output  bgas     bel
                     |          |        |       |
                     |          |        |       |
 wind(FixedSource)   |------------------>|       |
                     |          |        |       |
 pv(FixedSource)     |------------------>|       |
                     |          |        |       |
 rgas(Commodity)     |--------->|        |       |
                     |          |        |       |
 demand(Sink)        |<------------------|       |
                     |          |        |       |
                     |          |        |       |
 pp_gas(Transformer) |<---------|        |       |
                     |------------------>|       |
                     |          |        |       |
 storage(Storage)    |<------------------|       |
                     |------------------>|       |


Data
----
basic_example.csv


Installation requirements
-------------------------

This example requires the version v0.3.x of oemof. Install by:

    pip install 'oemof>=0.3,<0.4'

Optional:

    pip install matplotlib

"""

__copyright__ = "oemof developer group"
__license__ = "GPLv3"

# ****************************************************************************
# ********** PART 1 - Define and optimise the energy system ******************
# ****************************************************************************

###############################################################################
# imports
###############################################################################

# Default logger of oemof
from oemof.tools import logger
from oemof.tools import helpers

import oemof.solph as solph
import oemof.outputlib as outputlib

import logging
import os
import pandas as pd
import pprint as pp

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


solver = 'glpk'  # 'glpk', 'gurobi',....
debug = True  # Set number_of_timesteps to 3 to get a readable lp-file.
number_of_time_steps = 1
solver_verbose = True  # show/hide solver output

# initiate the logger (see the API docs for more information)
logger.define_logging(logfile='oemof_example.log',
                      screen_level=logging.INFO,
                      file_level=logging.DEBUG)

logging.info('Initialize the energy system')
date_time_index = pd.date_range('1/1/2016', periods=number_of_time_steps,
                                freq='H')

energysystem = solph.EnergySystem(timeindex=date_time_index)



##########################################################################
# Create oemof object
##########################################################################

logging.info('Create oemof objects')

# The bus objects were assigned to variables which makes it easier to connect
# components to these buses (see below).

## create (commodity (fuels + electricity in OSeMOSYS) busses Brandenburg & Berlin
# Brandenburg
GAS = solph.Bus(label="GAS")


## adding the buses to the energy system
#Brandenburg

ELECTRICITY = solph.Bus(label="ELECTRICITY")
energysystem.add(GAS, ELECTRICITY)

## create sources (fuel import technologies in OSeMOSYS) to represent the fuel input (annual limit)
#Brandenburg
energysystem.add(solph.Source(label='GAS_IMPORT', outputs={GAS: solph.Flow()}))


## create excess component for the electricity bus to allow overproduction
#Brandenburg
#energysystem.add(solph.Sink(label='excess_BBEL_FIN', inputs={BBEL_FIN: solph.Flow()}))


## create simple sink object representing the electrical demand
#Brandenburg
#energysystem.add(solph.Sink(label='demand_BBEL_FIN', inputs={BBEL_FIN: solph.Flow(fixed=True, nominal_value=2.1101)}))
energysystem.add(solph.Sink(label='DEMAND', inputs={ELECTRICITY: solph.Flow(
    actual_value=2.1101, fixed=True, nominal_value=1)}))

#actual_value=['stunden'*'%capafactor#listenweise multiplikation']

## create simple transformer object representing a power plants
#Brandenburg
energysystem.add(solph.Transformer(
    label="GAS_POWERPLANT",
    inputs={GAS: solph.Flow()},
    outputs={ELECTRICITY: solph.Flow(nominal_value=3.1101, variable_costs=9.1202)},
    conversion_factors={ELECTRICITY: 1, GAS: 1.1101}))


##########################################################################
# Optimise the energy system and plot the results
##########################################################################

logging.info('Optimise the energy system')

# initialise the operational model
model = solph.Model(energysystem)

# This is for debugging only. It is not(!) necessary to solve the problem and
# should be set to False to save time and disc space in normal use. For
# debugging the timesteps should be set to 3, to increase the readability of
# the lp-file.
if debug:
    filename = os.path.join(
        helpers.extend_basic_path('lp_files'), r'C:\Users\Winfried\Oemof\results\lp\ID.lp')
    logging.info('Store lp-file in {0}.'.format(filename))
    model.write(filename, io_options={'symbolic_solver_labels': True})

# if tee_switch is true solver messages will be displayed
logging.info('Solve the optimization problem')
model.solve(solver=solver, solve_kwargs={'tee': solver_verbose})

logging.info('Store the energy system with the results.')

# The processing module of the outputlib can be used to extract the results
# from the model transfer them into a homogeneous structured dictionary.

# add results to the energy system to make it possible to store them.
energysystem.results['main'] = outputlib.processing.results(model)
energysystem.results['meta'] = outputlib.processing.meta_results(model)



# The default path is the '.oemof' folder in your $HOME directory.
# The default filename is 'es_dump.oemof'.
# You can omit the attributes (as None is the default value) for testing cases.
# You should use unique names/folders for valuable results to avoid
# overwriting.

# store energy system with results
energysystem.dump(dpath=None, filename=None)

# ****************************************************************************
# ********** PART 2 - Processing the results *********************************
# ****************************************************************************

logging.info('**** The script can be divided into two parts here.')
logging.info('Restore the energy system and the results.')
energysystem = solph.EnergySystem()
energysystem.restore(dpath=None, filename=None)

# define an alias for shorter calls below (optional)
results = energysystem.results['main']


# get all variables of a specific component/bus
custom_storage = outputlib.views.node(results, 'storage')
electricity_bus = outputlib.views.node(results, 'electricity')
wind_component = outputlib.views.node(results, 'wind')
pv = outputlib.views.node(results, 'pv')
ppgas = outputlib.views.node(results, 'pp_gas')



# print the solver results
print('********* Meta results *********')
pp.pprint(energysystem.results['meta'])
print('')

dict_meta = energysystem.results['meta']

f = open(r"C:\Users\Winfried\Oemof\results\meta\meta_ID.txt","w")
f.write( str(dict_meta) )
f.close()


