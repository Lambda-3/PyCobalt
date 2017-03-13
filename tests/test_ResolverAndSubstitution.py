import logging
import unittest

import nose

from pycobalt import resolve, substitute

logging.getLogger('requests').setLevel(logging.WARNING)


class TestResolverAndSubstitution(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_simple_sentence(self):
        input_text = "Donald Trump is the president of USA. He is a business man."

        expected = ["Donald Trump is the president of USA.", "Donald Trump is a business man."]

        substituted = substitute(*resolve(input_text))

        self.assertEqual(
            expected,
            substituted
        )


if __name__ == '__main__':
    nose.main()
