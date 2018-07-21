# Super simple (and likely stupid) way of making animations with maptlotlib

I wanted to make a plot, then I wanted that plot to move into another plot. That was hard to do, then I foung imageio. But that was slow cause I had to save every figure to disk, then I rememberd that memory existed, then it was faster. Now I have packeged this so it is super easy, now we are here.

## Example

```python
import matplotlib.pyplot as plt
import numpy as np

from mplEasyAnimate import animation

figList = list()  # figures should be stoed in a list
filename = 'TestAnimation.mp4'
t = 10  
N = 50  

guass = np.random.normal(size=(t, 2, N))


for coord in guass:
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    ax.plot(coord[0], coord[1], 'o')
    figList.append(fig)

animation(filename, figList)
```

if you want to run this in jupyter the above example should be modified as follows

```python
import matplotlib.pyplot as plt
import numpy as np

from mplEasyAnimate import animation

figList = list()  # figures should be stoed in a list
filename = 'TestAnimation.mp4'
t = 10  
N = 50  

guass = np.random.normal(size=(t, 2, N))

plt.ioff()
for coord in guass:
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    ax.plot(coord[0], coord[1], 'o')
    figList.append(fig)

animation(filename, figList)
plt.ion()
```

Basically this keeps jupyter from rendering every figure you make.
