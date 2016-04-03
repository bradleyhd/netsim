import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import math
from scipy.optimize import curve_fit

def linear(x, a, b):
  return a * x + b

def quadratic(x, a, b, c):
  return a * x**2 + b * x + c

def exponential(x, a, b, c):
  return a * x**b + c

#plt.figure(num=None, figsize=(16, 12), dpi=300, facecolor='w', edgecolor='k')

data = [[0.1,0.1,-7.434018514593847],[0.1,0.25,-2.7369569138303933],[0.1,0.5,-1.079596449962587],[0.1,0.75,4.596619461976396],[0.1,0.9,10.830481631205592],[0.25,0.1,0.21121155599113534],[0.25,0.25,7.481430746270853],[0.25,0.5,2.8832030633129158],[0.25,0.75,1.9925524276597761],[0.25,0.9,2.9447124715510937],[0.5,0.1,4.757563383369764],[0.5,0.25,-3.1984266947325426],[0.5,0.5,6.347890828747816],[0.5,0.75,6.6237753260623515],[0.5,0.9,2.858226562113666],[0.75,0.1,1.2363156675448093],[0.75,0.25,-3.2559043644701],[0.75,0.5,-2.800127094158841],[0.75,0.75,6.053966184836968],[0.75,0.9,-2.7392444750793308],[0.9,0.1,0.7360892695013829],[0.9,0.25,-2.905678488062344],[0.9,0.5,0.6593192258260506],[0.9,0.75,-0.7692772111599379],[0.9,0.9,-3.3453158431961576]]
data = np.array(data)

# popt, pcov = curve_fit(exponential, x, y)

fig = plt.figure()
ax = fig.gca(projection='3d')

plt.scatter(data[:, 0], data[:, 1], zs=data[:, 2], c=data[:, 2], cmap=plt.get_cmap('jet'))
# plt.plot(xl, exponential(xl, *popt), ln_fmt)

# graph(0, 'EDS5 - regular', 'ro', 'r--')
# graph(1, 'D5 - regular', 'bs', 'b--')
# graph(2, 'EDS5 - decision', 'go', 'g--')
# graph(3, 'D5 - decision', 'ms', 'm--')

plt.title('Effects of Weight Smoothing and Decay on Mean Speedup')
plt.xlabel('Smoothing')
plt.ylabel('Decay')
ax.set_zlabel('Mean Speedup')
plt.legend(loc=0, numpoints=1)

axes = plt.gca()
# axes.set_xscale('symlog')

# plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

# plt.savefig('nodes_vs_edges_added.png')
plt.show()