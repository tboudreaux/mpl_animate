from setuptools import setup
from os import path

HERE = path.abspath(path.dirname(__file__))

setup(name='mplEasyAnimate',
      version='0.6.1',
      description='Super Simple Library for matplotlib animation',
      url='https://github.com/tboudreaux/mpl_animate',
      author='Thomas Boudreaux',
      author_email='thomas@boudreauxmail.com',
      license='MIT',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3'
      ],
      install_requires=[
          'numpy>=1.12.0',
          'imageio>=2.3.0',
          'matplotlib>=2.0.2',
          'scipy>=0.19.0',
          'tqdm>=4.23.4',
          'imageio-ffmpeg>=0.4.1',
          'scikit-image>=0.15.0',
          'Pillow>=9.4.0'
      ],
      packages=['mplEasyAnimate'],
      zip_safe=False)
