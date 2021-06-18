import matplotlib.pyplot as plt
import numpy as np
from tempfile import TemporaryFile
import time
outfile = TemporaryFile()

# prepare some coordinates
x, y, z = np.indices((20, 20, 20))

# draw cuboids in the top left and bottom right corners, and a link between
# them
cube1 = (x < 7) & (y < 7) & (z < 7)
cube2 = (x >= 13) & (y >= 13) & (z >= 13)
link = abs(x - y) + abs(y - z) + abs(z - x) <= 2

# combine the objects into a single boolean array
voxels = cube1 | cube2 | link

# set the colors of each object
colors = np.empty((len(x),len(y),len(z),3), np.float16)

print(voxels)
colors[link] = (0,0.5,0)
colors[cube1] = (0.4,0.8,1)
colors[cube2] = (0.9,0.1,1)
print(colors)
# and plot everything
ax = plt.figure().add_subplot(projection='3d')
ax.voxels(voxels, facecolors=colors, edgecolor='k')


with open('test.npy', 'wb') as f:
    np.save(f, colors)

    
plt.show()