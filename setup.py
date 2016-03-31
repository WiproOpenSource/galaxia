from distutils.core import setup
from setuptools import find_packages
setup(
     name='galaxia',
     version='1.0',
     packages=find_packages(),
     entry_points={
         'console_scripts':[
             'gapi = galaxia.gcmd.api:main',
             'galaxia = galaxiaclient.galaxia:main',
             'grenderer = galaxia.gcmd.renderer:main',
             'gexporter = galaxia.gcmd.exporter:main'
         ]

     },
     include_package_data=True,
     author='wipro'
)