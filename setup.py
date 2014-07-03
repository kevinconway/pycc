from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='pycc',
    version='0.0.1',
    url='https://github.com/kevinconway/pycc',
    license=license,
    description='Python code optimizer..',
    author='Kevin Conway',
    author_email='kevinjacobconway@gmail.com',
    long_description=readme,
    classifiers=[],
    packages=find_packages(exclude=['tests', 'build', 'dist', 'docs']),
    requires=['astkit', 'pytest'],
    entry_points={
        'console_scripts': [
            'pycc-transform = pycc.cli.transform:main',
            'pycc-compile = pycc.cli.compile:main',
        ],
    },
)
