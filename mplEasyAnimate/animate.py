import io
import imageio
from scipy.misc import imresize
from tqdm import tqdm
from moviepy.editor import VideoClip
from moviepy.video.io.bindings import mplfig_to_npimage


class animation:
    """
    Animation class. This class requires will take in a matplotib figure
    object and add it to an imageio open video file.

    Attributes:
        filename: Filename to write animation too [str]
        size: X, Y dimensions of image (x, y) [float tuple] [default first frame size]
        pbar: Use tqdm progress bar [bool] [default False]
        mbs: image macro_block_size to use [int] [default 16]
        mode: use imagio or moviepy [str] [default m]
              m -> moviepy [generally faster]
              i -> imagieo
    """
    def __init__(self, filename, size=None, pbar=False, mbs=16, mode='m'):

        self.filename = filename
        self.size = size
        self.mbs = mbs

        if not self.__check_mode__(mode):
            raise AttributeError("mode {} not recogninzed. Valid modes are 'm' for moviePy and 'i' for imageio")
        
        self.mode = mode
        self.writer = imageio.get_writer(self.filename, mode='I', macro_block_size=self.mbs)
        self.pbar = pbar
        self.frame_number = 0
        self.closed = False
    

    @staticmethod
    def __check_mode__(mode):
        """
        Check if a mode is a valid mode.
        
        Args:
            mode: mode to check [str]

        Returnes:
            True if mode is valid ('m' or 'i') 
            False is mode is invalid
        """
        if mode == 'm' or mode == 'i':
            return True
        else:
            return False

    def __scale_to_mbs_frame__(self, img):
        """Rescale image to be compatible with macro_block_scale."""
        xnew = img.shape[0] + self.mbs - img.shape[0]%self.mbs
        ynew = img.shape[1] + self.mbs - img.shape[1]%self.mbs
        return imresize(img, (xnew, ynew))

    def __make_animation_from_raw_list_i__(self, frameList):
        """
        Given list of matplotlib figures add them to animatio in mode i.

        Args:
            frameList: List of matplotlib figures [list of figure objects]
        """
        for frame in tqdm(frameList, disable=not self.pbar):
            buf = io.BytesIO()
            frame.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            image = imageio.imread(buf)
            if self.frame_number == 0 and self.size is None:
                image = self.__scale_to_mbs_frame__(image)
                self.size = image.shape
            image = imresize(image, self.size)
            self.writer.append_data(image)
            buf.close()
            self.frame_number += 1

    def __make_animation_from_raw_list_m__(self, frameList):
        """
        Given list of matplotlib figures add them to animatio in mode m.

        Args:
            frameList: List of matplotlib figures [list of figure objects]
        """
        def frame_time_map(frameList, duration, frameRate):
            mapedFrameList = np.repeat(list(range(len(frameList))), int(np.ceil(duration*framerate/len(frameList))))
            return mapedFrameList
        def find_nearest(array, value):
            idx = (np.abs(array - value)).argmin()
            return idx
        timeMap = frame_time_map(frameList, self.duration, self.framerate)
        drawTimes = np.linspace(0, t, self.duration*self.framerate)
        make_frame = lambda t: frameList[timeMap[find_nearest(drawTimes, t)]]
        animation = VideoClip(make_frame, duration=1)


    def add_frames(self, frameList):
        """
        User facing call to add list of frames.

        Args:
            frameList: List of matplotlib figures [list of figure objects]
        """
        if self.mode == 'i':
            self.__make_animation_from_raw_list_i__(frameList)
        elif self.mode == 'm':
            self.__make_animation_from_raw_list_f__(framelist)

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




