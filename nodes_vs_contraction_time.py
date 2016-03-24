import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.optimize import curve_fit

def linear(x, a, b):
  return a * x + b

def exponential(x, a, b, c):
  return a * x**2 + b * x + c

def exponential(x, a, b, c):
  return a * x**b + c

#plt.figure(num=None, figsize=(16, 12), dpi=300, facecolor='w', edgecolor='k')
plt.figure()

xs = [[1339, 4801, 11417, 35938, 111092, 244349], [1339, 4801, 11417, 35938, 111092, 244349]]
ys = [[0.29096614895388484, 1.425541217904538, 7.91564073599875, 201.3615051069064, 461.61539327399805, 1032.3463108900469], [0.10202891903463751, 0.4973782510496676, 1.4249127650400624, 6.247573849977925, 15.672931004082784, 45.308127364027314]]

y1 = np.array(ys[0])
x1 = np.array(xs[0])

xl1 = np.linspace(np.min(x1), np.max(x1), 50)

popt, pcov = curve_fit(exponential, x1, y1)

plt.plot(x1, y1, 'ro', label='EDS')
plt.plot(xl1, exponential(xl1, *popt), 'r--')

y2 = np.array(ys[1])
x2 = np.array(xs[1])

xl2 = np.linspace(np.min(x2), np.max(x2), 50)

popt, pcov = curve_fit(exponential, x2, y2)

plt.plot(x2, y2, 'bs', label='D')
plt.plot(xl2, exponential(xl2, *popt), 'b--')

plt.title('Effects of Node Ordering on Contraction Time')
plt.xlabel('$\\vert V\/\\vert$')
plt.ylabel('Contraction Time (s)')
plt.legend(loc=0, numpoints=1)

axes = plt.gca()
axes.set_xscale('symlog')

#plt.savefig('test.pdf')
plt.show()