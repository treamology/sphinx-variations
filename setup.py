import setuptools
from variations import __version__

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='sphinx-variations',
    version=__version__,
    author='D. Lawrence',
    author_email='trea@treamous.com',
    description='Create multiple variations of your Sphinx HTML documentation.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/treamology/sphinx-variations',
    packages=['variations'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Sphinx',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
    ],
    install_requires=[
       'sphinx'
    ],
)