import logging
import unittest

import os

from pycobalt import resolve, substitute

logging.getLogger('requests').setLevel(logging.WARNING)


class TestResolverForBarackObama(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_resolver_for_first_paragraphs(self):
        with open(os.path.join('examples', 'short_input.txt')) as i:
            sentences = [l for l in i]

        self.assertIsNotNone(sentences)
        self.assertEquals(25, len(sentences))

        text = "\n".join(sentences)

        sentences, substitutions = resolve(text, "")
        substituted = substitute(sentences, substitutions)

        with open(os.path.join('examples', 'short_expected.txt')) as i:
            expected = [l.strip() for l in i]

        substituted = [s.strip() for s in substituted]

        self.assertEquals(len(substituted), len(expected))

        for s, e in zip(substituted, expected):
            self.assertEquals(s, e)

    def test_resolver_for_full_article(self):
        with open(os.path.join('examples', 'Barack_Obama.input.txt')) as i:
            sentences = [l for l in i]

        self.assertIsNotNone(sentences)
        self.assertEquals(403, len(sentences))

        text = "\n".join(sentences)

        sentences, substitutions = resolve(text, "")
        substituted = substitute(sentences, substitutions)

        with open(os.path.join('examples', 'Barack_Obama.expected.txt')) as i:
            expected = [l.strip() for l in i]

        substituted = [s.strip() for s in substituted]

        self.assertEquals(len(substituted), len(expected))

        for s, e in zip(substituted, expected):
            self.assertEquals(s, e)


if __name__ == '__main__':
    unittest.main()
