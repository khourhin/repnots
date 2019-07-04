#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `repnots` package."""

import pytest
import papermill as pm
import subprocess

from repnots import repnots


# @pytest.fixture(scope="module")
# def setup(tmpdir):2


def test_init_repnots(tmpdir):

    subprocess.run(["init_repnots", "-o", tmpdir])
