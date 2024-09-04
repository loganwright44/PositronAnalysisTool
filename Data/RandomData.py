"""
Generates a bunch of random data to test the boxplots
for the PepTo software
"""

import pandas as pd
import os
from random import uniform, sample, randint

anneal_types = [
    'annealed',
    'unannealed'
]

materials = [
    'lead',
    'nickel',
    'tungsten',
    'gold',
    'copper',
    'aluminum'
]

# Generate 100 random csv files of data for each material to test the program
path = os.getcwd()

for i in range(100):
    # Data will be of the form
    # Sample Name, S Parameter, S Uncertainty, Left W Parameter, Left W Uncertainty, Right W Parameter, Right W Uncertainty,
    # The wing data is totally arbitrary and can always be zero for our needs
    data = {
        'Sample Name': \
            f'{sample(materials, len(materials))[3]}_{sample(anneal_types, len(anneal_types))[0]}_{randint(1, 5_000)}_trial_0{randint(1, 9)}.csv',
        'S Parameter': uniform(0.48, 0.62),
        'S Uncertainty': uniform(0.0025, 0.0037),
        'Left W Parameter': uniform(0.18, 0.32),
        'Left W Uncertainty': uniform(0.0015, 0.0027),
        'Right W Parameter': uniform(0.18, 0.32),
        'Right W Uncertainty': uniform(0.0015, 0.0027),
    }

    data = pd.DataFrame(data, index = [0])
    data.to_csv(f"{path}/{data['Sample Name'][0].split('.')[0] + '_pappy.csv'}", index = False)
    print(f"{str(data['Sample Name'][0])} successfully saved!")