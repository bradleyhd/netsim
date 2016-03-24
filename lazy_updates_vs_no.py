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

def mean(x, ys, idx):
  
  return [np.mean(ys[idx])] * len(x)

xs = [[1339, 4801, 11417, 35938],
      [1339, 4801, 11417, 35938]]

def outdegree():

  #plt.figure(num=None, figsize=(16, 12), dpi=300, facecolor='w', edgecolor='k')

  # plot 1: outdegree
  plt.figure()

  # series 1: no lazy updates
  # series 2: lazy updates

  ys = [[1.5832710978342046, 1.6838158716933973, 1.8605588158009985, 2.0703155434359175],
        [1.5832710978342046, 1.6779837533847115, 1.856967679775773, 2.0287995993099228]]

  y1 = np.array(ys[0])
  x1 = np.array(xs[0])

  xl1 = np.linspace(np.min(x1), np.max(x1), 50)
  plt.plot(x1, y1, 'ro', label='No Lazy Updates')
  plt.plot(xl1, mean(xl1, ys, 0), 'r--')

  y2 = np.array(ys[1])
  x2 = np.array(xs[1])

  xl2 = np.linspace(np.min(x2), np.max(x2), 50)
  plt.plot(x2, y2, 'bs', label='Lazy Updates')
  plt.plot(xl2, mean(xl2, ys, 1), 'b--')

  plt.title('Effects of Node Ordering on Mean Outdegree')
  plt.xlabel('$\\vert V\/\\vert$')
  plt.ylabel('Mean Outdegree in $G^\\uparrow$')
  plt.legend(loc=0, numpoints=1)

  axes = plt.gca()
  axes.set_xscale('symlog')

  #plt.savefig('test.pdf')
  plt.show()


outdegree()