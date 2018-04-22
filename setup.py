#!/usr/bin/env python
from setuptools import setup, find_packages

from kaggle_cli.meta import VERSION


PROJECT = 'kaggle-cli'


long_description = \
    'https://github.com/floydwch/kaggle-cli/blob/master/README.md'

setup(
    name=PROJECT,
    version=VERSION,

    description='An unofficial Kaggle command line tool.',
    long_description=long_description,

    author='floydwch',
    author_email='floydwch@gmail.com',

    url='https://github.com/floydwch/kaggle-cli',
    download_url='https://github.com/floydwch/kaggle-cli/tarball/master',

    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Intended Audience :: Developers',
                 'Environment :: Console',
                 ],

    platforms=['Any'],

    scripts=[],

    provides=[],
    install_requires=[
        'cliff>=2.8.0,<2.9',
        'MechanicalSoup>=0.7.0,<0.9',
        'lxml>=4.0.0,<=4.2.1',
        'cssselect>=1.0.1,<1.1',
        'configparser',
        'progressbar2>=3.34.3,<3.35',
        'beautifulsoup4>=4.6.0,<4.7'
    ],

    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'kg = kaggle_cli.main:main'
        ],
        'kaggle_cli': [
            'submit = kaggle_cli.submit:Submit',
            'config = kaggle_cli.config:Config',
            'download = kaggle_cli.download:Download',
            'dataset = kaggle_cli.download:Dataset',
            'submissions = kaggle_cli.submissions:Submissions'
        ],
    },

    zip_safe=False,
)
