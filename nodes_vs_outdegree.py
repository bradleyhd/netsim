import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.optimize import curve_fit

def linear(x, a, b):
  return a * x + b

def cubic(x, a, b, c):
  return a * x**2 + b * x + c

def cubic(x, a, b, c, d):
  return a * x**3 + b * x**2 + c * x + d

def mean(x, idx):
  
  return [np.mean(ys[idx])] * len(x)

#plt.figure(num=None, figsize=(16, 12), dpi=300, facecolor='w', edgecolor='k')
plt.figure()

xs = [[1339, 4801, 11417, 35938, 111092, 244349], [1339, 4801, 11417, 35938, 111092, 244349]]
ys = [[1.5832710978342046, 1.6838158716933973, 1.8605588158009985, 2.0703155434359175, 1.8582706225470782, 1.7940773238278036], [1.5653472740851382, 1.6263278483649239, 1.7325917491460103, 1.8476264678056653, 1.7342112843409065, 1.6993030460529817]]

y1 = np.array(ys[0])
x1 = np.array(xs[0])

xl1 = np.linspace(np.min(x1), np.max(x1), 50)
plt.plot(x1, y1, 'ro', label='EDS')
plt.plot(xl1, mean(xl1, 0), 'r--')

y2 = np.array(ys[1])
x2 = np.array(xs[1])

xl2 = np.linspace(np.min(x2), np.max(x2), 50)
plt.plot(x2, y2, 'bs', label='D')
plt.plot(xl2, mean(xl2, 1), 'b--')

plt.title('Effects of Node Ordering on Mean Outdegree')
plt.xlabel('$\\vert V\/\\vert$')
plt.ylabel('Mean Outdegree in $G^\\uparrow$')
plt.legend(loc=0, numpoints=1)

axes = plt.gca()
axes.set_xscale('symlog')

#plt.savefig('test.pdf')
plt.show()