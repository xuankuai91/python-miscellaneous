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
df['FMRatio'] = df.apply(lambda x: SimulateRatio(x['Rij'], x['B01001e2'], x['B01001m2'], x['B01001e26'], x['B01001m26']), axis=1)
df.loc[df['FMRatio'] > 10, 'FMRatio'] = 1 # Set outliers to normal values

# College diploma percentage
df['Bachelor'] = df.apply(lambda x: SimulateValue(x['Rij'], x['B15003e22'], x['B15003m22']), axis=1)
df['Master'] = df.apply(lambda x: SimulateValue(x['Rij'], x['B15003e23'], x['B15003m23']), axis=1)
df['Professional'] = df.apply(lambda x: SimulateValue(x['Rij'], x['B15003e24'], x['B15003m24']), axis=1)
df['Doctor'] = df.apply(lambda x: SimulateValue(x['Rij'], x['B15003e25'], x['B15003m25']), axis=1)
df['Subtotal'] = df.apply(lambda x: SimulateValue(x['Rij'], x['B15003e1'], x['B15003m1']), axis=1)
df['CollegeRate'] = 100 * (df['Bachelor'] + df['Master'] + df['Professional'] + df['Doctor']) / df['Subtotal']
df.loc[df['CollegeRate'] > 100, 'CollegeRate'] = 100 # Set outliers to normal values

# Poverty rate
df['Poverty'] = df.apply(lambda x: SimulateValue(x['Rij'], x['C17002e2'], x['C17002m2']), axis=1) + df.apply(lambda x: SimulateValue(x['Rij'], x['C17002e3'], x['C17002m3']), axis=1)
df['Subtotal'] = df.apply(lambda x: SimulateValue(x['Rij'], x['C17002e1'], x['C17002m1']), axis=1)
df['PovertyRate'] = 100 * (df['Poverty'] / df['Subtotal'])
df.loc[df['PovertyRate'] > 100, 'PovertyRate'] = 100 # Set outliers to normal values

# Median household income
df['Income'] = df.apply(lambda x: SimulateValue(1, x['B19013e1'], x['B19013m1']), axis=1)

# Renter-occupied household percentage
df['Renter'] = df.apply(lambda x: SimulateValue(x['Rij'], x['B25003e3'], x['B25003m3']), axis=1)
df['Subtotal'] = df.apply(lambda x: SimulateValue(x['Rij'], x['B25003e1'], x['B25003m1']), axis=1)
df['RenterRate'] = 100 * (df['Renter'] / df['Subtotal'])
df.loc[df['RenterRate'] > 100, 'RenterRate'] = 100 # Set outliers to normal values

# Carless household percentage
df['Carless'] = df.apply(lambda x: SimulateValue(x['Rij'], x['B25044e3'], x['B25044m3']), axis=1) + df.apply(lambda x: SimulateValue(x['Rij'], x['B25044e10'], x['B25044m10']), axis=1)
df['Subtotal'] = df.apply(lambda x: SimulateValue(x['Rij'], x['B25044e1'], x['B25044m1']), axis=1)
df['CarlessRate'] = 100 * (df['Carless'] / df['Subtotal'])
df.loc[df['CarlessRate'] > 100, 'CarlessRate'] = 100 # Set outliers to normal values

# Select fields to keep
df = df[['EBRP_Block_Pg_BLOCKID10', 'BLKGRPID10', 'Rij', 'TransitRate', 'FMRatio', 'CollegeRate', 'PovertyRate', 'Income', 'RenterRate', 'CarlessRate', 'MedAge', 'PctWhite', 'LDR', 'Ride2Drive']]

# Export to a CSV file
try:
	df.to_csv("TransitRate.csv")
except:
	pass

# Draw scatter and regression line plots
fig = plt.figure(figsize=(8.5, 11))
seq = 0
dict = {'FMRatio': 'Female-male ratio',
		'CollegeRate': 'College diploma percentage',
		'PovertyRate': 'Poverty rate',
		'Income': 'Median household income',
		'RenterRate': 'Renter-occupied housing percentage',
		'CarlessRate': 'Carless household percentage',
		'MedAge': 'Median age',
		'PctWhite': 'White percentage',
		'LDR': 'Low density residential',
		'Ride2Drive': 'Bus-riding-driving time ratio'}

for item in ['FMRatio', 'CollegeRate', 'PovertyRate', 'Income', 'RenterRate', 'CarlessRate', 'MedAge', 'PctWhite', 'LDR', 'Ride2Drive']:
	seq += 1
	ax = fig.add_subplot(5, 2, seq)

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
	plt.title(dict.get(item) + ' (' + str("{0:.3f}".format(result.pvalues[1])) + ')') # Write subplot's title with p-value
	plt.ylim((0, 70)) # Set X-axis range
	plt.tight_layout() # Optimize layout
	AdjustSpines(ax, ['left', 'bottom'])

plt.savefig('Figure 10.jpg', dpi=300)
plt.show()
