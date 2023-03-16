import numpy as np
import matplotlib.pyplot as plt
import mplEasyAnimate as mple
from tqdm import tqdm

def mkdata():
    return np.linspace(0, 10, 10), np.random.uniform(size=(10))

with mple.animation("SmoothingTest.mp4", dpi=50, fps=60, autoSmooth=True, smoothingFrames=60, saveFinalFrame=True) as anim:
    for i in tqdm(range(10)):
        print(anim)
        fig, ax = plt.subplots(1, 1)
        x, y = mkdata()
        ax.plot(x, y)
        anim.add_frame(fig)
        plt.close(fig)
