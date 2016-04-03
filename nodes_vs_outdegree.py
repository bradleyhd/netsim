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

def exponential(x, a, b, c):
  return a * x**b + c

def mean(x, idx):
  
  return [np.mean(ys[idx])] * len(x)

#plt.figure(num=None, figsize=(16, 12), dpi=300, facecolor='w', edgecolor='k')
plt.figure()

xs = [[1490, 4855, 15189, 43427, 138081, 346252, 681587, 1503567], [1490, 4855, 15189, 43427, 138081, 346252, 681587, 1503567], [1490, 4855, 15189, 43427, 138081, 346252, 681587, 1503567], [1490, 4855, 15189, 43427, 138081, 346252, 681587, 1503567]]
ys = [[1.5154362416107383, 1.8584963954685891, 2.1237079465402595, 2.0910263200313168, 2.0552646634946155, 1.9466486836177119, 1.9237734874638162, 1.9074673759134113], [1.2677852348993288, 1.6358393408856848, 1.9321877674632959, 1.9578372901651047, 1.8907597714385034, 1.7704995205803866, 1.7278322503216756, 1.7345718547959619], [2.1676767676767676, 2.9493589743589745, 3.6999519923187711, 3.9709801599052414, 3.5019151938713797, 2.7876351663716217, 2.7411168382915987, 2.676815899183778], [1.7737373737373738, 2.5403846153846152, 3.3802208353336534, 3.5861218043628469, 3.2405416302667831, 2.5060380890096634, 2.3658354000708597, 2.2967065894141814]]

def graph(i, label, pt_fmt, ln_fmt):

  y = np.array(ys[i])
  x = np.array(xs[i])

  xl = np.linspace(np.min(x), np.max(x), 500)

  plt.plot(x, y, pt_fmt, label=label)
  plt.plot(xl, mean(xl, i), ln_fmt)

graph(0, 'EDS5 - regular', 'ro', 'r--')
graph(1, 'D5 - regular', 'bs', 'b--')
graph(2, 'EDS5 - decision', 'go', 'g--')
graph(3, 'D5 - decision', 'ms', 'm--')

plt.title('Effects of Node Ordering on Mean Outdegree')
plt.xlabel('$\\vert V\/\\vert$')
plt.ylabel('Mean Outdegree in $G^\\uparrow$')
plt.legend(loc=0, numpoints=1)

axes = plt.gca()
axes.set_xscale('log')

plt.savefig('nodes_vs_outdegree.png')
# plt.show()