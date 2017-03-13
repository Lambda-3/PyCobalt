# -*- coding: utf-8 -*-
from typing import List

from pycobalt.language import Token
from .Reference import Reference


class Substitution(object):
    def __init__(self, sentence_index: int, original: List[Token], reference: Reference):
        self.__sentence_index = sentence_index
        self.__original = original
        self.__reference = reference

    @property
    def sentence_index(self) -> int:
        return self.__sentence_index

    @property
    def original(self) -> List[Token]:
        return self.__original

    @property
    def reference(self) -> Reference:
        return self.__reference

    @sentence_index.setter
    def sentence_index(self, sentence_index: int) -> None:
        self.__sentence_index = sentence_index

    @original.setter
    def original(self, original: List[Token]) -> None:
        self.__original = original

    @reference.setter
    def reference(self, reference: List[Token]) -> None:
        self.__reference = reference

    def __str__(self) -> str:
        return "{self.sentence_index} '{original}' -> '{reference}'".format(
            self=self,
            original=" ".join(t.word for t in self.original),
            reference=" ".join(t.word for t in self.reference.tokens))
