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

xs = [[1490, 4855, 15189, 43427, 138081, 346252, 681587], [1490, 4855, 15189, 43427, 138081, 346252, 681587], [1490, 4855, 15189, 43427, 138081, 346252, 681587], [1490, 4855, 15189, 43427, 138081, 346252, 681587]]
ys = [[0.22363941200001136, 1.6900403849999748, 10.281634379000025, 61.33003691399972, 112.68288505100008, 294.9633159410005, 862.8230567240007], [0.0937738040001932, 0.5849413189998813, 3.0360557869998956, 9.789275561000068, 26.22032573300021, 62.29369108499941, 135.91543047600044], [0.1324584999997569, 1.1136390820001907, 7.1074649759998465, 37.590614340999764, 334.2644013280001, 214.7357505509999, 394.48707237100007], [0.047173440999813465, 0.31775572399965313, 1.812454968000111, 6.830415844999607, 19.805900676999954, 56.8238684909993, 89.08203452399903]]

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

plt.title('Effects of Node Ordering on Contraction Time')
plt.xlabel('$\\vert V\/\\vert$')
plt.ylabel('Contraction Time (s)')
plt.legend(loc=0, numpoints=1)

axes = plt.gca()
# axes.set_xscale('symlog')

#plt.savefig('test.pdf')
plt.show()