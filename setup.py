# -*- coding: utf-8 -*-
import os
import sys
import pytest

from setuptools import setup
from setuptools.command.test import test as TestCommand

f = open(os.path.join(os.path.dirname(__file__), 'version.txt'))
version = f.read().strip()
f.close()


class SetupTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name="ssdb-py",
    version=version,
    description="ssdb python client",
    auth="qianwenpin",
    auth_email="pyloque@gmail.com",
    license="MIT",
    packages=['ssdb'],
    keywords=['ssdb'],
    cmdclass={'test': SetupTest})
