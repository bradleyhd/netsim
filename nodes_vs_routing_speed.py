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

xs =  [[1490, 4855, 15189, 43427, 138081, 346252, 681587], [1490, 4855, 15189, 43427, 138081, 346252, 681587], [1490, 4855, 15189, 43427, 138081, 346252, 681587], [1490, 4855, 15189, 43427, 138081, 346252, 681587],]
ys =  [[0.00026715049989434192, 0.0014035574999979872, 0.0061703260000740556, 0.010549757500257329, 0.02555760200016266, 0.040123603999745683, 0.063447176499721536], [0.00028976849989703624, 0.0013198225001360697, 0.005111699499821043, 0.012535749500102611, 0.028472909000129221, 0.047916752000219276, 0.071634814000390179], [0.00026610049985720252, 0.0011969804997988831, 0.0045219670000733458, 0.014301050000085525, 0.020341850000022532, 0.034052538999276294, 0.060132389000500552], [0.00027198950010642875, 0.001089114000023983, 0.0049764625000534579, 0.011896184500301388, 0.028867914499869585, 0.062511313500181132, 0.07914886300022772]]

y1 = np.array(ys[0])
x1 = np.array(xs[0])

xl1 = np.linspace(np.min(x1), np.max(x1), 50)

popt, pcov = curve_fit(exponential, x1, y1)

plt.plot(x1, y1, 'ro', label='EDS5 - regular')
plt.plot(xl1, exponential(xl1, *popt), 'r--')

# --

y2 = np.array(ys[1])
x2 = np.array(xs[1])

xl2 = np.linspace(np.min(x2), np.max(x2), 50)

popt, pcov = curve_fit(exponential, x2, y2)

plt.plot(x2, y2, 'bs', label='D5 - regular')
plt.plot(xl2, exponential(xl2, *popt), 'b--')

# --

y3 = np.array(ys[2])
x3 = np.array(xs[2])

xl3 = np.linspace(np.min(x3), np.max(x3), 50)

popt, pcov = curve_fit(exponential, x3, y3)

plt.plot(x3, y3, 'go', label='EDS5 - decision')
plt.plot(xl3, exponential(xl3, *popt), 'g--')

# --

y4 = np.array(ys[3])
x4 = np.array(xs[3])

xl4 = np.linspace(np.min(x4), np.max(x4), 50)

popt, pcov = curve_fit(exponential, x4, y4)

plt.plot(x4, y4, 'ms', label='D5 - decision')
plt.plot(xl3, exponential(xl3, *popt), 'm--')

plt.title('Effects of Node Ordering on 1000 Random Route Queries')
plt.xlabel('$\\vert V\/\\vert$')
plt.ylabel('Mean Route Time (s)')
plt.legend(loc=0, numpoints=1)

axes = plt.gca()
# axes.set_xscale('symlog')

plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

#plt.savefig('test.pdf')
plt.show()