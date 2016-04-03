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
ys = [[0.00027718550018107635, 0.0014051910002308432, 0.0059716799996749614, 0.0091314454998610017, 0.024666515500030073, 0.038507096499870386, 0.058184093000818393, 0.12793981399954646], [0.00029577450004580896, 0.0013283954999678826, 0.0050448135002625349, 0.011782086999573949, 0.027539378500023304, 0.043186980499740457, 0.064648241999748279, 0.12179330999970261], [0.00026476150014786981, 0.0012458404999051709, 0.0046034065003368596, 0.01235319650004385, 0.019788737499766285, 0.028652757000145357, 0.056187490000411344, 0.080005879999589524], [0.00025842550030574785, 0.0010697440002331859, 0.004112398999495781, 0.010342937000132224, 0.028225709000253119, 0.052291365500423126, 0.06639447450015723, 0.12681145349961298]]


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

plt.title('Effects of Node Ordering on 1000 Random Route Queries')
plt.xlabel('$\\vert V\/\\vert$')
plt.ylabel('Mean Route Time (s)')
plt.legend(loc=0, numpoints=1)

axes = plt.gca()
axes.set_xscale('log')

# plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

plt.savefig('nodes_vs_routing_speed.png')
# plt.show()