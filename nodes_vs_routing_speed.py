import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.optimize import curve_fit

def linear(x, a, b):
  return a * x + b

def quadratic(x, a, b, c):
  return a * x**2 + b * x + c

def exponential(x, a, b, c):
  return a * x**b + c

#plt.figure(num=None, figsize=(16, 12), dpi=300, facecolor='w', edgecolor='k')
plt.figure()

xs = [[1339, 4801, 11417, 35938, 111092, 244349], [1339, 4801, 11417, 35938, 111092, 244349]]
ys = [[1485, 6722, 19575, 74583, 186377, 377701], [1438, 6239, 17368, 62461, 166128, 342168]]

xs = [[1339, 4801, 11417, 35938, 111092, 244349], [1339, 4801, 11417, 35938, 111092, 244349]]
ys = [[0.0009774264763109386, 0.0016324890311807394, 0.0042289849952794611, 0.020992328936699778, 0.03979720053030178, 0.064169268996920437], [0.00089626299450173974, 0.0016038069734349847, 0.0034926565131172538, 0.01285797351738438, 0.019716657523531467, 0.032183445524424314]]

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

plt.title('Effects of Node Ordering on 1000 Random Route Queries')
plt.xlabel('$\\vert V\/\\vert$')
plt.ylabel('Mean Route Time (s)')
plt.legend(loc=0, numpoints=1)

axes = plt.gca()
axes.set_xscale('symlog')

plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

#plt.savefig('test.pdf')
plt.show()