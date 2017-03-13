from typing import List

from .Reference import Reference
from ..constant_types import GenderType
from ..constant_types import NERType
from ..constant_types import QuantityType
from ..language import Token


class NameReference(Reference):
    def __init__(self, sentence_index: int, tokens: List[Token], entity_type: NERType,
                 gender: GenderType, quantity: QuantityType):
        super().__init__(sentence_index, tokens)

        self.__entity_type = entity_type
        if entity_type == NERType.PERSON:
            self.__gender = gender
        else:
            self.__gender = GenderType.NEUTRAL
        self.__quantity = quantity

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
        return "{self.sentence_index} : {self.tokens} {self.entity_type} {self.gender} " \
               "{self.quantity}\n".format(self=self)

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return (self.tokens == other.tokens) \
                   and (self.entity_type == other.entity_type) \
                   and (self.sentence_index == other.sentence_index) \
                   and (self.word_position == other.word_position)
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.__str__())
