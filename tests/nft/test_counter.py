import ape
import pytest


def test_initialCount(token):
    count = token.totalSupply()
    assert count == 0


def test_increment(minted):
    assert minted.totalSupply() == 1


def test_nonzero_owner_index(token):
    with ape.reverts():
        token.tokenOfOwnerByIndex("0x0" + "0" * 39, 0)