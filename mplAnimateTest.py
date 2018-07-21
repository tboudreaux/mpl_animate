import matplotlib.pyplot as plt
import numpy as np

from mplEasyAnimate import animation, AutoAnimation

figList = list()
filename = 'TestAnimation.mp4'
t = 10
N = 50

guass = np.random.normal(size=(t, 2, N))


anim = AutoAnimation(filename, t, framebuffer=5, pbar=True)
for coord in guass:
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    ax.plot(coord[0], coord[1], 'o')
    anim.add_frame(fig)

print('HERE')


