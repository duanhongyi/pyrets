import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()


setup(name='pyrets',
      version='1.7.4',
      description='a python rets client',
      long_description=README,
      classifiers=[
        "Programming Language :: Python",
        ],
      author='duanhongyi',
      author_email='duanhyi@gmail.com',
      url='https://github.com/duanhongyi/pyrets',
      keywords='Python rets client',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=["xmltodict", "requests"],
      platforms = 'all platform',
      license = 'BSD',
      )