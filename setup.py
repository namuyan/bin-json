from setuptools import setup
import os


# version
here = os.path.dirname(os.path.abspath(__file__))
init_path = os.path.join(here, 'bjson', '__init__.py')
version = next((line.split('=')[1].strip().replace("'", '')
                for line in open(init_path)
                if line.startswith('__version__ = ')),
               '0.0.dev0')


setup(
    name='bjson',
    version=version,
    description='Alternative way to send Python3 object by binary.',
    author='namuyan',
    url='https://github.com/namuyan/bin-json',
    py_modules=['bjson'],
    license="MIT Licence",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],
)
