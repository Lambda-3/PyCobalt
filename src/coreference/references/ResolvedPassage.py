# -*- coding: utf-8 -*-
from typing import Dict


class ResolvedPassage(object):
    def __init__(self, resolved_passage: int, linked_entities: Dict[str, str]):
        self.resolved_passage = resolved_passage
        self.linked_entities = linked_entities

    def __str__(self):
        return "{self.resolved_passage} {self.linked_entities}".format(self=self)

    def __repr__(self):
        return self.__str__()
