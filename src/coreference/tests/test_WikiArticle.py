import logging
import unittest

import os
from nltk import sent_tokenize

from ..Resolver import Resolver

logging.getLogger('requests').setLevel(logging.WARNING)


class TestResolverForBarackObama(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_resolver_for_first_paragraphs(self):
        with open(os.path.join('examples', 'original.txt')) as i:
            sentences = [l for l in i]

        self.assertIsNotNone(sentences)
        self.assertEquals(25, len(sentences))

        text = "\n".join(sentences)

        substitutions = Resolver.resolve(text, "")
        substituted = Resolver.substitute_in_text(text, substitutions)

        with open(os.path.join('examples', 'expected.txt')) as i:
            expected = [l.strip() for l in i]

        substituted = [s.strip() for s in sent_tokenize(substituted)]

        self.assertEquals(len(substituted), len(expected))

        for s, e in zip(substituted, expected):
            self.assertEquals(s, e)


if __name__ == '__main__':
    unittest.main()
