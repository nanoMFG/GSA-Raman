import os
from setuptools import find_packages, setup

with open(os.path.join('.', 'VERSION')) as version_file:
    version = version_file.read().strip()

setup(
    name='gsaraman',
    version=version,
    long_description=open('README.md').read(),
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    entry_points={
          'gui_scripts': [
              'gsaraman = gsaraman.__main__:main'
          ]
      }
)
