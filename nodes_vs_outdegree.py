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
ys = [[1.6183719193427932, 1.7202666111226828, 1.903740036787247, 2.0479993321832044, 1.8654088503222555, 1.8067845581524786], [1.530993278566094, 1.6123724224119975, 1.7252342997284751, 1.831487561912182, 1.7162531955496345, 1.6819712787856713]]

y1 = np.array(ys[0])
x1 = np.array(xs[0])

xl1 = np.linspace(np.min(x1), np.max(x1), 50)
plt.plot(x1, y1, 'ro', label='EDS5')
plt.plot(xl1, mean(xl1, 0), 'r--')

y2 = np.array(ys[1])
x2 = np.array(xs[1])

xl2 = np.linspace(np.min(x2), np.max(x2), 50)
plt.plot(x2, y2, 'bs', label='D5')
plt.plot(xl2, mean(xl2, 1), 'b--')

plt.title('Effects of Node Ordering on Mean Outdegree')
plt.xlabel('$\\vert V\/\\vert$')
plt.ylabel('Mean Outdegree in $G^\\uparrow$')
plt.legend(loc=0, numpoints=1)

axes = plt.gca()
axes.set_xscale('symlog')

#plt.savefig('test.pdf')
plt.show()