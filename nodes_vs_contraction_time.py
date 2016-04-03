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

def log(x, a, k):
  return a * x**k

#plt.figure(num=None, figsize=(16, 12), dpi=300, facecolor='w', edgecolor='k')
plt.figure()

xs = [[1490, 4855, 15189, 43427, 138081, 346252, 681587, 1503567], [1490, 4855, 15189, 43427, 138081, 346252, 681587, 1503567], [1490, 4855, 15189, 43427, 138081, 346252, 681587, 1503567], [1490, 4855, 15189, 43427, 138081, 346252, 681587, 1503567]]
ys = [[0.21465283399993496, 1.6757347289994868, 9.465244578000238, 55.912540658999205, 108.501274147, 264.07022346899976, 815.374882479, 3622.656188894998], [0.0935756240005503, 0.597732391000136, 2.6956140100000994, 9.271567843999946, 25.187769163999292, 57.046770695000305, 121.05458980200092, 270.3290146699983], [0.1299236529994232, 1.0900151350006126, 6.764704788999552, 35.534809243999916, 323.07042835799984, 198.00203013699957, 358.60456797500046, 758.3101881289986], [0.045551170999715396, 0.3239416460000939, 1.748071138999876, 6.369728438000493, 19.507091763000062, 51.32769932299925, 79.9600312599996, 183.01638332899893]]

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

plt.title('Effects of Node Ordering on Contraction Time')
plt.xlabel('$\\vert V\/\\vert$')
plt.ylabel('Contraction Time (s)')
plt.legend(loc=0, numpoints=1)

axes = plt.gca()
# axes.set_xscale('log')
# axes.set_yscale('log')

plt.savefig('nodes_vs_contraction_time.png')
# plt.show()