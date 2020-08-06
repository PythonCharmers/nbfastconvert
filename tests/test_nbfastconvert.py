#!/usr/bin/env python

"""Tests for `nbfastconvert` package."""

import difflib

import pytest


from nbfastconvert import nbfastconvert as nbf


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_patch_transform():
    
    a = list("qabxcd")
    b = list("abycdf")
    test_matcher = difflib.SequenceMatcher(a=a, b=b)
    opcodes = test_matcher.get_opcodes()
    result = nbf.patch_transform(
        opcodes,
        [str.upper(ai) for ai in a],
        b,
        str.upper,
        verify=True
    )
    b_upper = [str.upper(bi) for bi in b]
    assert b_upper == result
