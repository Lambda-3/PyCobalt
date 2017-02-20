import random

import nltk
from nltk.corpus import names


class GenderClassifier(object):
    def __init__(self):
        self.classifier = self.__train()

    @staticmethod
    def gender_features(word):
        features = {"suffix(1)": word[-1:],
                    "suffix(2)": word[-2:],
                    "suffix(3)": word[-3:]}
        return features

    def __train(self):
        # Training a gender classifier
        labeled_names = ([(name, 'male') for name in names.words('male.txt')] +
                         [(name, 'female') for name in names.words('female.txt')])

        random.shuffle(labeled_names)

        feature_sets = [(self.gender_features(n), gender) for (n, gender) in labeled_names]
        train_set, test_set = feature_sets[500:], feature_sets[:500]
        return nltk.NaiveBayesClassifier.train(train_set)

    def classify(self, name: str) -> str:
        return self.classifier.classify(GenderClassifier.gender_features(name))
