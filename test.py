import matplotlib.pyplot as plt
import numpy as np
from tempfile import TemporaryFile
import time
import os
from os import path


# prepare some coordinates
x, y, z = np.indices((20, 20, 20))
# x, y, z = np.indices((30, 30, 30))
# x, y, z = np.indices((100, 100, 100))
# draw cuboids in the top left and bottom right corners, and a link between
# them
cube1 = (x < 7) & (y < 7) & (z < 7)
cube2 = (x >= 13) & (y >= 13) & (z >= 13)
link = abs(x - y) + abs(y - z) + abs(z - x) <= 2

# combine the objects into a single boolean array
voxels = cube1 | cube2 | link

# set the colors of each object
colors = np.empty((len(x),len(y),len(z),3), np.float32)

#print(voxels)
colors[link] = (0,0.5,0)
colors[cube1] = (0.1,0.8,0)
colors[cube2] = (0.1,0.1,1)
#print(colors)
# # and plot everything
ax = plt.figure().add_subplot(projection='3d')
ax.voxels(voxels, facecolors=colors, edgecolor='k')

# while True:


#     if round(time.time())%2==0:
#         try:
#             if path.exists("test.npy"):
#                 os.remove("test.npy")
#             with open('test.npy', 'wb') as f:
#                 f.truncate(0)
#                 np.save(f, colors)
#             f.close()

#             print("done")
#         except:
#             print("failed opening file")
    
plt.show()