# Super simple (and likely stupid) way of making animations with maptlotlib

I wanted to make a plot, then I wanted that plot to move into another plot. That was hard to do, then I foung imageio. But that was slow cause I had to save every figure to disk, then I rememberd that memory existed, then it was faster. Now I have packeged this so it is super easy, now we are here.

## Installation
You can either clone the repository and install it or install it via pip. Installing from the repository will get you the latest, possiblly broken, version. The pypi version is much more likley to be working, so if possible I recommend installing with pip.

```bash
git clone https://github.com/tboudreaux/mpl_animate.git
cd mpl_animate
python setup.py install
```
or 
```bash
pip install mplEasyAnimate
```

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
However, matplotlib will get uphappy if you have too many figures open at once. I reccomend that for more than say 10 figures you dynamically add them (the figures) to the animation instead of doing it all at the end. See below

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
        
        
plt.close('all')
anim.close()
```

here every 10 frames I add all the frames to the animation and then I flush the buffer at the end to make sure that the animation is readable.

## AutoAnimations
AutoAnimations are still (honestly like this entire project) a work in progress. However, they are eventually ment to be the main way that the user interfaces with mplEasyAnimate. The basic idea is that you pass an AutoAnimation one frame at a time and it will automatically deal with buffereing them and writing them to memory for you. Further down the line the goal is to make that an async processes to further limit overhead and hopefully make animations go faster (they still take sooo long to produce!). An example of how to use AutoAnimations is below:
```python
import numpy as np
import matplotlib.pyplot as plt
import mplEasyAnimate as mple
from tqdm import tqdm


def mkdata():
    return np.linspace(0, 10, 10), np.random.uniform(size=(10))


anim = mple.AutoAnimation('Test2.mp4', 10, framebuffer=5, pbar=True)
for i in range(10):
    fig, ax = plt.subplots(1, 1)
    x, y = mkdata()
    ax.plot(x, y)
    anim.add_frame(fig)
    plt.close(fig)
anim.close()
```
