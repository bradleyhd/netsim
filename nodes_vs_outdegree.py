import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.optimize import curve_fit

def linear(x, a, b):
  return a * x + b

def cubic(x, a, b, c):
  return a * x**2 + b * x + c

def cubic(x, a, b, c, d):
  return a * x**3 + b * x**2 + c * x + d

def mean(x, idx):
  
  return [np.mean(ys[idx])] * len(x)

#plt.figure(num=None, figsize=(16, 12), dpi=300, facecolor='w', edgecolor='k')
plt.figure()

xs = [[1490, 4855, 15189, 43427, 138081, 346252], [1490, 4855, 15189, 43427, 138081, 346252]]
ys = [[1.5154362416107383, 1.8584963954685891, 2.1237079465402595, 2.0910263200313168, 2.0552646634946155, 1.9466486836177119], [1.2677852348993288, 1.6358393408856848, 1.9321877674632959, 1.9578372901651047, 1.8907597714385034, 1.7704995205803866]]

y1 = np.array(ys[0])
x1 = np.array(xs[0])

xl1 = np.linspace(np.min(x1), np.max(x1), 50)
plt.plot(x1, y1, 'ro', label='EDS5')
plt.plot(xl1, mean(xl1, 0), 'r--')

y2 = np.array(ys[1])
x2 = np.array(xs[1])

xl2 = np.linspace(np.min(x2), np.max(x2), 50)
plt.plot(x2, y2, 'bs', label='D5')
plt.plot(xl2, mean(xl2, 1), 'b--')

plt.title('Effects of Node Ordering on Mean Outdegree')
plt.xlabel('$\\vert V\/\\vert$')
plt.ylabel('Mean Outdegree in $G^\\uparrow$')
plt.legend(loc=0, numpoints=1)

axes = plt.gca()
axes.set_xscale('symlog')

#plt.savefig('test.pdf')
plt.show()