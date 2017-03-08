# -*- coding: utf-8 -*-

from ..constant_types import EntityType
from ..constant_types import GenderType
from ..constant_types import PronounType
from ..constant_types import QuantityType


class PronominalReference(object):
    def __init__(self,
                 pronoun: str = '',
                 gender: GenderType = GenderType.NONE,
                 quantity: QuantityType = QuantityType.NONE,
                 pronoun_type: PronounType = PronounType.NONE,
                 entity_type: EntityType = EntityType.NONE,
                 sentence_index: int = -1,
                 word_position: int = -1):
        self.pronoun = pronoun
        self.gender = gender
        self.quantity = quantity
        self.pronoun_type = pronoun_type
        self.entity_type = entity_type
        self.sentence_index = sentence_index
        self.word_position = word_position

    def __str__(self):
        return "{self.pronoun} {self.gender} {self.quantity} {self.sentence_index} {self.word_position}".format(
            self=self)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.pronoun == other.pronoun) \
               and (self.sentence_index == other.sentence_index) \
               and (self.word_position == other.word_position)

    def __hash__(self):
        return hash(self.pronoun + ' ' + str(self.sentence_index) + ' ' + str(self.word_position))
