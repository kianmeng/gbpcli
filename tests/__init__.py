"""Tests for the Gentoo Build Publisher CLI"""
import datetime
import io
import sys
import unittest
from functools import partial
from json import dumps as stringify
from json import loads as parse
from pathlib import Path
from unittest import mock

import requests

from gbpcli import GBP

DATA_DIR = Path(__file__).resolve().parent / "data"
LOCAL_TIMEZONE = datetime.timezone(datetime.timedelta(days=-1, seconds=61200), "PDT")
NO_JSON = object()


class TestCase(unittest.TestCase):
    """Custom test case for gbpcli"""

    def setUp(self):
        super().setUp()

        self.gbp = make_gbp()

    def make_response(self, data):
        """Add 200 json response to mock post

        This is like make_response() below except it assumes all responses are 200
        responses and all content is JSON. Additionally it can be called more than once
        and adds responses for subsequent calls. If called with `None` as an argument,
        then any previously configured responses are cleared
        """
        if data is None:
            self.gbp.session.post.side_effect = None
            return

        if isinstance(data, str):
            mock_json = parse(load_data(data))
        else:
            mock_json = data

        if not self.gbp.session.post.side_effect:
            self.gbp.session.post.side_effect = (make_response(json=mock_json),)
        else:
            self.gbp.session.post.side_effect = (
                *self.gbp.session.post.side_effect,
                make_response(json=mock_json),
            )

    def assert_graphql(self, query: str, index=0, **variables):
        """Assert that self.gbp made a the given graphql query"""
        calls = self.gbp.session.post.call_args_list

        try:
            call = calls[index]
        except IndexError:
            self.fail("Query not called")

        assert call[0] == (self.gbp.url,)

        json = {"query": query, "variables": None}
        expected = {"json": json, "headers": self.gbp.headers}

        if variables:
            json["variables"] = variables

        self.assertEqual(call[1], expected)


def load_data(filename: str) -> bytes:
    """Read and return content from filename in the data directory"""
    return (DATA_DIR / filename).read_bytes()


def make_response(status_code=200, json=NO_JSON, content=None) -> mock.Mock:
    """Create a mock requests.Response object"""
    if content is None:
        content = b"test"
        text = "test"
    else:
        text = None

    attrs = {
        "content": content,
        "headers": {},
        "status_code": status_code,
        "text": text,
    }

    if json is not NO_JSON:
        attrs["json.return_value"] = json
        attrs["content"] = stringify(json, sort_keys=True).encode("utf-8")
        attrs["headers"] = {"content-type": "application/json"}

    response_mock = mock.Mock(spec=requests.Response)
    response_mock.configure_mock(**attrs)

    return response_mock


def make_gbp(url: str = "http://test.invalid/") -> GBP:
    """Return a GBP instance with a mock session attribute"""
    gbp = GBP(url)
    gbp.session = mock.Mock()

    return gbp


class MockPrint:  # pylint: disable=too-few-public-methods
    """mockable print() so that output goes to StringIO"""

    def __init__(self):
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self.file = io.StringIO()

    def __call__(self, value, file=sys.stdout):
        """Mocked print() function"""
        if file is sys.stdout:
            file = self.stdout
        elif file is sys.stderr:
            file = self.stderr
        else:
            file = self.file

        print(value, file=file)


def mock_print(where, *args, **kwargs):
    """Mocks the print function but keeps the output"""
    return mock.patch(
        f"{where}.print",
        *args,
        new_callable=MockPrint,
        **kwargs,
    )
