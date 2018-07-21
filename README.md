# Super simple (and likely stupid) way of making animations with maptlotlib

I wanted to make a plot, then I wanted that plot to move into another plot. That was hard to do, then I foung imageio. But that was slow cause I had to save every figure to disk, then I rememberd that memory existed, then it was faster. Now I have packeged this so it is super easy, now we are here.

## Adding Frames all at once

mplEasyAnimate allow you to build up a list of matplotlib figures and turn them into an animation. You can send a full list in, this works well for small numbers of figures.

```python
import matplotlib.pyplot as plt
import numpy as np

from mplEasyAnimate import animation

figList = list()
filename = 'TestAnimation.mp4'
t = 10
N = 50

guass = np.random.normal(size=(t, 2, N))


for coord in guass:
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    ax.plot(coord[0], coord[1], 'o')
    figList.append(fig)

anim = animation(filename)
anim.add_frames(figList)
anim.close()
```

if you want to run this in jupyter the above example should be modified as follows

```python
import matplotlib.pyplot as plt
import numpy as np

from mplEasyAnimate import animation

figList = list()
filename = 'TestAnimation.mp4'
t = 10
N = 50

guass = np.random.normal(size=(t, 2, N))

pit.ioff()
for coord in guass:
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    ax.plot(coord[0], coord[1], 'o')
    figList.append(fig)
    
anim = animation(filename)
anim.add_frames(figList)
anim.close()
plt.ion()
```

Basically this keeps jupyter from rendering every figure you make.


## Dynamically Adding Frames
However, matplotlib will get uphappy if you have too many figures open at onece. I reccomend that for more than say 10 figures you dynamically add them (the figures) to the animation instead of doing it all at the end. See below

```python
import matplotlib.pyplot as plt
import numpy as np

from mplEasyAnimate import animation


filename = 'TestAnimation.mp4'
t = 100
N = 50

guass = np.random.normal(size=(t, 2, N))

anim = animation(filename)
figList = list()
for i, coord in enumerate(guass):
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    ax.plot(coord[0], coord[1], 'o')
    figList.append(fig)
    if i % 10 == 0:
        anim.add_frames(figList)
        [plt.close(x) for x in figList]
        figList = list()

anim.close()
```

here every 10 frames I add all the frames to the animation and then I flush the buffer at the end to make sure that the animation is readable.
