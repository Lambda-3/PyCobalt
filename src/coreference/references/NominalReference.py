class NominalReference(object):
    def __init__(self, term: str, sentence_index: int):
        self.term = term
        self.sentence_index = sentence_index

    def __str__(self):
        return "{self.term} {self.sentence}".format(self=self)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.term == other.term) and (self.sentence_index == other.sentence_index)

    def __hash__(self):
        return hash(self.term + str(self.sentence_index))
