import os
from setuptools import find_packages, setup
import lkf_models

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


import datetime, base64, json, urllib2, \
       subprocess ,sys, simplejson, hashlib, time

from urllib2 import Request, urlopen, HTTPError
INSTALL_REQUIREMENTS = [
    'datetime',
    'base64',
    'json',
    'urllib2',
    'subprocess',
    'sys',
    'simplejson',
    'hashlib',
    'time'
]

setup(
    name='backblaze_utils',
    version=lkf_models.__version__,
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',  # example license
    description='Backblze Utils',
    long_description=README,
    url='https://app.linkaform.com/',
    author='LikaForm',
    author_email='develop@linkaform.com',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
     install_requires=INSTALL_REQUIREMENTS,
)