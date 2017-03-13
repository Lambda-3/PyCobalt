from typing import List

from .Reference import Reference
from ..language import Token


class NominalReference(Reference):
    def __init__(self, sentence_index: int, tokens: List[Token]):
        super().__init__(sentence_index, tokens)

    def __str__(self):
        return "{}: '{}'".format(self.sentence_index, ', '.join(str(t) for t in self.tokens))

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.__tokens == other.__tokens) and (self.sentence_index == other.sentence_index)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        return hash(self.__str__())
