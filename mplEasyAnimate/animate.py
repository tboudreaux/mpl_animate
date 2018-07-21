import io
import matplotlib.pyplot as pyplot
import imageio
from scipy.misc import imresize
from tqdm import tqdm


class animation:
    def __init__(self, filename, figList, size=None):
        self.filename = filename
        self.figList = figList
        self.size = size
        self.__make_animation__()

    def __make_animation__(self):
        with imageio.get_writer(self.filename, mode='I') as writer:
            for i, figure in tqdm(enumerate(self.figList), total=len(self.figList)):
                buf = io.BytesIO()
                figure.savefig(buf, format='png', bbox_inches='tight')
                buf.seek(0)
                image = imageio.imread(buf)
                if i == 0 and self.size is None:
                    self.size = image.shape
                image = imresize(image, self.size)
                writer.append_data(image)
                buf.close()

    def __repr__(self):
        out = list()
        out.append('Animation made up of: {}'.format(len(self.figList)))
        out.append('Animation size: {}'.format(self.size))
        out.append('Animation path: {}'.format(self.filename))
        return '\n'.join(out)
