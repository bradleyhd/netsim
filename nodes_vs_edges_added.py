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
fig = plt.figure(num=None, figsize=(12, 8), dpi=300, facecolor='k', edgecolor='k')

xs = [[1014, 4383, 11821, 37698, 108043, 286563, 672292], [1014, 4383, 11821, 37698, 108043, 286563, 672292], [1014, 4383, 11821, 37698, 108043, 286563, 672292], [1014, 4383, 11821, 37698, 108043, 286563, 672292]]
ys = [[1412, 8783, 33825, 91481, 244070, 587042, 1290365], [1063, 7393, 29495, 92105, 242137, 556413, 1189746], [788, 4723, 21549, 58069, 117940, 250189, 551651], [534, 4434, 20343, 53871, 124803, 264540, 544287]]

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
graph(2, 'EDS5 - decision graph', blue, '^', '--')
graph(3, 'N5 - decision graph', white, 'D', '--')

ax = fig.gca()
plt.title('Effects of Node Ordering on Shortcut Edges Added', color=white)
plt.xlabel('Effective $\\vert V\/\\vert$')
plt.ylabel('Shortcuts Added')
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

# plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

plt.savefig('nodes_vs_edges_added.png', transparent=True)
# plt.show()