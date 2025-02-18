"""Tests for the pull subcommand"""
# pylint: disable=missing-function-docstring,protected-access
from argparse import Namespace
from unittest import mock

from gbpcli.subcommands.pull import handler as pull

from . import LOCAL_TIMEZONE, TestCase


@mock.patch("gbpcli.render.LOCAL_TIMEZONE", new=LOCAL_TIMEZONE)
class PullTestCase(TestCase):
    """pull() tests"""

    def test(self):
        args = Namespace(machine="lighthouse", number="3226")
        self.make_response("pull.json")

        pull(args, self.gbp, self.console)

        self.assert_graphql(self.gbp.query.pull, id="lighthouse.3226")
