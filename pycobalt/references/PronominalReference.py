# -*- coding: utf-8 -*-
from typing import List

from .Reference import Reference
from ..constant_types import GenderType
from ..constant_types import NERType
from ..constant_types import PronounType
from ..constant_types import QuantityType
from ..language import Token


class PronominalReference(Reference):
    def __init__(self, sentence_index: int, tokens: List[Token],
                 gender: GenderType = GenderType.NONE,
                 quantity: QuantityType = QuantityType.NONE, pronoun_type: PronounType = PronounType.NONE,
                 entity_type: NERType = NERType.NONE):
        super().__init__(sentence_index, tokens)
        self.__gender = gender
        self.__quantity = quantity
        self.__pronoun_type = pronoun_type
        self.__entity_type = entity_type

    @property
    def entity_type(self) -> NERType:
        return self.__entity_type

    @property
    def gender(self) -> GenderType:
        return self.__gender

    @property
    def quantity(self) -> QuantityType:
        return self.__quantity

    def __str__(self):
        return "{self.sentence_index}: " \
               "{self.tokens} {self.gender} {self.entity_type} {self.quantity}".format(self=self)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.tokens == other.tokens) \
                   and (self.sentence_index == other.sentence_index)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        return hash(self.__str__())
