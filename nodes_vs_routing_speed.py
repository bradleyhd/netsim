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

fig = plt.figure(num=None, figsize=(12, 8), dpi=300, facecolor='k', edgecolor='k')

xs = [[1014, 4383, 11821, 37698, 108043, 286563, 672292], [1014, 4383, 11821, 37698, 108043, 286563, 672292], [1014, 4383, 11821, 37698, 108043, 286563, 672292], [1014, 4383, 11821, 37698, 108043, 286563, 672292]]
ys = [[0.00013309850001519408, 0.00059208550001699223, 0.002604027000003839, 0.004665461000030291, 0.014662985999962075, 0.023410306499954459, 0.041176939000251878], [0.00014861549998101964, 0.00055641999999522795, 0.002577900000005684, 0.0054275369999459144, 0.021226498000032734, 0.029786237500047719, 0.059782716000881919], [0.00012334000000180367, 0.00043368899999052246, 0.0020054734999632728, 0.005848614000001362, 0.014609930999995413, 0.019599954500336025, 0.028973604500606598], [0.00012613299999486571, 0.00044437049999146438, 0.0021501399999692694, 0.0055929929999933847, 0.019908546500118973, 0.039582631500252319, 0.054390303499531001]]

ys = np.array(ys) * 1000

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
plt.title('Effects of Node Ordering on Routing Speed', color=white)
plt.xlabel('Effective $\\vert V\/\\vert$')
plt.ylabel('Routing Time (ms)')
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

plt.savefig('nodes_vs_routing_speed.png', transparent=True)
#plt.show()