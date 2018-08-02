import io
import imageio
from scipy.misc import imresize
from tqdm import tqdm
import matplotlib.pyplot as plt


class animation:
    def __init__(self, filename, size=None, pbar=False, macro_block_size=16):
        self.filename = filename
        self.size = size
        self.mbs = macro_block_size
        self.writer = imageio.get_writer(self.filename, mode='I', macro_block_size=self.mbs)
        self.pbar = pbar
        self.frame_number = 0
        self.closed = False


    def __scale_to_mbs_frame__(self, img):
        xnew = img.shape[0] + self.mbs - img.shape[0]%self.mbs
        ynew = img.shape[1] + self.mbs - img.shape[1]%self.mbs
        return imresize(img, (xnew, ynew))

    def __make_animation_from_raw_list__(self, figList):
        for figure in tqdm(figList, disable=not self.pbar):
            buf = io.BytesIO()
            figure.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            image = imageio.imread(buf)
            if self.frame_number == 0 and self.size is None:
                image = self.__scale_to_mbs_frame__(image)
                self.size = image.shape
            image = imresize(image, self.size)
            self.writer.append_data(image)
            buf.close()
            self.frame_number += 1

    def add_frames(self, figList):
        self.__make_animation_from_raw_list__(figList)

    def add_single_frame(self, frame):
        self.__make_animation_from_raw_list__([frame])

    def close(self):
        self.closed = True
        self.writer.close()

    def __del__(self):
        self.writer.close()

    def __repr__(self):
        out = list()
        out.append('Animation size: {}'.format(self.size))
        out.append('Animation path: {}'.format(self.filename))
        return '\n'.join(out)


class AutoAnimation:
    def __init__(self, filename, total, pbar=False, size=None, framebuffer=10):
        self.anim = animation(filename, size=size, pbar=False)
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
        return self.total_frames

    def close(self):
        if not self.closed:
            if self.buffered_frames:
                self.anim.add_frames(self.frame_list)
                del(self.frame_list)
            self.anim.close()
            self.progress_bar.close()

            self.closed = True
            
    def __del__(self):
        self.close()




