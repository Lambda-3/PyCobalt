import logging
import unittest
import nose

from pycobalt.constant_types import NERType, POSType
from pycobalt.language import Sentence, Token
from pycobalt.language.stanford_tools import _clean_text, annotate_text

logging.getLogger('requests').setLevel(logging.WARNING)


class TestStanfordTools(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_cleaning_text_with_very_simple_sentence(self):
        input_text = "Donald Trump is the president of USA. He is a business man."

        output_text = _clean_text(input_text)

        self.assertEquals(
            input_text,
            output_text
        )

    def test_cleaning_text_with_actual_cleaning_needed(self):
        input_text = "Barack Hussein Obama II (US Listeni/bəˈrɑːk huːˈseɪn oʊˈbɑːmə/ bə-RAHK hoo-SAYN oh-BAH-mə;[1][" \
                     "2] born August 4, 1961) is an American politician who served as the 44th President of the " \
                     "United States from 2009 to 2017. He is the first African American to have served as president, " \
                     "as well as the first born outside the contiguous United States. He previously served in the " \
                     "U.S. Senate representing Illinois from 2005 to 2008, and in the Illinois State Senate from 1997 " \
                     "to 2004. "

        expected = "Barack Hussein Obama II (US Listeni/bəˈrɑːk huːˈseɪn oʊˈbɑːmə/ bə-RAHK hoo-SAYN oh-BAH-mə; born " \
                   "August 4, 1961) is an American politician who served as the 44th President of the United States " \
                   "from 2009 to 2017. He is the first African American to have served as president, as well as the " \
                   "first born outside the contiguous United States. He previously served in the U.S. Senate " \
                   "representing Illinois from 2005 to 2008, and in the Illinois State Senate from 1997 to 2004."

        output_text = _clean_text(input_text)

        self.assertEquals(
            expected,
            output_text
        )

    def test_convert_sentence_to_internal_sentence(self):
        input_text = "Donald Trump is the president."
        expected = [
            Sentence(
                0,
                "Donald Trump is the president.",
                tokens=[
                    Token(0, "Donald", "Donald", POSType.OTHER, NERType.PERSON),
                    Token(1, "Trump", "Trump", POSType.OTHER, NERType.PERSON),
                    Token(2, "is", "is", POSType.OTHER, NERType.OTHER),
                    Token(3, "the", "the", POSType.OTHER, NERType.OTHER),
                    Token(4, "president", "president", POSType.NN, NERType.OTHER),
                    Token(5, ".", ".", POSType.OTHER, NERType.OTHER),
                ]
            )
        ]

        actual = annotate_text(input_text)

        self.assertListEqual(expected, actual)


if __name__ == '__main__':
    nose.main()