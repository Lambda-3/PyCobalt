import logging
import unittest
import nose

import os

from pycobalt import resolve, substitute

logging.getLogger('requests').setLevel(logging.WARNING)


class TestResolverWithActualData(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_resolver_for_first_paragraphs_BarackObama(self):
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

    def test_resolver_for_article_BarackObama(self):
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

    def test_resolver_for_full_article_Paris(self):
        with open(os.path.join('examples', 'Paris.input.txt')) as i:
            text = i.read()

        self.assertIsNotNone(text)

        sentences, substitutions = resolve(text, "")

        self.assertIsNotNone(sentences)
        self.assertEquals(len(sentences), 657)
        self.assertIsNotNone(substitutions)
        self.assertGreater(len(substitutions), 100)


if __name__ == '__main__':
    nose.main()
