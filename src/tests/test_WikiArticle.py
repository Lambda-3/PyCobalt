import logging
import os
import sys
import unittest

from nltk import sent_tokenize

logging.getLogger('requests').setLevel(logging.WARNING)

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from Resolver import Resolver


# noinspection PyProtectedMember
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
