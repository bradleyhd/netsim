import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.optimize import curve_fit

def linear(x, a, b):
  return a * x + b

def quadratic(x, a, b, c):
  return a * x**2 + b * x + c

#plt.figure(num=None, figsize=(16, 12), dpi=300, facecolor='w', edgecolor='k')
plt.figure()

ys1 = np.array([0.06816799001535401, 0.5652654659934342, 5.158066017029341, 77.12978387798648, 298.955215725])
xs1 = np.array([186, 1457, 7100, 29583, 59271])

x1 = np.linspace(0, np.max(xs1), 50)

popt, pcov = curve_fit(quadratic, xs1, ys1)

plt.plot(xs1, ys1, 'r^', label='ED + Search Space + 3 * Neighbors')
plt.plot(x1, quadratic(x1, *popt), 'r--')

ys2 = np.array([0.014183336985297501, 0.10894927801564336, 0.5379755159956403, 3.1718707800027914, 6.6690281690098345])
xs2 = np.array([110, 1024, 5358, 22965, 44331])

x2 = np.linspace(0, np.max(xs1), 50)

popt, pcov = curve_fit(quadratic, xs2, ys2)

plt.plot(xs2, ys2, 'bv', label='Neighbors')
plt.plot(x2, quadratic(x2, *popt), 'b--')

plt.title('Affects of Node Ordering on Contraction Time')
plt.xlabel('Shortcuts Added')
plt.ylabel('Contraction Time (s)')
plt.legend(loc=0, numpoints=1)

axes = plt.gca()
# axes.set_xlim([0, np.max(np.append(xs1, xs2)) * 1.1])
# axes.set_ylim([0, np.max(np.append(ys1, ys2)) * 1.1])

plt.show()

