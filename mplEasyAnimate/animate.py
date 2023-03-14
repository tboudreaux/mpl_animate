import io
import numpy as np
import imageio
from skimage.transform import resize
from skimage import img_as_ubyte
from tqdm import tqdm
import matplotlib
import traceback


class animation:
    """
    Animation class. This class requires will take in a matplotib figure
    object and add it to an imageio open video file.

    Attributes:
        filename: Filename to write animation too [str]
        size: X, Y dimensions of image (x, y) [float tuple] [default first frame size]
        pbar: Use tqdm progress bar [bool] [default False]
        mbs: image macro_block_size to use [int] [default 16]
        dpi: image dpi [int] [defualt 150]
        init_frame: canvas to draw on, use to speed up animation
                    user needs to handel clearing the canvas [figure]
                    [default None]
        init_ax: axes to go with init_frame [axis] [default None]
        fps: frames per second to draw animation at [int] [default 5]
        ineractive: disable matplotlib interactive mode on animation start
                    this helps mitigate a memory leak present in ipython when
                    plotting many figures. Interactive more will be resumes 
                    on close of figure [bool] [default False]. 
    """

    def __init__(self, filename, size=None, pbar=False, mbs=16, dpi=150, init_frame = None, init_ax=None, fps=5, interactive=None):
        self.filename = filename
        self.size = size
        self.mbs = mbs
        self.writer = imageio.get_writer(self.filename, mode='I', macro_block_size=self.mbs, fps=fps)
        self.pbar = pbar
        self.frame_number = 0
        self.closed = False
        self.dpi = dpi
        self.cframe = None
        if init_frame and init_ax:
            self.__init_frame__(init_frame, init_ax)

        self.init_interactive = matplotlib.is_interactive()
        if self.init_interactive and not interactive:
            matplotlib.interactive(False)
        else:
            matplotlib.interactive(interactive)

    def __init_frame__(self, init_frame, init_ax):
        self.cframe = init_frame.canvas.copy_from_bbox(init_ax.bbox)

    def __scale_to_mbs_frame__(self, img):
        """Rescale image to be compatible with macro_block_scale."""
        xnew = img.shape[0] + self.mbs - img.shape[0]%self.mbs
        ynew = img.shape[1] + self.mbs - img.shape[1]%self.mbs
        return (255*resize(img, (xnew, ynew))).astype(np.uint8)

    def __make_animation_from_raw_list__(self, frameList, facecolor='white'):
        """
        Given list of matplotlib figures add them to animatio in mode i.

        Args:
            frameList: List of matplotlib figures [list of figure objects]
            facecolor: Facecolor of canvas when written to animation [string: default->'white']
        """
        for frame in tqdm(frameList, disable=not self.pbar):
            if frame.dpi < self.dpi:
                frame.dpi = self.dpi
            frame.patch.set_facecolor(facecolor)
            frame.canvas.draw()
            image = np.array(frame.canvas.renderer._renderer)
            if self.frame_number == 0 and self.size is None:
                image = self.__scale_to_mbs_frame__(image)
                self.size = image.shape
            if image.size != self.size:
                image = (255*resize(image, self.size)).astype(np.uint8)
            self.writer.append_data(image)
            self.frame_number += 1


    def add_frames(self, frameList, facecolor='white'):
        """
        User facing call to add list of frames.

        Args:
            frameList: List of matplotlib figures [list of figure objects]
            facecolor: Facecolor of canvas when written to animation [string: default->'white']
        """
        self.__make_animation_from_raw_list__(frameList, facecolor=facecolor)

    def add_frame(self, frame, facecolor='white'):
        """
        User facing call to add single frame.

        Args:
            frame: matplotlig figure to be added to animation [figure]
            facecolor: Facecolor of canvas when written to animation [string: default->'white']

        """
        self.__make_animation_from_raw_list__([frame], facecolor=facecolor)

    def __enter__(self):
        """
        Context Manager Entrance
        """
        return self

    def __exit__(self, exc_type, exc_value, tb):
        """
        Context Manager Exit
        """
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        if self.init_interactive:
            matplotlib.interactive(True)

        self.close()
        return True

    def close(self):
        """Safe close of animation."""
        self.closed = True
        self.writer.close()

    def __del__(self):
        """Invocation of safe close on descope of animation object."""
        self.writer.close()

    def __repr__(self):
        """String Representation."""
        out = list()
        out.append('Animation size: {}'.format(self.size))
        out.append('Animation path: {}'.format(self.filename))
        return '\n'.join(out)
