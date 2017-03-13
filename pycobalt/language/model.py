from typing import List

from ..constant_types import POSType, NERType


class Token(object):
    def __init__(self, index: int, word: str, original_word: str, pos: POSType, ner: NERType):
        self.__index = index
        self.__word = word
        self.__original_word = original_word
        self.__pos = pos
        self.__ner = ner

        self.__lower = word.lower()

    @property
    def index(self) -> int:
        return self.__index

    @property
    def word(self) -> str:
        return self.__word

    @property
    def original_word(self) -> str:
        return self.__original_word

    @property
    def lower(self) -> str:
        return self.__lower

    @property
    def pos(self) -> POSType:
        return self.__pos

    @property
    def ner(self) -> NERType:
        return self.__ner

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    def __str__(self):
        return "{self.index}: {self.word} {self.pos} {self.ner}".format(self=self)

    def __repr__(self):
        return self.__str__()


class Sentence(object):
    def __init__(self, index: int, text: str, tokens: List[Token]):
        self.__index = index
        self.__text = text
        self.__tokens = tokens

    @property
    def index(self) -> int:
        return self.__index

    @property
    def text(self) -> str:
        return self.__text

    @property
    def tokens(self) -> List[Token]:
        return self.__tokens

    @text.setter
    def text(self, text):
        self.__text = text

    def __str__(self) -> str:
        return "{self.index}: {self.text}".format(self=self)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.index == other.index \
                   and self.text == other.text \
                   and len(self.tokens) == len(other.tokens) \
                   and all(st == ot for st, ot in zip(self.tokens, other.tokens))
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
