# What's New?
	- Added the ability to transition between added frames with either a cross dissolve (built in) or using a custom transition function
	- Added Ability to Change the Facecolor of the saved figure
	- Upaded the image loading away from scipy.misc to skimage

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

## API Documentation
mplEasyAnimate has a relativley simple API, only making use of one (animation) class.
The API is however well documented in the code as well as <a href="https://algebrist.com/~tboudreaux/docs/mplEasyAnimate/index.html#">here</a>

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


## Dynamically Adding Frames (sorta recommended)
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
for i, coord in enumerate(guass):
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    ax.plot(coord[0], coord[1], 'o')
    anim.add_frame(fig)
    plt.close(fig)

anim.close()
```

here every 10 frames I add all the frames to the animation and then I flush the buffer at the end to make sure that the animation is readable.


## Context Manager (very recommended)
mplEasyAnimate can easily called using context managers which will take care of closing the files for you, here is an example
```python
import matplotlib.pyplot as plt
import numpy as np

from mplEasyAnimate import animation


filename = 'TestAnimation.mp4'
t = 100
N = 50

guass = np.random.normal(size=(t, 2, N))

with animation(filename, fps=60) as anim:
	for i, coord in enumerate(guass):
		fig, ax = plt.subplots(1, 1, figsize=(10, 7))
		ax.plot(coord[0], coord[1], 'o')
		anim.add_frame(fig)
		plt.close(fig)

```
## Smoothing
mplEasyAnimate can automatically apply a cross dissolve between frames. This is turned on with the autoSmoothing parameter to animation. There is also a smoothingFrames parameter which describes how many frames will be used to dissolve. Note that this smoothes the entire frame, not just the graphed data.
```python
import matplotlib.pyplot as plt
import numpy as np

from mplEasyAnimate import animation


filename = 'TestAnimation.mp4'
t = 100
N = 50

guass = np.random.normal(size=(t, 2, N))

with animation(filename, fps=60, autoSmooth=True, smoothingFrame=60) as anim:
	for i, coord in enumerate(guass):
		fig, ax = plt.subplots(1, 1, figsize=(10, 7))
		ax.plot(coord[0], coord[1], 'o')
		anim.add_frame(fig)
		plt.close(fig)

```

## Saveing the Final Frame
Sometimes when you are giving a talk you want to transition to a slide where the image looks the same as the final frame of the animation; however, because mplEasyAnimate rescales some stuff internally just saving the figure with matplotlib won't provide a seemless transition. mplEasyAnimate allows you to save the final frame of an animation to a png which you can use to make these transitions smooth!

```python
with animation(filename, fps=60, saveFinalFrame=True) as anim:
	for i, coord in enumerate(guass):
		fig, ax = plt.subplots(1, 1, figsize=(10, 7))
		ax.plot(coord[0], coord[1], 'o')
		anim.add_frame(fig)
		plt.close(fig)

```

This will produce a file called "finalFrame.png" in your current working directory

## Some Examples
Here are some examples of output<br>
![Alt Text](https://github.com/tboudreaux/mpl_animate/blob/master/examples/example.gif?raw=true)

Another example can be seen here, this shows three views of a the evolution of a Globular Cluster through a couple Mega Years <br>
![Alt Text](https://github.com/tboudreaux/mpl_animate/blob/master/examples/ClusterAnimation.gif?raw=true)

An Example showing the developement of exoplanet statistics between the 90s and the 2020s (Credit: <a href="https://www.kerockcliffe.com/">Keighley Rockcliffe</a>)


https://user-images.githubusercontent.com/6620251/225698910-994ea8a3-496c-4331-9ddb-4acff3405f1f.mp4


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

