from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open('requirements.txt') as f:
    requirements = f.readlines()

setup(
    name='pycc',
    version='2.0.0',
    url='https://github.com/kevinconway/pycc',
    license=license,
    description='Python code optimizer.',
    author='Kevin Conway',
    author_email='kevinjacobconway@gmail.com',
    long_description=readme,
    classifiers=[],
    packages=find_packages(exclude=['tests', 'build', 'dist', 'docs']),
    requires=requirements,
    entry_points={
        'console_scripts': [
            'pycc-transform = pycc.cli.transform:main',
            'pycc-compile = pycc.cli.compile:main',
        ],
        'pycc.optimizers': [
            'pycc_constant_inliner = pycc.cli.extensions.constants:ConstantInlineExtension',
        ],
    },
)
