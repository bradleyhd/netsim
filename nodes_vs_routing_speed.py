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
ys = [[0.00015850999625399709, 0.00034465501084923744, 0.0011010959860868752, 0.0063666889909654856, 0.013431586034130305, 0.022599655494559556], [0.00017578795086592436, 0.00035217299591749907, 0.00093084300169721246, 0.0036733669694513083, 0.0084095964557491243, 0.013656680472195148]]

y1 = np.array(ys[0])
x1 = np.array(xs[0])

xl1 = np.linspace(np.min(x1), np.max(x1), 50)

popt, pcov = curve_fit(exponential, x1, y1)

plt.plot(x1, y1, 'ro', label='EDS5')
plt.plot(xl1, exponential(xl1, *popt), 'r--')

y2 = np.array(ys[1])
x2 = np.array(xs[1])

xl2 = np.linspace(np.min(x2), np.max(x2), 50)

popt, pcov = curve_fit(exponential, x2, y2)

plt.plot(x2, y2, 'bs', label='D5')
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