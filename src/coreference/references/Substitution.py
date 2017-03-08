# -*- coding: utf-8 -*-


class Substitution(object):
    def __init__(self, sentence_index: int, original: str, reference: str):
        self.sentence_index = sentence_index
        self.original = original
        self.reference = reference

    def __str__(self):
        return "{self.sentence_index} '{self.original}' -> '{self.reference}'".format(self=self)
