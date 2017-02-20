class NominalReference(object):
    def __init__(self, term: str, sentence: int):
        self.term = term
        self.sentence = sentence

    def getSentenceIndex(self):
        return self.sentence

    def __str__(self):
        return "{self.term} {self.sentence}".format(self=self)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.term == other.term) and (self.sentence == other.sentence)

    def __hash__(self):
        return hash(self.term + str(self.sentence))
