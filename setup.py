import os
from setuptools import setup, find_packages

f = open(os.path.join('src', 'wicked', 'version.txt'))
VERSION = f.read().strip()
f.close()

PACKAGE_DATA = {
    'wicked': ['*.zcml',
               '*.txt',
               'lib/*.zcml',
               'conf/*',
               'browser/*.zcml',
               'skins/wicked/*'],
}

setup(
    name = 'wicked',
    version = VERSION,
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    package_data = PACKAGE_DATA,
    zip_safe = False,
    entry_points = {'zope2.initialize':
                    ['initialize=wicked:initialize']},
    )

