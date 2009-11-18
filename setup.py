from setuptools import setup, find_packages
import sys, os

version = '1.1.8alpha1'

setup(name='wicked',
      version=version,
      description="wicked is a compact syntax for doing wiki-like content linking and creation in zope and plone",
      long_description="""\
""",
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='wiki anti-wiki zope3 zope2 plone',
      author='whit',
      author_email='wicked@lists.openplans.org',
      url='http://openplans.org/projects/wicked',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['wicked'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [wicked.base_registration]
      basic_plone_registration = wicked.registration:BasePloneWickedRegistration
      bracketted_plone_registration = wicked.registration:BasePloneMediaWickedRegistration
      #[wicked.cache_manager]
      """,
      )
