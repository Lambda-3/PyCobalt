from typing import List

from ..language import Token


class Reference(object):
    def __init__(self, sentence_index: int, tokens: List[Token]):
        self.__sentence_index = sentence_index
        self.__tokens = tokens

    @property
    def sentence_index(self):
        return self.__sentence_index

    @property
    def tokens(self):
        return self.__tokens
