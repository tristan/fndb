 
from distutils.core import setup

setup(
    name='FakeNDB',
    version='0.1.0',
    author='Tristan King',
    author_email='tristan.king@gmail.com',
    packages=['fndb', 'fndb.test'],
    url='http://github.com/tristan/fndb',
    description='Data Modeling and Querying based off the NDB libraries available on the Google AppEngine.',
    long_description=open('README.md').read(),
    install_requires=[
    ],
    extra_require = {
        'simplekv_store': ['simplekv']
    }
)
