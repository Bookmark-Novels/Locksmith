from setuptools import setup

setup(
    name='locksmith',
    description='Python module for fetching secrets for Bookmark services.',
    author='Bookmark Novels',
    version='1.0.1',
    packages=['locksmith'],
    url='https://github.com/Bookmark-Novels/Locksmith',
    license='MIT',
    install_requires=[
        'hvac'
    ]
)
