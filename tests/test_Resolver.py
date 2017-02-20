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
class TestResolverMethod(unittest.TestCase):
    def test_clean_text(self):
        input_text = sent_tokenize(
            """I have multiple sentences for [123] years.
            Probably this is a clean sentence."""
        )

        cleaned_text = Resolver._cleanText(input_text)

        expected_output = sent_tokenize(
            """I have multiple sentences for  years.
            Probably this is a clean sentence."""
        )

        self.assertEqual(cleaned_text, expected_output)

    def test_simple_sentence(self):
        input_text = "Donald Trump is the president of USA. He is a business man."

        substituted, _ = Resolver.substituteInText(
            input_text, Resolver.resolve(input_text, ''))

        self.assertEqual(
            substituted,
            "Donald Trump is the president of USA. Donald Trump is a business man."
        )

    def test_simple_sentence_2(self):
        input_text = "Donald Trump is the president of USA. He is a business man."

        substituted, _ = Resolver.substituteInText(
            input_text, Resolver.resolve(input_text, ''))

        self.assertEqual(
            substituted,
            "Donald Trump is the president of USA. Donald Trump is a business man."
        )


if __name__ == '__main__':
    unittest.main()
