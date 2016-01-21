#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import os.path
import warnings
import sys
import shutil, errno
import subprocess

try:
    import PyQt5
except Exception as e:
    subprocess.Popen( 'sudo apt-get -y install python3-pyqt5',
                   shell=True,
                   stdin=subprocess.PIPE ).communicate()

def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise

try:
    from setuptools import setup
    setuptools_available = True
except ImportError:
    from distutils.core import setup
    setuptools_available = False

try:
    # This will create an exe that needs Microsoft Visual C++ 2008
    # Redistributable Package
    import py3exe
except ImportError:
    if len(sys.argv) >= 2 and sys.argv[1] == 'py3exe':
        print("Cannot import py3exe", file=sys.stderr)
        exit(1)

py3exe_options = {
    "bundle_files": 1,
    "compressed": 1,
    "optimize": 2,
    "dist_dir": '.',
    "dll_excludes": ['w9xpopen.exe', 'crypt32.dll'],
}

py3exe_console = [{
    "script": "./pt-video-downloader.py",
    "dest_base": "pt-video-downloader",
}]

py3exe_params = {
    'console': py3exe_console,
    'options': {"py3exe": py3exe_options},
    'zipfile': None
}

if len(sys.argv) >= 2 and sys.argv[1] == 'py3exe':
    params = py3exe_params
else:
    files_spec = [
        ('etc/bash_completion.d', ['pt-video-downloader.bash-completion']),
        ('share/doc/pt-video-downloader', ['README.txt']),
    ]
    root = os.path.dirname(os.path.abspath(__file__))
    data_files = []
    for dirname, files in files_spec:
        resfiles = []
        for fn in files:
            if not os.path.exists(fn):
                warnings.warn('Skipping file %s since it is not present. Type  make  to build all automatically generated files.' % fn)
            else:
                resfiles.append(fn)
        data_files.append((dirname, resfiles))
    copyanything("app_data", str(os.environ['HOME']) + "/pt_video_downloader/app_data")
    params = {}

setup(
    name='pt-video-downloader',
    version='0.1',
    description='PT Video Downloader',
    long_description='Small gui program to download videos from'
    ' YouTube.com and other video sites with youtube-dl.',
    url='http://pythonturkiye.com/pt-video-downloader',
    author='Python Turkiye',
    author_email='info@pythonturkiye.com',
    scripts=['pt-video-downloader'],
    packages=[
        'app_code'
    ],
    install_requires=[
        'pyquery',
        'youtube_dl'
    ],

    # Provokes warning on most systems (why?!)
    # test_suite = 'nose.collector',
    # test_requires = ['nosetest'],

    classifiers=[
        "Topic :: Multimedia :: Video",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: Public Domain",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],

    **params
)
