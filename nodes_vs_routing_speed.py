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

xs =  [[1339, 4801, 11417], [1339, 4801, 11417], [1339, 4801, 11417], [1339, 4801, 11417]]
ys =  [[0.00021601701155304909, 0.00052001397125422955, 0.0012323575210757554], [0.00030329899163916707, 0.00055971450638025999, 0.001290484971832484], [9.5622031949460506e-05, 0.00034522998612374067, 0.00085518450941890478], [0.00013565650442615151, 0.00033377099316567183, 0.00087871693540364504]]

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