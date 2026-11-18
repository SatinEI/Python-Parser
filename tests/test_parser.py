from pathlib import Path
import unittest
from unittest.mock import Mock, patch

import requests

from src.database import DatabaseRepository
from src.parser import ForumParser


class TestForumParser(unittest.TestCase):
    def setUp(self):
        self.html = (Path(__file__).parent / 'fixtures' / 'forum.html').read_text(encoding='utf-8')
        self.response = Mock(text=self.html)
        request_patch = patch('src.parser.requests.get', return_value=self.response)
        self.request = request_patch.start()
        self.addCleanup(request_patch.stop)
        self.parser = ForumParser()

    def test_parse_page(self):
        comments = self.parser.parse_page('https://example.com/topic')
        self.assertEqual(comments, [
            {'id': 101, 'user': 'alice', 'text': 'Привет, <b>мир</b>!'},
            {'id': 102, 'user': 'bob', 'text': 'Второй комментарий'},
        ])

    def test_page_without_comments(self):
        self.response.text = (Path(__file__).parent / 'fixtures' / 'empty.html').read_text(encoding='utf-8')
        self.assertEqual(self.parser.parse_page('https://example.com/topic'), [])

    def test_request_headers_and_timeout(self):
        self.response.text = '<table class="comment-tree"></table>'
        self.parser.parse_page('https://example.com/topic')
        self.assertTrue(self.request.call_args.kwargs['headers']['User-Agent'])
        self.assertGreater(self.request.call_args.kwargs['timeout'], 0)

    def test_http_error(self):
        self.response.raise_for_status.side_effect = requests.HTTPError('404')
        with self.assertRaises(requests.HTTPError):
            self.parser.parse_page('https://example.com/topic')

    def test_save_to_db(self):
        repository = DatabaseRepository(':memory:')
        self.addCleanup(repository.connection.close)
        comments = self.parser.parse_page('https://example.com/topic')
        self.parser.save_to_db(comments, repository)
        self.assertEqual(repository.get_by_id(101), {
            'id': 101, 'name': 'alice', 'message': 'Привет, <b>мир</b>!',
        })
        self.assertEqual(len(repository.get_by_name('bob')), 1)


if __name__ == '__main__':
    unittest.main()
