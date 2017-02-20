class NameReference(object):
    def __init__(self, term: str, type: str, gender: str, number: str, sentence: int, position: int):
        self.term = term
        self.type = type
        if type == 'PERSON':
            self.gender = gender
        else:
            self.gender = 'neutral'
        self.number = number
        self.sentence = sentence
        self.position = position
        self.resolvedTerm = term

    def getSentenceIndex(self):
        return self.sentence

    def __str__(self):
        return "{self.term} {self.type} {self.gender} {self.number} {self.sentence} {self.position}\n".format(self=self)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.term == other.term) \
               and (self.type == other.type) \
               and (self.sentence == other.sentence) \
               and (self.position == other.position)

    def __hash__(self):
        return hash(self.term + self.type + str(self.sentence))
