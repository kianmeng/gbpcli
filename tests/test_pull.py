"""Tests for the pull subcommand"""
# pylint: disable=missing-function-docstring
from argparse import Namespace
from unittest import mock

from gbpcli import queries
from gbpcli.subcommands.pull import handler as pull

from . import LOCAL_TIMEZONE, MockConsole, TestCase


@mock.patch("gbpcli.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class PullTestCase(TestCase):
    """pull() tests"""

    def test(self):
        args = Namespace(machine="lighthouse", number=3226)
        self.make_response("pull.json")

        pull(args, self.gbp, MockConsole())

        self.assert_graphql(queries.pull, id="lighthouse.3226")
