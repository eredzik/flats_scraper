
import os

from setuptools import setup, find_packages

# Meta information
version = open('VERSION').read().strip()
dirname = os.path.dirname(__file__)

# Save version and author to __meta__.py
path = os.path.join(dirname, 'src', 'flats_scraper', '__meta__.py')
data = '''# Automatically created. Please do not edit.
__version__ = u'%s'
__author__ = u'Emil Redzik'
''' % version
with open(path, 'wb') as F:
    F.write(data.encode())
    

setup(
    # Basic info
    name='flats_scraper',
    version=version,
    author='Emil Redzik',
    author_email='emilredzik1994@gmail.com',
    url='https://github.com/eredzik/flats_scraper',
    description='Creates the skeleton of your Python project.',
    long_description=open('README.md').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],

    # Packages and depencies
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        'sqlalchemy',
        'alembic',
        'prefect',
    ],
)