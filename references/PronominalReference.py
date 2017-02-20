# -*- coding: utf-8 -*-


# noinspection PyPep8Naming
class PronominalReference(object):
    def __init__(self, pronoun: str = '', gender: str = '', number: str = '', pronounType: str = '',
                 entityType: str = '', sentence: int = -1, position: int = -1):
        self.pronoun = pronoun
        self.gender = gender
        self.number = number
        self.pronounType = pronounType
        self.entityType = entityType
        self.sentence = sentence
        self.position = position

    def __str__(self):
        return "{self.pronoun} {self.gender} {self.number} {self.sentence} {self.position}".format(self=self)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.pronoun == other.term) \
               and (self.sentence == other.sentence) \
               and (self.position == other.position)

    def __hash__(self):
        return hash(self.pronoun + ' ' + str(self.sentence) + ' ' + str(self.position))
