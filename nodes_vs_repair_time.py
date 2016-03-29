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

xs = [[1339, 4801, 11417], [1339, 4801, 11417], [1339, 4801, 11417], [1339, 4801, 11417]]
ys = [[0.2130420790053904, 0.8482432729797438, 2.589548366027884], [0.11530607601162046, 0.5111584099940956, 1.473455838044174], [0.032665980979800224, 0.25017273996490985, 1.212844974012114], [0.01961639104411006, 0.11673664301633835, 0.6340060209622607]]
def graph(i, label, pt_fmt, ln_fmt):

  y = np.array(ys[i])
  x = np.array(xs[i])

  xl = np.linspace(np.min(x), np.max(x), 100)

  popt, pcov = curve_fit(exponential, x, y)

  plt.plot(x, y, pt_fmt, label=label)
  plt.plot(xl, exponential(xl, *popt), ln_fmt)

graph(0, 'EDS5 - regular', 'ro', 'r--')
graph(1, 'D5 - regular', 'bs', 'b--')
graph(2, 'EDS5 - decision', 'go', 'g--')
graph(3, 'D5 - decision', 'ms', 'm--')

plt.title('Effects of Node Ordering on Repair Time')
plt.xlabel('$\\vert V\/\\vert$')
plt.ylabel('Contraction Time (s)')
plt.legend(loc=0, numpoints=1)

axes = plt.gca()
# axes.set_xscale('symlog')

#plt.savefig('test.pdf')
plt.show()