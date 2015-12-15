# coding: utf8
from setuptools import setup

setup(name='tiare', version='0.1', description='sound',
      author='Maxime Le Coz', author_email='maxime.lecoz@gmail.com',
      packages=["analysers", "view"],
      install_requires=["pysoundfile", "pyqtgraph", 'pyside'],
      package_data={},
      zip_safe=True
      )
