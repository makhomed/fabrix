#!/usr/bin/env python

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Fabrix',
    version='0.2',
    description='Fabrix is Fabric extension for configuration management',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    keywords=['configuration management'],
    author='Gena Makhomed',
    author_email='makhomed@gmail.com',
    url='https://github.com/makhomed/fabrix',
    license='GPLv3',
    platforms=['Linux'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=['fabric>=1.12,<2.0', 'PyYAML>=3.10', 'jinja2>=2.7.2'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Clustering',
        'Topic :: System :: Software Distribution',
        'Topic :: System :: Systems Administration',
    ],
)
