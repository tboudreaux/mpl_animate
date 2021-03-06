import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from tqdm import tqdm

import cProfile

from mplEasyAnimate import animation

def main():
    figList = list()
    filename1 = 'TestAnimation.mp4'
    filename2 = 'TestAnimation_context.mp4'
    t = 100
    N = 100

    guass = np.random.normal(size=(t, 2, N))

    anim = animation(filename1, fps=60)
    for coord in tqdm(guass):
        fig, ax = plt.subplots(1, 1, figsize=(10, 7))
        ax.plot(coord[0], coord[1], 'o')
        anim.add_frame(fig)
        plt.close(fig)

    anim.close()

    with animation(filename2, fps=60) as anim:
        for coord in tqdm(guass):
            fig, ax = plt.subplots(1, 1, figsize=(10, 7))
            ax.plot(coord[0], coord[1], 'o')
            anim.add_frame(fig)
            plt.close(fig)


if __name__ == '__main__':
    main()
    # cProfile.run('main()')
