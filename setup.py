from setuptools import setup, setuptools

setup(
    name='dpdutils',
    url='https://github.com/BayAreaMetro/dpdutils',
    author='BayAreaMetro',
    author_email='ehuang@bayareametro.gov',
    packages=setuptools.find_packages(),
    install_requires=['pandas', 'requests', 'xlrd'],
    version='0.1.0',
    license='MIT',
    description='A collection of utilities to support the work of the Design and Project Delivery section at MTC.',
    long_description=open('README.MD').read(),
    long_description_content_type="text/markdown"
)
