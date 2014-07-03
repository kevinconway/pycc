import os

import pytest

from pycc import module


@pytest.fixture
def current_dir():

    return os.path.split(os.path.realpath(__file__))[0]


@pytest.fixture
def pycc_dir(current_dir):

    return os.path.realpath(os.path.join(current_dir, '../pycc'))


@pytest.fixture
def pkg(pycc_dir):

    return module.Package(location=pycc_dir)


def test_path_from_location_init(pkg):

    assert pkg._path_from_location(
        os.path.join(pkg.location, '__init__.py')
    ) == '/pycc'


def test_path_from_location_module(pkg):

    assert pkg._path_from_location(
        os.path.join(pkg.location, 'loader.py')
    ) == '/pycc/loader'


def test_add_init(pkg):

    location = os.path.join(pkg.location, '__init__.py')
    pkg.add(location, node=None)
    result = pkg.get(pkg._path_from_location(location))
    assert result.module.location == location


def test_add_module(pkg):

    location = os.path.join(pkg.location, 'loader.py')
    pkg.add(location, node=None)
    result = pkg.get(pkg._path_from_location(location))
    assert result.module.location == location


def test_get_with_target(pkg):

    location = os.path.join(pkg.location, 'loader.py')
    pkg.add(location, node=None)
    result = pkg.get('pycc.loader.ModuleLoader')
    assert result.module.location == location
    assert result.target == 'ModuleLoader'


def test_modules_iter(pkg):

    location = os.path.join(pkg.location, 'loader.py')
    pkg.add(location, node=None)

    modules = pkg.modules()
    assert hasattr(modules, '__iter__')
    assert location in (m.location for m in modules)
