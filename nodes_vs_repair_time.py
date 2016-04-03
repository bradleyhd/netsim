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

xs = [[1490, 4855, 15189, 43427, 138081, 346252, 681587, 1503567], [1490, 4855, 15189, 43427, 138081, 346252, 681587, 1503567], [1490, 4855, 15189, 43427, 138081, 346252, 681587, 1503567], [1490, 4855, 15189, 43427, 138081, 346252, 681587, 1503567]]
ys = [[0.2228060520001236, 1.8555066520002583, 10.67007054900023, 55.54242648700074, 111.41753270200024, 276.6879492450007, 799.021312891, 3211.573103781], [0.09970236099979957, 0.6367513140003211, 2.82379642000069, 10.443741371000215, 29.3362445570001, 80.48980009499974, 144.95471005099898, 280.376861550998], [0.1399367150006583, 1.2532831990001796, 7.910048228000051, 34.53181689200028, 265.2433016340001, 188.40716418899956, 366.3291645679983, 759.2621534159989], [0.054081736000625824, 0.37569782700029464, 1.7856588040003771, 7.623619067999243, 20.82412155200018, 49.701029986999856, 90.25244883800042, 202.52818293399832]]

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

plt.title('Effects of Node Ordering on Repair Time')
plt.xlabel('$\\vert V\/\\vert$')
plt.ylabel('Contraction Time (s)')
plt.legend(loc=0, numpoints=1)

axes = plt.gca()
# axes.set_xscale('log')
# axes.set_yscale('log')

plt.savefig('nodes_vs_repair_time.png')
# plt.show()