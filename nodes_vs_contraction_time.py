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

xs = [[1490, 4855, 15189, 43427, 138081, 346252], [1490, 4855, 15189, 43427, 138081, 346252]]
ys = [[0.2201713149997886, 1.6422044639994056, 9.988838999999643, 62.075977898999554, 119.03660374799983, 310.1239784449999], [0.08390571099971567, 0.5979957429999558, 3.0203566660002252, 10.412488781999855, 28.608607763999316, 68.60547382500044]]

y1 = np.array(ys[0])
x1 = np.array(xs[0])

xl1 = np.linspace(np.min(x1), np.max(x1), 50)

popt, pcov = curve_fit(exponential, x1, y1)

plt.plot(x1, y1, 'ro', label='EDS5')
plt.plot(xl1, exponential(xl1, *popt), 'r--')
print(exponential(18000000, *popt))

y2 = np.array(ys[1])
x2 = np.array(xs[1])

xl2 = np.linspace(np.min(x2), np.max(x2), 50)

popt, pcov = curve_fit(exponential, x2, y2)

plt.plot(x2, y2, 'bs', label='D5')
plt.plot(xl2, exponential(xl2, *popt), 'b--')
print(exponential(18000000, *popt))

plt.title('Effects of Node Ordering on Contraction Time')
plt.xlabel('$\\vert V\/\\vert$')
plt.ylabel('Contraction Time (s)')
plt.legend(loc=0, numpoints=1)

axes = plt.gca()
axes.set_xscale('symlog')

#plt.savefig('test.pdf')
plt.show()