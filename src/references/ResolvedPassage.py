# -*- coding: utf-8 -*-
from typing import Dict


# noinspection PyPep8Naming
class ResolvedPassage:
    def __init__(self, resolvedPassage: int, linkedEntities: Dict[str, str]):
        self.resolvedPassage = resolvedPassage
        self.linkedEntities = linkedEntities

    def __str__(self):
        return "{self.resolvedPassage} {self.linkedEntities}".format(self=self)

    def __repr__(self):
        return self.__str__()
