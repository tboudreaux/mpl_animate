import io
import numpy as np
import imageio
from skimage.transform import resize
from skimage import img_as_ubyte
from tqdm import tqdm
import matplotlib
import traceback
from PIL import Image

from typing import Tuple, Callable


class animation:
    """
    Animation class. This class requires will take in a matplotib figure
    object and add it to an imageio open video file.

    Attributes:
    ----------
    filename : str
        Filename to animation will be written to
    size : Tuple[int]
        X, Y dimensions of image (x, y)
    pbar : bool
        Flag controlling use of a tqdm progress bar
    dpi : int
        image dpi (dots per inch)
    fps : int
        frames per second to draw animation at

    Examples:
    --------
    >>> import matplotlib.pyplot as plt
    >>> import numpy as np
    >>> from animate import animation
    >>> fig, ax = plt.subplots()
    >>> x = np.linspace(0, 2*np.pi, 100)
    >>> line, = ax.plot(x, np.sin(x))
    >>> anim = animation('test.mp4', size=(500, 500), pbar=True)
    >>> for i in range(100):
    >>>     line.set_ydata(np.sin(x + i/10.0))
    >>>     anim.add_frame(fig)
    >>> anim.close()


    """

    def __init__(
            self : "animation",
            filename : "str",
            size : "Tuple[int,int]" = None,
            pbar : "bool" = False,
            mbs : "int" = 16,
            dpi : "int" = 150,
            init_frame : "matplotlib.figure.Figure" = None,
            init_ax : "matplotlib.axes._subplots.AxesSubplot" = None,
            fps : "int" = 5,
            interactive : "bool" = False,
            autoSmooth : "bool" = False,
            smoothingFrames : "int" = 5,
            saveFinalFrame : "int" = False,
            smoothingTime : float = None,
            smoothingFunction : "Callable" = None
            ):
        """
        Constructs all the necessary attributes for the animation object.
        If init_frame and init_ax are provided then the animation will
        be drawn on top of the init_frame. This can be used to speed up
        the animation process. If the matplotlib enviroment is interactive
        then that will be recorded and restored when the animation is closed.

        Parameters:
        ----------
        filename : str
            Filename to write animation too
        size : tuple[int], default=None
            X, Y dimensions of image (x, y)
        pbar : bool, default=False
            Use tqdm progress bar
        mbs : int, default=16
            image macro_block_size to use
        dpi : int, default=150
            image dpi
        init_frame : matplotlib.figure.Figure, default=None
            canvas to draw on, use to speed up animation
        init_ax : matplotlib.axes._subplots.AxesSubplot, default=None
            axes to go with init_frame
        fps : int, default=5
            frames per second to draw animation at
        ineractive : bool, default=False
            disable matplotlib interactive mode on animation start
        autoSmooth : bool, default=False
            Smooth transitions between frames by adding intermediate frames
        smoothingFrames : int, default=5
            Number of frames to add between each frame
        saveFinalFrame : bool, default=False
            Save the final frame of the animation to a png file called finalFrame.png
        smoothingTime : float, default=None
            Time in seconds to smooth over. If this is provided then
            smoothingFrames will be ignored.
        smoothingFunction : Callable, default=None
            Function to use to smooth frames. This function should take two
            frames along with a frame index and the total number of frames to
            be smoothed over and return a new frame of the same size. If this
            is not provided and autoSmooth is turned on then a linear
            interpolation between the two frames will be used (cross fade). The
            function should return a numpy array of the same size as the input
            frames and as type np.uint8.
        """
        self.filename = filename
        self.size = size
        self._mbs = mbs
        self._writer = imageio.get_writer(
                self.filename,
                mode='I',
                macro_block_size=self._mbs,
                fps=fps
                )
        self.fps = fps
        self.pbar = pbar
        self._frame_number = 0
        self._closed = False
        self.dpi = dpi
        self._cframe = None
        if init_frame and init_ax:
            self._init_frame(init_frame, init_ax)

        self._init_interactive = matplotlib.is_interactive()
        if self._init_interactive and not interactive:
            matplotlib.interactive(False)
        else:
            matplotlib.interactive(interactive)
        if autoSmooth:
            assert smoothingFrames > 0

        self._autosmooth = autoSmooth
        self._prevFrame = None


        # Set up smoothing
        if smoothingTime is None:
            self._smoothingFrames = smoothingFrames
        else:
            self._smoothingFrames = int(smoothingTime*fps)

        if smoothingFunction is None:
            self._smoothingFunction = self._linear_interpolation
        else:
            self._smoothingFunction = smoothingFunction

        self._saveFinalFrame = saveFinalFrame

    def _init_frame(self : "animation",
                    init_frame : "matplotlib.figure.Figure",
                    init_ax : "matplotlib.axes._subplots.AxesSubplot"
                    ):
        """ Copy the init_frame to the animation canvas."""
        self._cframe = init_frame.canvas.copy_from_bbox(init_ax.bbox)

    def _scale_to_mbs_frame(self : "animation",
                            img : "np.ndarray"
                            ) -> "np.ndarray":
        """Rescale image to be compatible with macro_block_scale."""
        xnew = img.shape[0] + self._mbs - img.shape[0]%self._mbs
        ynew = img.shape[1] + self._mbs - img.shape[1]%self._mbs
        return (255*resize(img, (xnew, ynew))).astype(np.uint8)


    def _write_frame(self : "animation",
                     frame : "np.ndarray"
                     ):
        """
        Write frame to animation and incriment frame number. Also update
        the previous frame.
        """
        self._writer.append_data(frame)
        self._frame_number += 1
        self._prevFrame = frame

    @staticmethod
    def _linear_interpolation(
            prevFrame : "np.ndarray",
            cFrame : "np.ndarray",
            fID : "int",
            smoothingFrames : "int"
            ) -> "np.ndarray":
        """
        Linear interpolation between two frames. (cross fade)

        Parameters:
        ----------
        prevFrame : np.ndarray
            Previous frame
        cFrame : np.ndarray
            Current frame
        fID : int
            Frame index
        smoothingFrames : int
            Total number of frames to be smoothed over

        Returns:
        -------
        transitionFrame : np.ndarray
            New frame
        """
        prevWeight = 1-((fID+1)/smoothingFrames)
        finalWeight = (fID+1)/smoothingFrames
        transitionFrame = prevWeight * prevFrame + finalWeight*cFrame
        return transitionFrame.astype(np.uint8)

    def _insert_smoothed_frames(self : "animation",
                                cFrame : "np.ndarray"
                                ):
        """
        Insert smoothed frames between the current frame and the previous
        using a linear interpolation. (cross fade)
        """
        if self._prevFrame is not None:
            finalImage = cFrame.copy()
            transitionFrame = np.zeros_like(finalImage)
            for frameID in range(self._smoothingFrames):
                transitionFrame = self._smoothingFunction(
                        self._prevFrame,
                        finalImage,
                        frameID,
                        self._smoothingFrames
                        )
                self._write_frame(transitionFrame)



    def _make_animation_from_raw_list(self : "animation",
                                      frameList : "list",
                                      facecolor='white'
                                      ):
        """
        Make animation from a list of frames.

        Parameters:
        ----------
        frameList : list
            List of matplotlib figures
        facecolor : str, default='white'
            Background color of animation
        """
        for frame in tqdm(frameList, disable=not self.pbar):
            if frame.dpi < self.dpi:
                frame.dpi = self.dpi
            frame.patch.set_facecolor(facecolor)
            frame.canvas.draw()
            image = np.array(frame.canvas.renderer._renderer)
            if self._frame_number == 0 and self.size is None:
                image = self._scale_to_mbs_frame(image)
                self.size = image.shape
            if image.size != self.size:
                image = (255*resize(image, self.size)).astype(np.uint8)
            if self._autosmooth:
                self._insert_smoothed_frames(image)
            self._write_frame(image)

    def add_frames(
            self : "animation",
            frameList : "list[matplotlib.figure.Figure]",
            facecolor : "str" = 'white'
            ):
        """
        User facing call to add list of frames.

        Parameters
        ----------
        frameList : List[matplotlib.figure]
            List of matplotlib figures
        facecolor : str, default='white'
            Background color of animation
        """
        self._make_animation_from_raw_list(frameList, facecolor=facecolor)

    def add_frame(
            self : "animation",
            frame : "matplotlib.figure.Figure",
            facecolor : "str" = 'white'
            ):
        """
        User facing call to add a single frame.

        Parameters
        ----------
        frame : matplotlib.figure
            Matplotlib figure
        facecolor : str, default='white'
            Background color of animation
        """
        self._make_animation_from_raw_list([frame], facecolor=facecolor)

    def __enter__(self):
        """
        Context Manager Entrance
        """
        return self

    def _save_frame_as_png(
            self : "animation",
            frame : "np.ndarray",
            filename :  "str"
            ):
        """
        Save frame as png.

        Parameters
        ----------
        frame : np.ndarray
            Frame to be saved
        filename : str
            Name of file to be saved
        """
        im = Image.fromarray(frame)
        im.save(filename)

    def __exit__(self, exc_type, exc_value, tb):
        """
        Context Manager Exit
        """
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        if self._init_interactive:
            matplotlib.interactive(True)
        if self._prevFrame is not None and self._saveFinalFrame:
            self._save_frame_as_png(self._prevFrame, "finalFrame.png")

        self.close()
        return True

    def close(self):
        """Safe close of animation."""
        self._closed = True
        self._writer.close()

    def __del__(self):
        """Invocation of safe close on descope of animation object."""
        self._writer.close()

    def __repr__(self):
        """String Representation."""
        out = f"<{self.__class__.__name__} - {self.filename} : {self.fps} fps : dpi : {self.dpi}>"
        return out
