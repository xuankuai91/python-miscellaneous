import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.formula.api as sm

from scipy.stats import truncnorm

# Simulate single value
def SimulateValue(Rij, Est, MoE):
	# Set initial values
	epsilon = truncnorm(-1.645, 1.645, loc=0, scale=1).rvs()
	estimate = -1

	# Check if negative values are simulated
	while estimate < 0:
		# Re-simulate
		epsilon = truncnorm(-1.645, 1.645, loc=0, scale=1).rvs()
		estimate = Rij * (Est + MoE * epsilon)

		# Stop simulating if values are positive
		if estimate >= 0:
			break

	return estimate

# Simulate ratio
def SimulateRatio(Rij, NumerEst, NumerMoE, DenomEst, DenomMoE):
	# Set initial values
	epsilon = truncnorm(-1.645, 1.645, loc=0, scale=1).rvs()
	numerator = -1
	denominator = -1

	# Check if negative values are simulated
	while numerator < 0 or denominator <= 0:
		# Re-simulate
		epsilon = truncnorm(-1.645, 1.645, loc=0, scale=1).rvs()
		numerator = NumerEst + NumerMoE * epsilon
		denominator = DenomEst + DenomMoE * epsilon

		# Stop simulating if values are positive
		if numerator >= 0 and denominator > 0:
			break

	estimate = numerator / denominator

	return estimate

# Modify axes of plot
def AdjustSpines(ax, spines):
    for loc, spine in ax.spines.items():
        if loc in spines:
            spine.set_smart_bounds(False)
        else:
            spine.set_color('none')  # Hide spine

    # Turn off ticks where there is no spine
    if 'left' in spines:
        ax.yaxis.set_ticks_position('left')
    else:
        # Hide Y-axis ticks
        ax.yaxis.set_ticks([])

    if 'bottom' in spines:
        ax.xaxis.set_ticks_position('bottom')
    else:
        # Hide X-axis ticks
        ax.xaxis.set_ticks([])

df = pd.read_csv('ACS_for_MCS.csv')

# Simulate the dependent value - transit rate
df['TransitRate'] = 100 * df.apply(lambda x: SimulateRatio(x['Rij'], x['B08301e10'], x['B08301m10'], x['B08301e1'], x['B08301m1']), axis=1)

# Simulate the independent values:
# Female-male ratio
df['FHHRate'] = 100 * df.apply(lambda x: SimulateRatio(x['Rij'], x['B11001e6'], x['B11001m6'], x['B11001e1'], x['B11001m1']), axis=1)
df.loc[df['FHHRate'] > 100, 'FHHRate'] = 100 # Set outliers to normal values

# Renter-occupied household percentage
df['RenterRate'] = 100 * df.apply(lambda x: SimulateRatio(x['Rij'], x['B25003e3'], x['B25003m3'], x['B25003e1'], x['B25003m1']), axis=1)
df.loc[df['RenterRate'] > 100, 'RenterRate'] = 100 # Set outliers to normal values

# Carless household percentage
df['Carless'] = df.apply(lambda x: SimulateValue(x['Rij'], x['B25044e3'], x['B25044m3']), axis=1) + df.apply(lambda x: SimulateValue(x['Rij'], x['B25044e10'], x['B25044m10']), axis=1)
df['Subtotal'] = df.apply(lambda x: SimulateValue(x['Rij'], x['B25044e1'], x['B25044m1']), axis=1)
df['CarlessRate'] = 100 * (df['Carless'] / df['Subtotal'])
df.loc[df['CarlessRate'] > 100, 'CarlessRate'] = 100 # Set outliers to normal values

# Poverty rate
df['Poverty'] = df.apply(lambda x: SimulateValue(x['Rij'], x['C17002e2'], x['C17002m2']), axis=1) + df.apply(lambda x: SimulateValue(x['Rij'], x['C17002e3'], x['C17002m3']), axis=1)
df['Subtotal'] = df.apply(lambda x: SimulateValue(x['Rij'], x['C17002e1'], x['C17002m1']), axis=1)
df['PovertyRate'] = 100 * (df['Poverty'] / df['Subtotal'])
df.loc[df['PovertyRate'] > 100, 'PovertyRate'] = 100 # Set outliers to normal values

# Median household income
df['Income'] = df.apply(lambda x: SimulateValue(1, x['B19013e1'], x['B19013m1']), axis=1)

# Select fields to keep
df = df[['BLOCKID10', 'BLKGRPID10', 'Rij', 'TransitRate', 'FHHRate', 'PctWhite', 'RenterRate', 'CarlessRate', 'PovertyRate', 'Income', 'LDR', 'Ride2Drive', 'NEAR_DIST', 'Emp_60min']]

# Export to a CSV file
try:
	df.to_csv("TransitRate.csv")
except:
	os.remove("TransitRate.csv") # Delete existing file
	df.to_csv("TransitRate.csv")

# Draw scatter and regression line plots
# Non-spatial variables
fig1 = plt.figure(figsize=(8.5, 6.6))
seq = 0
non_spatial_dict = {'FHHRate': 'Female household percentage',
					'PctWhite': 'White population percentage',
					'RenterRate': 'Renter-occupied housing percentage',
					'CarlessRate': 'Carless household percentage',
					'PovertyRate': 'Poverty rate',
					'Income': 'Median household income'}

for item in ['FHHRate', 'PctWhite', 'RenterRate', 'CarlessRate', 'PovertyRate', 'Income']:
	seq += 1
	ax = fig1.add_subplot(3, 2, seq)

	# Scatter
	ax.scatter(df[item], df['TransitRate'], s=2)

	# Regression line
	result = sm.ols(formula=("TransitRate ~ " + item), data=df).fit()
	k = result.params[1]
	b = result.params[0]

	x = np.linspace(0, df.loc[df[item].idxmax(), item])
	y = k * x + b
	ax.plot(x, y, color='C1')

	# Configure layout
	plt.title(non_spatial_dict.get(item) + ' (' + str("{0:.3f}".format(result.pvalues[1])) + ')') # Write subplot's title with p-value
	plt.ylim((0, 70)) # Set X-axis range
	plt.tight_layout() # Optimize layout
	AdjustSpines(ax, ['left', 'bottom'])

plt.savefig('Figure 10.jpg', dpi=300)

# Spatial variables
fig2 = plt.figure(figsize=(8.5, 4.4))
seq = 0
spatial_dict = {'LDR': 'Low density residential',
				'Ride2Drive': 'Transit-driving time ratio',
				'NEAR_DIST': 'Distance to nearest stop',
				'Emp_60min': 'Number of jobs in 30 minutes'}

for item in ['LDR', 'Ride2Drive', 'NEAR_DIST', 'Emp_60min']:
	seq += 1
	ax = fig2.add_subplot(2, 2, seq)

	# Scatter
	ax.scatter(df[item], df['TransitRate'], s=2)

	# Regression line
	result = sm.ols(formula=("TransitRate ~ " + item), data=df).fit()
	k = result.params[1]
	b = result.params[0]

	x = np.linspace(0, df.loc[df[item].idxmax(), item])
	y = k * x + b
	ax.plot(x, y, color='C1')

	# Configure layout
	plt.title(spatial_dict.get(item) + ' (' + str("{0:.3f}".format(result.pvalues[1])) + ')') # Write subplot's title with p-value
	plt.ylim((0, 70)) # Set X-axis range
	plt.tight_layout() # Optimize layout
	AdjustSpines(ax, ['left', 'bottom'])

plt.savefig('Figure 11.jpg', dpi=300)
