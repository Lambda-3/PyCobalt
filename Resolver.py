# -*- coding: utf-8 -*-

import logging
import os
import re
from collections import Counter

from nltk.tokenize import sent_tokenize, word_tokenize
from pycorenlp import StanfordCoreNLP
from typing import List, Tuple, Dict, Union, Set

from classifier import GenderClassifier
from references import NameReference, NominalReference, PronominalReference
from references import ResolvedPassage
from references import Substitution
from references.TypeLookup import TypeLookup

logging.getLogger('requests').setLevel(logging.WARNING)


# noinspection PyPep8Naming
class Resolver(object):
    _typeLookUp = TypeLookup(
        os.path.normpath(
            os.path.join(
                os.path.abspath(__file__),
                os.path.pardir,
                'resources',
                'instance.types.bz2'
            )
        )
    )
    _separator = '---- <> ----'
    _nlp = StanfordCoreNLP('http://corenlp:9000')
    # _nlp = StanfordCoreNLP('http://localhost:9000')

    _genderClassifier = GenderClassifier()

    _personalPronouns = {'he': 'male', 'He': 'male', 'she': 'female', 'She': 'female', 'it': 'neutral',
                         'It': 'neutral', 'they': 'neutral/plural', 'They': 'neutral/plural'}
    _possessivePronouns = {'his': 'male', 'him': 'male', 'His': 'male', 'her': 'female', 'Her': 'female'}

    _reflexivePronouns = {'himself': 'male', 'herself': 'female'}

    @staticmethod
    def resolve(text: str, entityURI: str) -> List[Substitution]:

        substitutions = []

        sentences = Resolver._cleanText(sent_tokenize(text))

        if len(sentences) < 1:
            return []

        types = Resolver._typeLookUp.getType(entityURI).split(' ')

        nameReferences, pronominalReferences, nominalReferences = Resolver._collectReferencesAndCoreferences(
            text=sentences,
            types=types)

        firstNameMention = Resolver._getFirstNameMention(
            nameReferences=nameReferences,
            predominantGender=Resolver._getPredominantGender(pronominalReferences),
            text=sentences)

        Resolver._resolveNameCorefs(
            firstNameMention=firstNameMention,
            nameReferences=nameReferences,
            substitutions=substitutions)

        Resolver._resolvePronominalCorefs(
            firstNameMention=firstNameMention,
            nameReferences=nameReferences,
            pronominalReferences=pronominalReferences,
            substitutions=substitutions)

        Resolver._resolveNominalCorefs(
            firstNameMention=firstNameMention,
            nominalReferences=nominalReferences,
            substitutions=substitutions)

        return substitutions

    @staticmethod
    def _collectReferencesAndCoreferences(
            text: List[str],
            types: List[str]
    ) -> Tuple[List[NameReference], List[PronominalReference], List[NominalReference]]:

        nameReferences, pronominalReferences, nominalReferences = Resolver._collectReferences(text, types)
        return nameReferences, pronominalReferences, nominalReferences

    @staticmethod
    def substituteInText(
            text: str,
            substitutions: List[Substitution]
    ) -> Tuple[str, Dict[int, str]]:

        out_text = []
        resolvedSentences = {}

        for index, sentence in enumerate(sent_tokenize(text)):
            sentence = ' ' + sentence.replace('—', ' ').replace('\'s', ' \'s')
            for substitution in substitutions:
                if index == substitution.sentenceIndex:
                    sentence = Resolver._substituteCoref(substitution.originalTerm,
                                                         substitution.referenceTerm,
                                                         sentence)
                    resolvedSentences[index] = sentence

            out_text.append(sentence.strip())

        return "\n".join(out_text), resolvedSentences

    @staticmethod
    def _resolveNameCorefs(
            firstNameMention: NameReference,
            nameReferences: List[NameReference],
            substitutions: List[Substitution]) -> None:
        firstMention = firstNameMention.term if firstNameMention is not None else []
        for ne in nameReferences:

            if ne.term in firstMention:
                reference = firstMention
            else:
                reference = Resolver._getLongestPrecedentStringWithSubstring(nameReferences, ne.term, ne.sentence)

            ne.resolvedTerm = reference

            substitutions.append(Substitution(ne.sentence, ne.term, reference))

    @staticmethod
    def _resolvePronominalCorefs(
            firstNameMention: NameReference,
            nameReferences: List[NameReference],
            pronominalReferences: List[PronominalReference],
            substitutions: List[Substitution]) -> None:

        for pronoun in pronominalReferences:
            if pronoun.gender == firstNameMention.gender:
                nameTerm = firstNameMention.term
            else:
                nameTerm = Resolver._getClosestMatchingNameMention(pronoun, nameReferences)

            if nameTerm is None:
                nameTerm = pronoun.pronoun

            substitutions.append(Substitution(pronoun.sentence, pronoun.pronoun, nameTerm))

    @staticmethod
    def _resolveNominalCorefs(
            firstNameMention: NameReference,
            nominalReferences: List[NominalReference],
            substitutions) -> None:

        for nominalReference in nominalReferences:
            substitutions.append(Substitution(nominalReference.sentence, nominalReference.term, firstNameMention.term))

    @staticmethod
    def _cleanText(text: List[str]):
        cleanText = []
        for sentence in text:
            sentence = re.sub(r'\[\d+\]', '', sentence)
            sentence = sentence.strip()
            if sentence.endswith('.') or sentence.endswith('.\n'):
                if sentence != '':
                    cleanText.append(sentence)

        return cleanText

    @staticmethod
    def _substituteCoref(
            originalTerm: str,
            referenceTerm: str,
            sentence: str) -> str:

        originalTerm = ' ' + originalTerm + ' '
        referenceTerm = ' ' + referenceTerm + ' '

        # print(originalTerm + ' ----> ' + referenceTerm)

        sentence = re.sub(r'([.,;])', r' \1', sentence)

        if Resolver._getPronounType(originalTerm) != '':

            if referenceTerm == '':
                referenceTerm = originalTerm
                sentence = sentence.replace(originalTerm, referenceTerm)
            else:
                if Resolver._getPronounType(originalTerm) == 'personal':
                    sentence = sentence.replace(originalTerm, referenceTerm)
                elif Resolver._getPronounType(originalTerm) == 'possessive':
                    sentence = sentence.replace(originalTerm, referenceTerm + "'s ")
                else:
                    referenceTerm = originalTerm
                sentence = sentence.replace(originalTerm, referenceTerm)
        else:
            sentence = sentence.replace(originalTerm, referenceTerm)

        sentence = re.sub(r'\s+([.,;])', r'\1', sentence)

        return sentence

    @staticmethod
    def _getClosestMatchingNameMention(pronominalReference: PronominalReference,
                                       nameReferences: List[NameReference]
                                       ) -> Union[None, str]:
        for sentenceIndex in range(pronominalReference.sentence - 1, 0, -1):
            name = Resolver._getNameAtSentence(nameReferences, sentenceIndex, pronominalReference.gender,
                                               pronominalReference.entityType)

            if name is not None:
                return name.resolvedTerm

        return None

    @staticmethod
    def _getNameAtSentence(nameReferences: List[NameReference], sentenceIndex: int, gender: str, entityType: str):
        for name in nameReferences:
            if (sentenceIndex == name.sentence) \
                    and (name.gender == gender) \
                    and (name.type == entityType):
                return name

        return None

    @staticmethod
    def _getFirstNameMention(nameReferences: List[NameReference], predominantGender: str, text: List[str]
                             ) -> NameReference:
        for nameReference in nameReferences:
            if nameReference.sentence == 0 and nameReference.position < 10:
                if predominantGender in ['male', 'female']:
                    return NameReference(nameReference.term, 'PERSON', predominantGender, 'singular', 0, 0)
                else:
                    return NameReference(nameReference.term, 'OTHER', 'neutral', 'singular', 0, 0)

        for sentence in text:
            sentence = Resolver._cleanSentence(sentence)
            if sentence != '':
                entity = ''
                for token in word_tokenize(sentence):
                    if len(token) > 0 and token[0].isupper():
                        entity += token + ' '
                    else:
                        return NameReference(entity.strip(), 'OTHER', 'neutral', 'singular', 0, 0)

    @staticmethod
    def _getPredominantGender(pronominalReferences: List[PronominalReference]) -> str:
        cnt = Counter(
            p.gender.lower() for p in pronominalReferences
        ).most_common(n=1)

        if len(cnt) == 1:
            return cnt[0][0]

        return 'neutral'  # TODO default value?

    @staticmethod
    def _cleanSentence(
            sentence: str) -> str:
        sentence = sentence.replace('—', ' ').replace('–', ' ').replace("'s", " 's").replace('ʻ', '')
        return ''.join([token if ord(token) < 128 else ' ' for token in sentence])

    @staticmethod
    def _collectReferences(sentences: List[str], types: List[str]
                           ) -> Tuple[List[NameReference], List[PronominalReference], List[NominalReference]]:
        names, pronouns, nominals = [], [], []

        for i, sentence in enumerate(sentences):
            cleaned = Resolver._cleanSentence(sentence)
            annotated = Resolver._nlp.annotate(cleaned, properties={
                'annotators': 'tokenize,ssplit,ner',
                'outputFormat': 'json'
            })

            names.extend(list(Resolver._getNER(annotated['sentences'][0]['tokens'], i)))

            if Resolver._hasPronoun(cleaned):
                pronouns.append(Resolver._getPronoun(cleaned, i))

            nominals.extend(
                list(Resolver._getNominalReferences(annotated['sentences'][0]['tokens'], i, types))
            )

        return names, pronouns, nominals

    @staticmethod
    def _getNER(parsedString: List[Dict[str, str]], sentenceIndex: int) -> Set[NameReference]:
        nes = set()
        nerTerms = ''
        nerType = []
        nerPos = 0
        previousNER = 'O'
        for token in parsedString:
            if token['ner'] is not 'O':
                nerTerms += token['originalText'] + ' '
                nerType.append(token['ner'])
                if previousNER is not 'O':
                    nerPos = token['index']
            else:
                if Resolver._hasValidNERType(nerType):
                    if nerTerms is not '':
                        ne = NameReference(nerTerms.strip(),
                                           nerType[0],
                                           Resolver._getNameGender(nerTerms),
                                           Resolver._getNameNumber(nerTerms),
                                           sentenceIndex, nerPos)

                        nes.add(ne)
                        nerTerms = ''
                        nerType = []
                        nerPos = 0
            previousNER = token['ner']

        return nes

    @staticmethod
    def _getNominalReferences(parsedString: List[Dict[str, str]], sentenceIndex: int, types: List[str]):
        nominalRefs = set()
        previousDET = 0
        term = ''
        for token in parsedString:
            if token['originalText'].lower() == 'the':
                previousDET = 1
                term = token['originalText'] + ' '

            if previousDET and 'NN' == token['pos']:
                if token['originalText'].lower() in types:
                    term += token['originalText']
                    nr = NominalReference(term.strip(), sentenceIndex)
                    nominalRefs.add(nr)

        return nominalRefs

    @staticmethod
    def _hasPronoun(sentence: str):
        return any(
            token in Resolver._personalPronouns
            or token in Resolver._possessivePronouns
            or token in Resolver._reflexivePronouns
            for token in word_tokenize(sentence))

    @staticmethod
    def _getPronoun(sentence: str, sentenceIndex: int) -> PronominalReference:
        for token in word_tokenize(sentence):

            if token in Resolver._personalPronouns:
                number = 'singular'
                if 'plural' in Resolver._personalPronouns[token]:
                    number = 'plural'
                return PronominalReference(token,
                                           Resolver._personalPronouns[token],
                                           number,
                                           Resolver._getPronounType(token),
                                           Resolver._getEntityType(token),
                                           sentenceIndex,
                                           sentence.index(token))

            if token in Resolver._possessivePronouns:
                number = 'singular'
                if 'plural' in Resolver._possessivePronouns[token]:
                    number = 'plural'
                return PronominalReference(token,
                                           Resolver._possessivePronouns[token],
                                           number,
                                           Resolver._getPronounType(token),
                                           Resolver._getEntityType(token),
                                           sentenceIndex,
                                           sentence.index(token))

            if token in Resolver._reflexivePronouns:
                number = 'singular'
                if 'plural' in Resolver._reflexivePronouns[token]:
                    number = 'plural'
                return PronominalReference(token,
                                           Resolver._reflexivePronouns[token],
                                           number,
                                           Resolver._getPronounType(token),
                                           Resolver._getEntityType(token),
                                           sentenceIndex,
                                           sentence.index(token))

        return PronominalReference()

    @staticmethod
    def _getPronounType(token: str) -> str:

        if token in Resolver._personalPronouns:
            return 'personal'
        if token in Resolver._possessivePronouns:
            return 'possessive'
        if token in Resolver._reflexivePronouns:
            return 'reflexive'

        return ''

    @staticmethod
    def _getEntityType(token: str) -> str:
        if token.lower() in ['he', 'she', 'his', 'her', 'him', 'hers', 'they', 'their', 'theirs']:
            return 'PERSON'

        return 'THING'

    @staticmethod
    def _getLongestPrecedentStringWithSubstring(
            nameReferences: List[NameReference],
            substring: str,
            sentenceIndex: int) -> str:

        output = substring
        for nameReference in nameReferences:
            terms = nameReference.term.split(' ')
            if output in terms:
                if nameReference.sentence < sentenceIndex:
                    if len(terms) > len(output.split(' ')):
                        output = nameReference.term

        return output

    @staticmethod
    def _getNameGender(
            name: str) -> str:
        return Resolver._genderClassifier.classify(name.split(' ')[0])

    # noinspection PyUnusedLocal
    @staticmethod
    def _getNameNumber(name: str) -> str:
        return ''

    @staticmethod
    def _hasValidNERType(terms: List[str]) -> bool:
        return all(x not in terms for x in ['DATE', 'NUMBER', 'SET', 'MONEY', 'PERCENT', 'DURATION', 'MISC', 'ORDINAL'])

    @staticmethod
    def getPassagesAndLinkedEntities(
            substitutions: List[Substitution],
            resolvedSentences: Dict[int, str],
            entityLinks: Dict[str, str]) -> List[ResolvedPassage]:
        linkedPassages = []

        for index, sentence in resolvedSentences.items():
            linkedEntities = {}
            for substitution in substitutions:
                if substitution.sentenceIndex == index:
                    for entityLabel, entityLink in entityLinks.items():
                        if substitution.referenceTerm.lower() == entityLabel.lower():
                            linkedEntities[substitution.referenceTerm] = entityLink
                    if substitution.referenceTerm not in linkedEntities:
                        linkedEntities[substitution.referenceTerm] = ''

            if 'p.' not in sentence and '(' not in sentence and len(sentence) >= 25:
                linkedPassages.append(
                    ResolvedPassage(index, linkedEntities)
                )

        return linkedPassages

    @staticmethod
    def getEntityLinks(articleId: str, links: List[Dict[str, str]]) -> Dict[str, str]:
        entityLinks = {}
        label = articleId[articleId.rfind('/') + 1:].replace('_', ' ')
        entityLinks[label] = articleId
        for link in links:
            entityLinks[link['anchorText']] = link['link']

        return entityLinks
