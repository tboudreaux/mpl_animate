import io
import imageio
from scipy.misc import imresize
from tqdm import tqdm


class animation:
    def __init__(self, filename, size=None, pbar=False):
        self.filename = filename
        self.size = size
        self.writer = imageio.get_writer(self.filename, mode='I')
        self.pbar = pbar

    def __make_animation_from_raw_list__(self, figList):
        for i, figure in tqdm(enumerate(figList), total=len(figList), disable=not self.pbar):
            buf = io.BytesIO()
            figure.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            image = imageio.imread(buf)
            if i == 0 and self.size is None:
                self.size = image.shape
            image = imresize(image, self.size)
            self.writer.append_data(image)
            buf.close()

    def add_frames(self, figList):
        self.__make_animation_from_raw_list__(figList)

    def close(self):
        self.writer.close()

    def __del__(self):
        self.writer.close()


    def __repr__(self):
        out = list()
        out.append('Animation size: {}'.format(self.size))
        out.append('Animation path: {}'.format(self.filename))
        return '\n'.join(out)
