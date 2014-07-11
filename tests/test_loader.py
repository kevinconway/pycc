import os

import pytest

from pycc import loader


@pytest.fixture
def current_dir():

    return os.path.split(os.path.realpath(__file__))[0]


@pytest.fixture
def pycc_dir(current_dir):

    return os.path.realpath(os.path.join(current_dir, '../pycc'))


def test_module_loader_fail(pycc_dir):

    with pytest.raises(ValueError):

        loader.ModuleLoader(os.path.join(pycc_dir, 'notreal.txt'))


def test_module_loader_pass(pycc_dir):

    loader.ModuleLoader(os.path.join(pycc_dir, 'loader.py'))


def test_module_loader_load(pycc_dir):

    mloader = loader.ModuleLoader(os.path.join(pycc_dir, 'loader.py'))

    mod = mloader.load()

    assert mod.location == mloader.path


def test_package_loader_fail(current_dir):

    with pytest.raises(ValueError):

        loader.PackageLoader(current_dir)


def test_package_loader_pass(pycc_dir):

    loader.PackageLoader(pycc_dir)


def test_package_loader_load(pycc_dir):

    ploader = loader.PackageLoader(pycc_dir)

    pkg = ploader.load()

    result = pkg.get('pycc.asttools.references')
    assert result.module.location == os.path.join(
        pycc_dir,
        'asttools/references.py',
    )
