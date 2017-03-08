from ..constant_types import EntityType
from ..constant_types import GenderType
from ..constant_types import QuantityType


class NameReference(object):
    def __init__(self,
                 term: str,
                 entity_type: EntityType,
                 gender: GenderType,
                 quantity: QuantityType,
                 sentence_index: int,
                 word_position: int):
        self.term = term
        self.entity_type = entity_type
        if entity_type == EntityType.PERSON:
            self.gender = gender
        else:
            self.gender = GenderType.NEUTRAL
        self.quantity = quantity
        self.sentence_index = sentence_index
        self.word_position = word_position
        self.resolved_term = term

    def get_sentence_index(self):
        return self.sentence_index

    def __str__(self):
        return "{self.term} {self.entity_type} {self.gender} {self.quantity} " \
               "{self.sentence_index} {self.word_position}\n".format(self=self)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.term == other.term) \
               and (self.entity_type == other.entity_type) \
               and (self.sentence_index == other.sentence_index) \
               and (self.word_position == other.word_position)

    def __hash__(self):
        return hash(self.term + str(self.entity_type) + str(self.sentence_index))
