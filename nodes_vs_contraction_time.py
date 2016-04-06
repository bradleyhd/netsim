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
fig = plt.figure(num=None, figsize=(12, 8), dpi=300, facecolor='k', edgecolor='k')

xs = [[1014, 4383, 11821, 37698, 108043, 286563, 672292], [1014, 4383, 11821, 37698, 108043, 286563, 672292], [1014, 4383, 11821, 37698, 108043, 286563, 672292], [1014, 4383, 11821, 37698, 108043, 286563, 672292]]
ys = [[0.12496292499997708, 1.3427177930000198, 14.946727169000013, 77.84711978999997, 132.89606807799998, 347.22768731099995, 1159.6632128390002], [0.05571517599997833, 0.4678915659999916, 3.010586804000013, 10.956674838999902, 50.57508854799994, 115.12396636599988, 411.1783608910009], [0.10473765999998363, 0.7840828500000043, 11.989076787000045, 60.015191535999975, 496.0349359410002, 374.17332344199986, 573.4308050990003], [0.031237349999997832, 0.30562868499998785, 2.640261240999962, 10.047408474999997, 31.24031598900001, 85.61622297099984, 240.39986596800009]]

def graph(i, label, color, marker, l_marker):

  y = np.array(ys[i])
  x = np.array(xs[i])

  xl = np.linspace(np.min(x), np.max(x), 500)

  popt, pcov = curve_fit(exponential, x, y)

  plt.scatter(x, y, label=label, color=color, marker=marker)
  plt.plot(xl, exponential(xl, *popt), color=color, linestyle=l_marker)

blue = '#5738FF'
purple = '#E747E7'
orange = '#E7A725'
green = '#A1FF47'
red = '#FF1E43'
gray = '#333333'
white = 'w'

graph(0, 'EDS5 - original graph', red, 'o', '--')
graph(1, 'N5 - original graph', purple, 's', '--')
graph(2, 'EDS5 - decision graph', green, 'o', '--')
graph(3, 'N5 - decision graph', white, 's', '--')

ax = fig.gca()
plt.title('Effects of Node Ordering on Contraction Time', color=white)
plt.xlabel('Effective $\\vert V\/\\vert$')
plt.ylabel('Contraction Time (s)')
plt.axes().set_axis_bgcolor('black')
ax.xaxis.label.set_color(white)
ax.yaxis.label.set_color(white)
ax.tick_params(axis='x', colors=white)
ax.tick_params(axis='y', colors=white)
ax.spines['bottom'].set_color(white)
ax.spines['top'].set_color(white)
ax.spines['left'].set_color(white)
ax.spines['right'].set_color(white)
legend = plt.legend(loc=0, numpoints=1, framealpha=0.0)
legend.get_frame().set_facecolor('k')

max_x = np.max(np.array(xs))
max_y = np.max(np.array(ys))
min_x = np.min(np.array(xs))

min_y = 0 - (max_y * 0.01)
min_x = 0 - (max_x * 0.01)
max_x *= 1.01
max_y *= 1.01
plt.axes().set_xlim([min_x, max_x])
plt.axes().set_ylim([min_y, max_y])

for text in legend.get_texts():
    text.set_color(white)

axes = plt.gca()
# axes.set_xscale('log')
# axes.set_yscale('log')

plt.savefig('nodes_vs_contraction_time.png', transparent=True)
#plt.show()