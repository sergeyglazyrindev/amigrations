import sys

# dirty hack, always use wheel
sys.argv.append('bdist_wheel')

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='amigrations',
    version='0.1',
    description='Ascetic database migrations. The most ease way to power your python app with raw database migrations',
    long_description=readme(),
    classifiers=[
        'Development Status :: 0.1 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Topic :: Database',
    ],
    url='https://github.com/sergeyglazyrindev/amigrations',
    author='Sergey Glazyrin',
    author_email='sergey.glazyrin.dev@gmail.com',
    license='MIT',
    package_dir={'': 'src'},
    packages=['amigrations', ],
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': ['nose', 'mock'],
    },
    test_suite='tests',
    install_requires=['mysqlclient==1.3.6', ]
)
