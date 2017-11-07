#!/usr/bin/env python

import codecs
import os.path
from setuptools import setup, find_packages


def long_description():
    project_root = os.path.abspath(os.path.dirname(__file__))
    readme_filename = os.path.join(project_root, 'README.rst')
    with codecs.open(readme_filename, encoding='UTF-8') as readme_file:
        lines = [line.rstrip('\n') for line in readme_file]
    lines = lines[4:]
    return "\n".join(lines)


setup(
    name='Fabrix',
    version='0.2.3',
    description='Fabrix is Fabric extension for configuration management',
    long_description=long_description(),
    long_description_content_type='text/x-rst',
    keywords=['configuration management'],
    author='Gena Makhomed',
    author_email='makhomed@gmail.com',
    url='https://github.com/makhomed/fabrix',
    license='GPLv3',
    platforms=['Linux'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=['Fabric>=1.12,<2.0', 'PyYAML>=3.10', 'Jinja2>=2.7.2'],
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
