from setuptools import find_packages, setup


setup(
    name='gsaraman',
    version='1.2.0-beta',
    long_description=open('README.md').read(),
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    entry_points={
          'gui_scripts': [
              'gsaraman = gsaraman.__main__:main'
          ]
      }
)
