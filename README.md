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

also you will need to install ffmpeg, find instructions for you OS of choice

## Adding Frames all at once (not recommended)

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
    
anim = animation(filename, fps=30)
anim.add_frames(figList)
anim.close()
plt.ion()
```

Basically this keeps jupyter from rendering every figure you make. Note that this is a bad way of making animations if you have more than say 20 frames as it will force your computer to store each of those figures. For animations with thousands of frames than can require more memory than can be allocated and cause your program to crash on an OSError.


## Dynamically Adding Frames (recommended)
However, matplotlib will get uphappy if you have too many figures open at once. I reccomend that for more than say 10 figures you dynamically add them (the figures) to the animation instead of doing it all at the end. See below

```python
import matplotlib.pyplot as plt
import numpy as np

from mplEasyAnimate import animation


filename = 'TestAnimation.mp4'
t = 100
N = 50

guass = np.random.normal(size=(t, 2, N))

anim = animation(filename, fps=60)
figList = list()
for i, coord in enumerate(guass):
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    ax.plot(coord[0], coord[1], 'o')
    anim.add_frames(fig)
    plt.close(fig)

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

This should output something that looks like <br>
![Alt Text](https://github.com/tboudreaux/mpl_animate/blob/master/examples/example.gif?raw=true)

Another example can be seen here, this shows three views of a the evolution of a Globular Cluster through a couple Mega Years <br>
![Alt Text](https://github.com/tboudreaux/mpl_animate/blob/master/examples/ClusterAnimation.gif?raw=true)

## Speed
There are some ways to get speed / preformance improvments when making an animation

 1) Turn down the dpi, when you make an animation objects you can set the dpi as a keyword argument, lower dpis will render faster
 2) Reuse the same figure, consider the following code and how it reuses the same figure instead of creating a new one for each frame

```python
number = 100
rlayers = 100

circ, equib = make_circ(1, 1, number)
anim = animation('Animations/DrawStar_{}x{}.mp4'.format(number, rlayers), fps=30, dpi=5)
fig, ax = plt.subplots(1, 1, figsize=(10, 7))
ax.set_xlim(-1.1, 1.1)
ax.set_ylim(-1.1, 1.1)
ax.axis('off')

for particle in tqdm(range(1, number)):
    ax.plot(circ[particle-1:particle+1, 0, 0, 0], circ[particle-1:particle+1, 0, 0, 1], 'C0o-', linewidth=1)

    anim.add_frame(fig)


d0 = np.pi/(rlayers/2)
for theta in tqdm(np.arange(d0, 2*np.pi-d0/2, d0)):
    R = np.sqrt((circ[:, 0, 0, 0]**2) + (circ[:, 0, 0, 1]**2))
    ax.plot(R*np.cos(theta), R*np.sin(theta), 'C0o-', linewidth=1)
    
    anim.add_frame(fig)
    
for theta in tqdm(np.arange(d0, 2*np.pi+d0, d0)):
    R = np.sqrt((circ[:, 0, 0, 0]**2) + (circ[:, 0, 0, 1]**2))
    
    x1, y1 = R*np.cos(theta), R*np.sin(theta)
    x2, y2 = R*np.cos(theta+d0), R*np.sin(theta+d0)
    ax.plot([x1, x2], [y1, y2], 'C0', linewidth=1)
    anim.add_frame(fig)

plt.close(fig)
anim.close()
```
 3) turn off the axes, drawing the x and y axes is one of the slowest parts of matplotlib's drawing process, if they are not nessicairy for the animation consider turning them off (see the above code block).

## Documentation
I generally describe myself as a crazy script gibbon, meaning I have terrible development practices. I am far to lazy to learn how to use a proper documentation tool like Sphix so I have coppied all the pydoc output here, it can also be found in the docs directory in nice, easy to read, ASCII files. 

<pre>
mplEasyAnimate.animation = class animation(builtins.object)
 |  Animation class. This class requires will take in a matplotib figure
 |  object and add it to an imageio open video file.
 |
 |  Attributes:
 |      filename: Filename to write animation too [str]
 |      size: X, Y dimensions of image (x, y) [float tuple] [default first frame size]
 |      pbar: Use tqdm progress bar [bool] [default False]
 |      mbs: image macro_block_size to use [int] [default 16]
 |      fps: output video frames per second [int] [default 30] 
 |
 |  Methods defined here:
 |
 |  __del__(self)
 |      Invocation of safe close on descope of animation object.
 |
 |  __init__(self, filename, size=None, pbar=False, mbs=16)
 |      Initialize self.  See help(type(self)) for accurate signature.
 |
 |  __make_animation_from_raw_list__(self, frameList)
 |      Given list of matplotlib figures add them to animatio.
 |
 |      Args:
 |          frameList: List of matplotlib figures [list of figure objects]
 |
 |  __repr__(self)
 |      String Representation.
 |
 |  __scale_to_mbs_frame__(self, img)
 |      Rescale image to be compatible with macro_block_scale.
 |
 |  add_frame(self, frame)
 |      User facing call to add single frame.
 |
 |      Args:
 |          frame: matplotlig figure to be added to animation [figure]
 |
 |  add_frames(self, frameList)
 |      User facing call to add list of frames.
 |
 |      Args:
 |          frameList: List of matplotlib figures [list of figure objects]
 |
 |  close(self)
 |      Safe close of animation.
 |
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |
 |  __dict__
 |      dictionary for instance variables (if defined)
 |
 |  __weakref__
 |      list of weak references to the object (if defined)
</pre>
<pre>
mplEasyAnimate.autoAnimation = class autoAnimation(builtins.object)
 |  AutoAnimation class. This class requires will take in a matplotib figure
 |  object and add it to an frame buffer. The frame buffer will get dumped into
 |  an Imageio open video file once it is full.
 |
 |  Attributes:
 |      filename: Filename to write animation too [str]
 |      total: The total number of frames that will be in the final animation [int]
 |      size: X, Y dimensions of image (x, y) [float tuple] [default first frame size]
 |      framebuffer: The size of the framebuffer to use [int] [default 10]
 |      pbar: Use tqdm progress bar [bool] [default False]
 |      mbs: image macro_block_size to use [int] [default 16]
 |
 |  Methods defined here:
 |
 |  __del__(self)
 |      Invocation of safe close on descope of animation object.
 |
 |  __init__(self, filename, total, pbar=False, size=None, framebuffer=10, mbs=16)
 |      Initialize self.  See help(type(self)) for accurate signature.
 |
 |  __len__(self)
 |      len overload
 |
 |      Returns:
 |          total number of frames currently in AutoAnimation
 |
 |  __repr__(self)
 |      Auto Animation repr, returns composed animation repr.
 |
 |  add_frame(self, frame)
 |      User Facing method to add frame to AutoAnimation
 |
 |      Args:
 |          frame: matplotlig figure to become nth frame in animation [figure]
 |
 |      Raises:
 |          IndexError: If you try and add more frames than total to and AutoAnimation is Open
 |          EnviromentError: If you try and add a frame when AutoAnimation has closed
 |
 |  close(self)
 |      Safe Termination of AutoAnimation, no more frames can be added once this is called.
 |
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |
 |  __dict__
 |      dictionary for instance variables (if defined)
 |
 |  __weakref__
 |      list of weak references to the object (if defined)
</pre>
