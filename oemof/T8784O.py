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
number_of_time_steps = 8784
solver_verbose = True  # show/hide solver output

# initiate the logger (see the API docs for more information)
logger.define_logging(logfile='oemof_example.log',
                      screen_level=logging.INFO,
                      file_level=logging.DEBUG)

logging.info('Initialize the energy system')
date_time_index = pd.date_range('1/1/2016', periods=number_of_time_steps,
                                freq='H')

energysystem = solph.EnergySystem(timeindex=date_time_index)

# Read data file
filename = os.path.join(os.path.dirname(__file__), 'T8784.csv')
data = pd.read_csv(filename)

##########################################################################
# Create oemof object
##########################################################################

logging.info('Create oemof objects')

# The bus objects were assigned to variables which makes it easier to connect
# components to these buses (see below).

## create (commodity (fuels + electricity in OSeMOSYS) busses Brandenburg & Berlin
# Brandenburg
BBNaturalGas = solph.Bus(label="BBNaturalGas")
BBHardCoal = solph.Bus(label="BBHardCoal")
BBLignite = solph.Bus(label="BBLignite")
BBOil = solph.Bus(label="BBOil")
BBBiomass = solph.Bus(label="BBBiomass")
BBEL_SEC = solph.Bus(label="BBEL_SEC")
BBEL_FIN = solph.Bus(label="BBEL_FIN")
# Berlin
BENaturalGas = solph.Bus(label="BENaturalGas")
BEHardCoal = solph.Bus(label="BEHardCoal")
BELignite = solph.Bus(label="BELignite")
BEOil = solph.Bus(label="BEOil")
BEBiomass = solph.Bus(label="BEBiomass")
BEEL_SEC = solph.Bus(label="BEEL_SEC")
BEEL_FIN = solph.Bus(label="BEEL_FIN")

## adding the buses to the energy system
#Brandenburg
energysystem.add(BBNaturalGas, BBHardCoal, BBLignite, BBOil, BBBiomass, BBEL_SEC, BBEL_FIN)
#Berlin
energysystem.add(BENaturalGas, BEHardCoal, BELignite, BEOil, BEBiomass, BEEL_SEC, BEEL_FIN)

## create sources (fuel import technologies in OSeMOSYS) to represent the fuel input (annual limit)
#Brandenburg
energysystem.add(solph.Source(label='rBBGAS_IMPORT', outputs={BBNaturalGas: solph.Flow()}))
energysystem.add(solph.Source(label='rBBHCO_IMPORT', outputs={BBHardCoal: solph.Flow()}))
energysystem.add(solph.Source(label='rBBLIG_IMPORT', outputs={BBLignite: solph.Flow()}))
energysystem.add(solph.Source(label='rBBOIL_IMPORT', outputs={BBOil: solph.Flow()}))
energysystem.add(solph.Source(label='rBBBIO_IMPORT', outputs={BBBiomass: solph.Flow()}))
#Berlin
energysystem.add(solph.Source(label='rBEGAS_IMPORT', outputs={BENaturalGas: solph.Flow()}))
energysystem.add(solph.Source(label='rBEHCO_IMPORT', outputs={BEHardCoal: solph.Flow()}))
energysystem.add(solph.Source(label='rBELIG_IMPORT', outputs={BELignite: solph.Flow()}))
energysystem.add(solph.Source(label='rBEOIL_IMPORT', outputs={BEOil: solph.Flow()}))
energysystem.add(solph.Source(label='rBEBIO_IMPORT', outputs={BEBiomass: solph.Flow()}))

## create fixed sources to represent the renewable volatiles wind, pv, run-of-river
#Brandenburg
energysystem.add(solph.Source(label='BBWIND_P', outputs={BBEL_SEC: solph.Flow(
    actual_value=data['BBWIND_P'], nominal_value=6358.14, fixed=True)}))
energysystem.add(solph.Source(label='BBSOLPV_P', outputs={BBEL_SEC: solph.Flow(
    actual_value=data['BBSOLPV_P'], nominal_value=3205.76, fixed=True)}))
energysystem.add(solph.Source(label='BBRORHYD_P', outputs={BBEL_SEC: solph.Flow(
    actual_value=data['BBRORHYD_P'], nominal_value=4.86, fixed=True)}))
#Berlin
energysystem.add(solph.Source(label='BEWIND_P', outputs={BEEL_SEC: solph.Flow(
    actual_value=data['BEWIND_P'], nominal_value=12.38, fixed=True)}))
energysystem.add(solph.Source(label='BESOLPV_P', outputs={BEEL_SEC: solph.Flow(
    actual_value=data['BESOLPV_P'], nominal_value=86.95, fixed=True)}))

## create excess component for the electricity bus to allow overproduction
#Brandenburg
energysystem.add(solph.Sink(label='excess_BBEL_FIN', inputs={BBEL_FIN: solph.Flow()}))
#Berlin
energysystem.add(solph.Sink(label='excess_BEEL_FIN', inputs={BEEL_FIN: solph.Flow()}))

## create simple sink object representing the electrical demand
#Brandenburg
energysystem.add(solph.Sink(label='demand_BBEL_FIN', inputs={BBEL_FIN: solph.Flow(
    actual_value=data['demand_BBEL_FIN'], fixed=True, nominal_value=1)}))
#Berlin
energysystem.add(solph.Sink(label='demand_BEEL_FIN', inputs={BEEL_FIN: solph.Flow(
    actual_value=data['demand_BEEL_FIN'], fixed=True, nominal_value=1)}))


## create simple transformer object representing a power plants
#Brandenburg
energysystem.add(solph.Transformer(
    label="BBNGA_P",
    inputs={BBNaturalGas: solph.Flow()},
    outputs={BBEL_SEC: solph.Flow(nominal_value=733.3, variable_costs=19.89)},
    conversion_factors={BBEL_SEC: 0.581395349}))

energysystem.add(solph.Transformer(
    label="BBHCO_P",
    inputs={BBHardCoal: solph.Flow()},
    outputs={BBEL_SEC: solph.Flow(nominal_value=0, variable_costs=11.24)},
    conversion_factors={BBEL_SEC: 0.460829493}))

energysystem.add(solph.Transformer(
    label="BBLIG_P",
    inputs={BBLignite: solph.Flow()},
    outputs={BBEL_SEC: solph.Flow(nominal_value=4409, variable_costs=4.72)},
    conversion_factors={BBEL_SEC: 0.429184549}))

energysystem.add(solph.Transformer(
    label="BBOIL_P",
    inputs={BBOil: solph.Flow()},
    outputs={BBEL_SEC: solph.Flow(nominal_value=333.5, variable_costs=25.17)},
    conversion_factors={BBEL_SEC: 0.383141762}))

energysystem.add(solph.Transformer(
    label="BBBIO_P",
    inputs={BBBiomass: solph.Flow()},
    outputs={BBEL_SEC: solph.Flow(nominal_value=439.8, variable_costs=30.18)},
    conversion_factors={BBEL_SEC: 0.4}))
#Berlin
energysystem.add(solph.Transformer(
    label="BENGA_P",
    inputs={BENaturalGas: solph.Flow()},
    outputs={BEEL_SEC: solph.Flow(nominal_value=1040, variable_costs=19.89)},
    conversion_factors={BEEL_SEC: 0.581395349}))

energysystem.add(solph.Transformer(
    label="BEHCO_P",
    inputs={BEHardCoal: solph.Flow()},
    outputs={BEEL_SEC: solph.Flow(nominal_value=777, variable_costs=11.24)},
    conversion_factors={BEEL_SEC: 0.460829493}))

energysystem.add(solph.Transformer(
    label="BELIG_P",
    inputs={BELignite: solph.Flow()},
    outputs={BEEL_SEC: solph.Flow(nominal_value=0, variable_costs=4.72)},
    conversion_factors={BEEL_SEC: 0.429184549}))

energysystem.add(solph.Transformer(
    label="BEOIL_P",
    inputs={BEOil: solph.Flow()},
    outputs={BEEL_SEC: solph.Flow(nominal_value=327, variable_costs=25.17)},
    conversion_factors={BEEL_SEC: 0.383141762}))

energysystem.add(solph.Transformer(
    label="BEBIO_P",
    inputs={BEBiomass: solph.Flow()},
    outputs={BEEL_SEC: solph.Flow(nominal_value=45.19, variable_costs=30.18)},
    conversion_factors={BEEL_SEC: 0.4}))

## create transmission & trade lines
#Brandenburg
energysystem.add(solph.Transformer(
    label="BBTRANS",
    inputs={BBEL_SEC: solph.Flow()},
    outputs={BBEL_FIN: solph.Flow(variable_costs=0)},
    conversion_factors={BBEL_FIN: 0.9}))
# trade !TO! Brandenburg
energysystem.add(solph.Transformer(
    label="BBINT",
    inputs={BEEL_SEC: solph.Flow()},
    outputs={BBEL_SEC: solph.Flow(nominal_value=3000, variable_costs=2)},
    conversion_factors={BBEL_SEC: 1}))
#Berlin
energysystem.add(solph.Transformer(
    label="BETRANS",
    inputs={BEEL_SEC: solph.Flow()},
    outputs={BEEL_FIN: solph.Flow(variable_costs=0)},
    conversion_factors={BEEL_FIN: 0.9}))
# trade !TO! Berlin
energysystem.add(solph.Transformer(
    label="BEINT",
    inputs={BBEL_SEC: solph.Flow()},
    outputs={BEEL_SEC: solph.Flow(nominal_value=3000, variable_costs=1)},
    conversion_factors={BEEL_SEC: 1}))

## create Backstop (source) to cover demand
#Brandenburg
energysystem.add(solph.Transformer(
    label="BBBACKSTOP_FIN",
    outputs={BBEL_FIN: solph.Flow(nominal_value=999999999, variable_costs=1000000000)},
    conversion_factors={BBEL_FIN: 1}))
#Berlin
energysystem.add(solph.Transformer(
    label="BEBACKSTOP_FIN",
    outputs={BEEL_FIN: solph.Flow(nominal_value=999999999, variable_costs=1000000000)},
    conversion_factors={BEEL_FIN: 1}))


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
        helpers.extend_basic_path('lp_files'), r'C:\Users\Winfried\Oemof\results\lp\T8784O.lp')
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

# plot the time series (sequences) of a specific component/bus
# if plt is not None:
#       fig, ax = plt.subplots(figsize=(10, 5))
#     electricity_bus['sequences'].plot(ax=ax, kind='line',
#                                       drawstyle='steps-post')
#     plt.legend(loc='upper center', prop={'size': 8}, bbox_to_anchor=(0.5, 1.3),
#                ncol=2)
#     fig.subplots_adjust(top=0.8)
#     #plt.show()


# print the solver results
print('********* Meta results *********')
pp.pprint(energysystem.results['meta'])
print('')

dict_meta = energysystem.results['meta']

f = open(r"C:\Users\Winfried\Oemof\results\meta\meta_T8784O.txt","w")
f.write( str(dict_meta) )
f.close()

# ####################################################################################################
# string_results = outputlib.processing.convert_keys_to_strings(results)
# print(string_results.keys())

# make the dict "electricity_bus" to dataframe "df_electricity_bus" and print to csv
node_BBEL_SEC = outputlib.views.node(results, 'BBEL_SEC')
df_node_BBEL_SEC = node_BBEL_SEC['sequences']

node_BBEL_FIN = outputlib.views.node(results, 'BBEL_FIN')
df_node_BBEL_FIN = node_BBEL_FIN['sequences']

node_BEEL_SEC = outputlib.views.node(results, 'BEEL_SEC')
df_node_BEEL_SEC = node_BEEL_SEC['sequences']

node_BEEL_FIN = outputlib.views.node(results, 'BEEL_FIN')
df_node_BEEL_FIN = node_BEEL_FIN['sequences']

pd.concat([
    pd.concat([df_node_BBEL_SEC, df_node_BBEL_FIN,df_node_BEEL_SEC, df_node_BEEL_FIN], axis=1)]).to_csv(r'C:\Users\Winfried\Oemof\results\T8784O_EL.csv')



