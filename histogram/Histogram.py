import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import string

def despine(ax):
    for x in ax:
        x.spines['right'].set_visible(False)
        x.spines['top'].set_visible(False)

df = pd.read_csv('TransitRateRatio.csv')
cols = ['FHHRate', 'PctWhite', 'RenterRate', 'CarlessRate', 'PovertyRate', 'Income', 'Ride2Drive', 'NEAR_DIST', 'Emp_60min']
title_dict = {'FHHRate': 'Female household percentage',
              'PctWhite': 'White population percentage',
              'RenterRate': 'Renter-occupied housing percentage',
              'CarlessRate': 'Carless household percentage',
              'PovertyRate': 'Poverty rate',
              'Income': 'Median household income',
              'Ride2Drive': 'Transit-driving time ratio',
              'NEAR_DIST': 'Distance to nearest stop',
              'Emp_60min': 'Number of jobs in 30 minutes'}
n = 0

# Draw histogram
for col in cols:
    ax = df.hist(column=col, bins=100, sharex=True, sharey=True, grid=False, figsize=(3.5, 2.5))

    # Despine
    ax = ax[0]
    despine(ax)

    plt.title(title_dict.get(col), size=8)
    plt.xticks(size=8)
    plt.yticks(size=8)
    ax[0].xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    ax[0].yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))

    letter = string.ascii_lowercase[n]
    plt.savefig('Figure 17(' + letter + ').jpg', dpi=300)
    n += 1
