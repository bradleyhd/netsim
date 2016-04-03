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

xs = [[1490, 4855, 15189, 43427, 138081, 346252, 681587, 1503567], [1490, 4855, 15189, 43427, 138081, 346252, 681587, 1503567], [1490, 4855, 15189, 43427, 138081, 346252, 681587, 1503567], [1490, 4855, 15189, 43427, 138081, 346252, 681587, 1503567]]
ys = [[2278, 10246, 37064, 97234, 294640, 653029, 1253273, 2668482], [1719, 8387, 31839, 92773, 266137, 568621, 1063823, 2267218], [1199, 5813, 20073, 54679, 120706, 257934, 498372, 953608], [842, 4608, 17778, 47163, 118590, 236544, 422126, 779191]]

def graph(i, label, pt_fmt, ln_fmt):

  y = np.array(ys[i])
  x = np.array(xs[i])

  xl = np.linspace(np.min(x), np.max(x), 500)

  popt, pcov = curve_fit(exponential, x, y)

  plt.plot(x, y, pt_fmt, label=label)
  plt.plot(xl, exponential(xl, *popt), ln_fmt)

graph(0, 'EDS5 - regular', 'ro', 'r--')
graph(1, 'D5 - regular', 'bs', 'b--')
graph(2, 'EDS5 - decision', 'go', 'g--')
graph(3, 'D5 - decision', 'ms', 'm--')

plt.title('Effects of Node Ordering on Shortcuts Added')
plt.xlabel('$\\vert V\/\\vert$')
plt.ylabel('Shortcuts')
plt.legend(loc=0, numpoints=1)

axes = plt.gca()
# axes.set_xscale('symlog')

# plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

plt.savefig('nodes_vs_edges_added.png')
# plt.show()