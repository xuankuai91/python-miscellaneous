import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm, lognorm

# Customize axises
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

fig = plt.figure(figsize=(11, 8.5), dpi=300)

# Draw uniform distribution
x1 = np.linspace(-1, 2)
y1 = 0.5 + x1 * 0

ax = fig.add_subplot(2, 2, 1)
ax.plot(x1, y1, clip_on = False)
AdjustSpines(ax, ['bottom'])

plt.title('Uniform distribution')
plt.xticks([-1, 2], ['a', 'b']) # Replace ticks on X axis
plt.yticks([]) # Remove ticks on Y axis
plt.xlim((-2, 3)) # Set X-axis range
plt.ylim((0, 1)) # Set Y-axis range
plt.vlines(-1, 0, 0.5, colors='C1', linestyles='dashed') # Draw vertical dash lines
plt.vlines(2, 0, 0.5, colors='C1', linestyles='dashed')

# Draw normal distribution
x2 = np.linspace(-1, 3)
y2 = norm(1, 1).pdf(x2)

ax = fig.add_subplot(2, 2, 2)
ax.plot(x2, y2, clip_on = False)
AdjustSpines(ax, ['bottom'])

plt.title('Normal distribution')
plt.xticks([-1, 3], ['a', 'b']) # Replace ticks on X axis
plt.yticks([]) # Remove ticks on Y axis
plt.xlim((-2, 4)) # Set X-axis range
plt.ylim((0, 1)) # Set Y-axis range
plt.vlines(-1, 0, norm(1, 1).pdf(-1), colors='C1', linestyles='dashed') # Draw vertical dash lines
plt.vlines(3, 0, norm(1, 1).pdf(3), colors='C1', linestyles='dashed')

# Draw lognormal distribution
x3 = np.linspace(0.01, 3)
y3 = lognorm(1, 0).pdf(x3)

ax = fig.add_subplot(2, 2, 3)
ax.plot(x3, y3, clip_on = False)
AdjustSpines(ax, ['bottom'])

plt.title('Lognormal distribution')
plt.xticks([0.01, 3], ['a', 'b']) # Replace ticks on X axis
plt.yticks([]) # Remove ticks on Y axis
plt.xlim((-1, 4)) # Set X-axis range
plt.ylim((0, 1)) # Set Y-axis range
plt.vlines(3, 0, lognorm(1, 0).pdf(3), colors='C1', linestyles='dashed') # Draw vertical dash lines

# Draw discrete distribution
x4 = np.linspace(-1, 2)

ax = fig.add_subplot(2, 2, 4)

plt.plot(x4[x4 < 0], 0.3 + x4[x4 < 0] * 0, color='C0')
plt.plot(x4[(x4 >= 0) & (x4 <= 1)], 0.5 + x4[(x4 >= 0) & (x4 <= 1)] * 0, color='C0')
plt.plot(x4[x4 > 1],0.2 + x4[x4 > 1] * 0, color='C0')
AdjustSpines(ax, ['bottom'])


plt.title('Discrete distribution')
plt.xticks([-1, 0, 1, 2], ['a', 'b', 'c', 'd']) # Replace ticks on X axis
plt.yticks([]) # Remove ticks on Y axis
plt.xlim((-2, 3)) # Set X-axis range
plt.ylim((0, 1)) # Set Y-axis range
plt.vlines(-1, 0, 0.3, colors='C1', linestyles='dashed') # Draw vertical dash lines
plt.vlines(0, 0, 0.5, colors='C1', linestyles='dashed')
plt.vlines(1, 0, 0.5, colors='C1', linestyles='dashed')
plt.vlines(2, 0, 0.2, colors='C1', linestyles='dashed')

plt.tight_layout() # Optimize layout

plt.savefig('Figure 5.jpg', dpi=300)
plt.show()
