import os
from setuptools import find_packages, setup
import backblaze_utils

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

INSTALL_REQUIREMENTS = [
    'simplejson',
    'Pillow'
]

setup(
    name='backblaze_utils',
    version=backblaze_utils.__version__,
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',  # example license
    description='Backblaze Utils',
    url='https://app.linkaform.com/',
    author='LinkaForm',
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
