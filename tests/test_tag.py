"""Tests for the tag subcommand"""
# pylint: disable=missing-docstring,protected-access
from argparse import Namespace

from gbpcli.subcommands.tag import handler as tag

from . import TestCase


class TagTestCase(TestCase):
    """tag() tests"""

    def test_tag(self):
        args = Namespace(machine="lighthouse", number="9400", tag="prod", remove=False)
        self.make_response("tag_build.json")

        status = tag(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assert_graphql(self.gbp.query.tag_build, id="lighthouse.9400", tag="prod")

    def test_untag(self):
        args = Namespace(machine="lighthouse", number=None, tag="prod", remove=True)
        self.make_response("untag_build.json")

        status = tag(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assert_graphql(
            self.gbp.query.untag_build, machine="lighthouse", tag="prod"
        )

    def test_untag_with_string_starting_with_tagsym_works(self):
        args = Namespace(machine="lighthouse", number=None, tag="@prod", remove=True)
        self.make_response("untag_build.json")

        status = tag(args, self.gbp, self.console)

        self.assertEqual(status, 0)
        self.assert_graphql(
            self.gbp.query.untag_build, machine="lighthouse", tag="prod"
        )

    def test_untag_with_build_number_gives_error(self):
        args = Namespace(machine="lighthouse", number="9400", tag="prod", remove=True)

        status = tag(args, self.gbp, self.console)

        self.assertEqual(status, 1)
        self.assertEqual(
            self.console.err.getvalue(), "When removing a tag, omit the build number\n"
        )
