import numpy as np
import matplotlib.pyplot as plt
import mplEasyAnimate as mple
from tqdm import tqdm

def mkdata():
    return np.linspace(0, 10, 10), np.random.uniform(size=(10))

anim = mple.autoAnimation('Test2.mp4', 10, framebuffer=5, pbar=True)
for i in range(10):
    fig, ax = plt.subplots(1, 1)
    x, y = mkdata()
    ax.plot(x, y)
    anim.add_frame(fig)
    plt.close(fig)
anim.close()
