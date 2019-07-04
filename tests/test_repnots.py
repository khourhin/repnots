#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `repnots` package."""

import pytest
import papermill as pm
import scrapbook as sb
import subprocess

from repnots import repnots

# From https://github.com/diana-hep/pyhf/blob/master/tests/test_notebooks.py
@pytest.fixture()
def common_kwargs(tmpdir):
    outputnb = tmpdir.join("output.ipynb")
    return {"output_path": str(outputnb)}


def test_init_repnots(tmpdir):
    """ Launch complete init_repnots script
    """
    subprocess.run(["init_repnots", "-o", tmpdir])


def test_notebook(common_kwargs):
    """ Test a specific notebook using scrapbook
    """
    pm.execute_notebook(
        "repnots/scripts/notebook_templates/workflow.ipynb", **common_kwargs
    )

    nb = sb.read_notebook(common_kwargs["output_path"])

    assert nb.scraps["results"].data == 2
