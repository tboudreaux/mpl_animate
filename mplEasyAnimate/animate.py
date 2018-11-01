import io
import numpy as np
import imageio
from scipy.misc import imresize
from tqdm import tqdm


class animation:
    """
    Animation class. This class requires will take in a matplotib figure
    object and add it to an imageio open video file.

    Attributes:
        filename: Filename to write animation too [str]
        size: X, Y dimensions of image (x, y) [float tuple] [default first frame size]
        pbar: Use tqdm progress bar [bool] [default False]
        mbs: image macro_block_size to use [int] [default 16]
    """
    def __init__(self, filename, size=None, pbar=False, mbs=16, dpi=150):

        self.filename = filename
        self.size = size
        self.mbs = mbs
        self.writer = imageio.get_writer(self.filename, mode='I', macro_block_size=self.mbs)
        self.pbar = pbar
        self.frame_number = 0
        self.closed = False
        self.dpi = dpi

    def __scale_to_mbs_frame__(self, img):
        """Rescale image to be compatible with macro_block_scale."""
        xnew = img.shape[0] + self.mbs - img.shape[0]%self.mbs
        ynew = img.shape[1] + self.mbs - img.shape[1]%self.mbs
        return imresize(img, (xnew, ynew))

    def __make_animation_from_raw_list__(self, frameList):
        """
        Given list of matplotlib figures add them to animatio.

        Args:
            frameList: List of matplotlib figures [list of figure objects]
        """
        for frame in tqdm(frameList, disable=not self.pbar):
            if frame.dpi < self.dpi:
                frame.dpi = self.dpi
            frame.canvas.draw()
            image = np.array(frame.canvas.renderer._renderer)
            if self.frame_number == 0 and self.size is None:
                image = self.__scale_to_mbs_frame__(image)
                self.size = image.shape
            if image.size != self.size:
                image = imresize(image, self.size)
            self.writer.append_data(image)
            self.frame_number += 1

    def add_frames(self, frameList):
        """
        User facing call to add list of frames.

        Args:
            frameList: List of matplotlib figures [list of figure objects]
        """
        self.__make_animation_from_raw_list__(frameList)

    def add_frame(self, frame):
        """
        User facing call to add single frame.

        Args:
            frame: matplotlig figure to be added to animation [figure]

        """
        self.__make_animation_from_raw_list__([frame])

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


class autoAnimation:
    """
    AutoAnimation class. This class requires will take in a matplotib figure
    object and add it to an frame buffer. The frame buffer will get dumped into
    an Imageio open video file once it is full.

    Attributes:
        filename: Filename to write animation too [str]
        total: The total number of frames that will be in the final animation [int]
        size: X, Y dimensions of image (x, y) [float tuple] [default first frame size]
        framebuffer: The size of the framebuffer to use [int] [default 10]
        pbar: Use tqdm progress bar [bool] [default False]
        mbs: image macro_block_size to use [int] [default 16]

    """
    def __init__(self, filename, total, pbar=False, size=None, framebuffer=10, mbs=16):
        self.anim = animation(filename, size=size, pbar=False, mbs=mbs)
        self.pbar = pbar
        self.frame_list = list()
        self.total_frames = 0
        self.frame_buffer = framebuffer
        if self.pbar:
            self.progress_bar = tqdm(total=total)
        self.total = total
        self.closed = False
        self.has_frames = False
        self.buffered_frames = False

    def add_frame(self, frame):
        """
        User Facing method to add frame to AutoAnimation

        Args:
            frame: matplotlig figure to become nth frame in animation [figure]

        Raises:
            IndexError: If you try and add more frames than total to and AutoAnimation is Open
            EnviromentError: If you try and add a frame when AutoAnimation has closed
        """
        if not self.closed:
            self.has_frames = True
            self.total_frames += 1
            if self.total_frames <= self.total:
                self.frame_list.append(frame)
                self.buffered_frames = True
                if self.total_frames % self.frame_buffer == 0:
                    self.anim.add_frames(self.frame_list)
                    self.frame_list = list()
                    self.buffered_frames = False
                    if self.pbar:
                        self.progress_bar.update(self.frame_buffer)
                if self.total_frames == self.total:
                    self.close()
            else:
                raise IndexError('Cannot add frame {} to animation with max frames {}'.format(self.total_frames, self.total))
        else:
            raise EnvironmentError('AutoAnimation of size {} has been closed, no more frames may be added'.format(self.total_frames))

    def __len__(self):
        """
        len overload

        Returns:
            total number of frames currently in AutoAnimation
        """
        return self.total_frames

    def close(self):
        """Safe Termination of AutoAnimation, no more frames can be added once this is called."""
        if not self.closed:
            if self.buffered_frames:
                self.anim.add_frames(self.frame_list)
                del(self.frame_list)
            self.anim.close()
            self.progress_bar.close()

            self.closed = True

    def __repr__(self):
        """Auto Animation repr, returns composed animation repr."""
        return str(self.anim)
            
    def __del__(self):
        """Invocation of safe close on descope of animation object."""
        self.close()




