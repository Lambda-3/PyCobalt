# -*- coding: utf-8 -*-


# noinspection PyPep8Naming
class Substitution(object):
    def __init__(self, sentenceIndex: int, originalTerm: str, referenceTerm: str):
        self.sentenceIndex = sentenceIndex
        self.originalTerm = originalTerm
        self.referenceTerm = referenceTerm

    def __str__(self):
        return "{self.sentenceIndex} '{self.originalTerm}' -> '{self.referenceTerm}'".format(self=self)
