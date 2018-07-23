import matplotlib.pyplot as plt
import matplotlib
import numpy as np

from mplEasyAnimate import animation, AutoAnimation

figList = list()
filename = 'TestAnimation.mp4'
t = 10
N = 50

guass = np.random.normal(size=(t, 2, N))


anim = AutoAnimation(filename, t, framebuffer=5, pbar=True)
plt.ion()
for coord in guass:
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    ax.plot(coord[0], coord[1], 'o')
    anim.add_frame(fig)
    plt.close(fig)

figures=[manager.canvas.figure
         for manager in matplotlib._pylab_helpers.Gcf.get_all_fig_managers()]
print(figures)

for i, figure in enumerate(figures):
    figure.savefig('figure%d.png' % i)


