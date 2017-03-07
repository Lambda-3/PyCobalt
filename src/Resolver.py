# -*- coding: utf-8 -*-
import logging
import os
import re
from collections import Counter

from nltk.tokenize import sent_tokenize, word_tokenize
from pycorenlp import StanfordCoreNLP
from typing import List, Tuple, Dict, Union, Set

from classifier import GenderClassifier
from constant_types import PronounType, QuantityType, GenderType, EntityType
from references import NameReference, NominalReference, PronominalReference
from references import ResolvedPassage
from references import Substitution
from references.TypeLookup import TypeLookup

logging.getLogger('requests').setLevel(logging.WARNING)


# noinspection PyPep8Naming
class Resolver(object):
    _type_lookup = TypeLookup(
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
    _nlp = StanfordCoreNLP('http://localhost:9000')
    # _nlp = StanfordCoreNLP('http://localhost:9000')

    _gender_classifier = GenderClassifier()

    _personal_pronouns = {
        'he': {
            'gender': GenderType.MALE,
            'quantity': QuantityType.SINGULAR
        },
        'she': {
            'gender': GenderType.FEMALE,
            'quantity': QuantityType.SINGULAR
        },
        'it': {
            'gender': GenderType.NEUTRAL,
            'quantity': QuantityType.SINGULAR
        },
        'they': {
            'gender': GenderType.NEUTRAL,
            'quantity': QuantityType.PLURAL
        }
    }

    _possessive_pronouns = {
        'his': {
            'gender': GenderType.MALE,
            'quantity': QuantityType.SINGULAR
        },
        'him': {
            'gender': GenderType.MALE,
            'quantity': QuantityType.SINGULAR
        },
        'her': {
            'gender': GenderType.FEMALE,
            'quantity': QuantityType.SINGULAR
        }
    }

    _reflexive_pronouns = {
        'himself': {
            'gender': GenderType.MALE,
            'quantity': QuantityType.SINGULAR
        },
        'herself': {
            'gender': GenderType.FEMALE,
            'quantity': QuantityType.SINGULAR
        }
    }

    @staticmethod
    def resolve(text: str, entity_uri: str) -> List[Substitution]:

        substitutions = []

        sentences = Resolver._clean_text(sent_tokenize(text))

        if len(sentences) < 1:
            return []

        types = Resolver._type_lookup.type(entity_uri).split(' ')

        name_references, pronominal_references, nominal_references = Resolver._collect_references_and_coreferences(
            text=sentences,
            types=types)

        first_name_mention = Resolver._first_name_mention(
            name_references=name_references,
            predominant_gender=Resolver._predominant_gender(pronominal_references),
            text=sentences)

        Resolver._resolve_name_coreferences(
            first_name_mention=first_name_mention,
            name_references=name_references,
            substitutions=substitutions)

        Resolver._resolve_pronominal_coreferences(
            first_name_mention=first_name_mention,
            name_references=name_references,
            pronominal_references=pronominal_references,
            substitutions=substitutions)

        Resolver._resolve_nominal_coreferences(
            first_name_mention=first_name_mention,
            nominal_references=nominal_references,
            substitutions=substitutions)

        return substitutions

    @staticmethod
    def _collect_references_and_coreferences(
            text: List[str],
            types: List[str]
    ) -> Tuple[List[NameReference], List[PronominalReference], List[NominalReference]]:

        name_references, pronominal_references, nominal_references = Resolver._collect_references(text, types)
        return name_references, pronominal_references, nominal_references

    @staticmethod
    def substitute_in_text(
            text: str,
            substitutions: List[Substitution]
    ) -> str:

        out_text = []

        for index, sentence in enumerate(sent_tokenize(text)):
            sentence = ' ' + sentence.replace('—', ' ').replace('\'s', ' \'s')
            for substitution in substitutions:
                if index == substitution.sentence_index:
                    sentence = Resolver._substitute_coreference(substitution.original,
                                                                substitution.reference,
                                                                sentence)
            out_text.append(sentence.strip())

        return "\n".join(out_text)

    @staticmethod
    def _resolve_name_coreferences(
            first_name_mention: NameReference,
            name_references: List[NameReference],
            substitutions: List[Substitution]) -> None:
        first_name = first_name_mention.term if first_name_mention is not None else ""
        for ne in name_references:

            if ne.term in first_name:
                reference = first_name
            else:
                reference = Resolver._longest_precedent_string_with_substring(
                    name_references, ne.term, ne.sentence_index)

            ne.resolved_term = reference

            substitutions.append(Substitution(ne.sentence_index, ne.term, reference))

    @staticmethod
    def _resolve_pronominal_coreferences(
            first_name_mention: NameReference,
            name_references: List[NameReference],
            pronominal_references: List[PronominalReference],
            substitutions: List[Substitution]) -> None:

        for pronoun in pronominal_references:
            if pronoun.gender == first_name_mention.gender:
                name_term = first_name_mention.term
            else:
                name_term = Resolver._closest_matching_name_mention(pronoun, name_references)

            if name_term is None:
                name_term = pronoun.pronoun

            substitutions.append(Substitution(pronoun.sentence_index, pronoun.pronoun, name_term))

    @staticmethod
    def _resolve_nominal_coreferences(
            first_name_mention: NameReference,
            nominal_references: List[NominalReference],
            substitutions) -> None:

        for nominal_reference in nominal_references:
            substitutions.append(
                Substitution(nominal_reference.sentence_index, nominal_reference.term, first_name_mention.term))

    @staticmethod
    def _clean_text(text: List[str]):
        cleanText = []
        for sentence in text:
            sentence = re.sub(r'\[\d+\]', '', sentence)
            sentence = sentence.strip()
            if sentence.endswith('.') or sentence.endswith('.\n'):
                if sentence != '':
                    cleanText.append(sentence)

        return cleanText

    @staticmethod
    def _substitute_coreference(
            original_term: str,
            reference_term: str,
            sentence: str) -> str:

        original_term = ' ' + original_term + ' '
        reference_term = ' ' + reference_term + ' '

        # print(originalTerm + ' ----> ' + referenceTerm)

        sentence = re.sub(r'([.,;])', r' \1', sentence)

        if Resolver._pronoun_type(original_term) != PronounType.NONE:

            if reference_term == '':
                reference_term = original_term
                sentence = sentence.replace(original_term, reference_term)
            else:
                if Resolver._pronoun_type(original_term) == PronounType.PERSONAL:
                    sentence = sentence.replace(original_term, reference_term)
                elif Resolver._pronoun_type(original_term) == PronounType.POSSESSIVE:
                    sentence = sentence.replace(original_term, reference_term + "'s ")
                else:
                    reference_term = original_term
                    sentence = sentence.replace(original_term, reference_term)
        else:
            sentence = sentence.replace(original_term, reference_term)

        sentence = re.sub(r'\s+([.,;])', r'\1', sentence)

        return sentence

    @staticmethod
    def _closest_matching_name_mention(pronominal_reference: PronominalReference,
                                       name_references: List[NameReference]
                                       ) -> Union[None, str]:
        for sentence_index in range(pronominal_reference.sentence_index - 1, 0, -1):
            name = Resolver._name_at_sentence(name_references, sentence_index, pronominal_reference.gender,
                                              pronominal_reference.entity_type)

            if name is not None:
                return name.resolved_term

        return None

    @staticmethod
    def _name_at_sentence(name_references: List[NameReference], sentence_index: int, gender: GenderType,
                          entity_type: EntityType):
        for name in name_references:
            if (sentence_index == name.sentence_index) \
                    and (name.gender == gender) \
                    and (name.entity_type == entity_type):
                return name

        return None

    @staticmethod
    def _first_name_mention(name_references: List[NameReference], predominant_gender: GenderType, text: List[str]
                            ) -> NameReference:
        for name_reference in name_references:
            if name_reference.sentence_index == 0 and name_reference.word_position < 10:
                if predominant_gender in [GenderType.MALE, GenderType.FEMALE]:
                    return NameReference(name_reference.term, EntityType.PERSON, predominant_gender,
                                         QuantityType.SINGULAR, 0, 0)
                else:
                    return NameReference(name_reference.term, EntityType.OTHER, GenderType.NEUTRAL,
                                         QuantityType.SINGULAR, 0, 0)

        for sentence in text:
            sentence = Resolver._clean_sentence(sentence)
            if sentence != '':
                entity = ''
                for token in word_tokenize(sentence):
                    if len(token) > 0 and token[0].isupper():
                        entity += token + ' '
                    else:
                        return NameReference(entity.strip(), EntityType.OTHER, GenderType.NEUTRAL,
                                             QuantityType.SINGULAR, 0, 0)

    @staticmethod
    def _predominant_gender(pronominal_references: List[PronominalReference]) -> GenderType:
        cnt = Counter(
            p.gender for p in pronominal_references
        ).most_common(n=1)

        if len(cnt) == 1:
            return cnt[0][0]

        return GenderType.NEUTRAL  # TODO default value?

    @staticmethod
    def _clean_sentence(
            sentence: str) -> str:
        sentence = sentence.replace('—', ' ').replace('–', ' ').replace("'s", " 's").replace('ʻ', '')
        return ''.join([token if ord(token) < 128 else ' ' for token in sentence])

    @staticmethod
    def _collect_references(sentences: List[str], types: List[str]
                            ) -> Tuple[List[NameReference], List[PronominalReference], List[NominalReference]]:
        names, pronouns, nominals = [], [], []

        for i, sentence in enumerate(sentences):
            cleaned = Resolver._clean_sentence(sentence)
            annotated = Resolver._nlp.annotate(cleaned, properties={
                'annotators': 'tokenize,ssplit,ner',
                'outputFormat': 'json'
            })

            names.extend(list(Resolver._getNER(annotated['sentences'][0]['tokens'], i)))

            if Resolver._has_pronoun(cleaned):
                pronouns.extend(Resolver._pronominal_references(cleaned, i))

            nominals.extend(
                list(Resolver._nominal_references(annotated['sentences'][0]['tokens'], i, types))
            )

        return names, pronouns, nominals

    @staticmethod
    def _getNER(parsedString: List[Dict[str, str]], sentence_index: int) -> Set[NameReference]:
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
                if len(nerType) > 0 and Resolver._valid_NER_type(nerType):
                    if nerTerms is not '':
                        ne = NameReference(term=nerTerms.strip(),
                                           entity_type=nerType[0],
                                           gender=Resolver._gender(nerTerms),
                                           quantity=Resolver._quantity(nerTerms),
                                           sentence_index=sentence_index,
                                           word_position=nerPos)

                        nes.add(ne)
                        nerTerms = ''
                        nerType = []
                        nerPos = 0
                else:
                    nerTerms = ''
                    nerType = []
                    nerPos = 0
            previousNER = token['ner']

        return nes

    @staticmethod
    def _nominal_references(annotated_tokens: List[Dict[str, str]], sentence_index: int, types: List[str]):
        nominal_references = set()
        previous_det = False
        term = ''
        for annotated_token in annotated_tokens:
            if annotated_token['originalText'].lower() == 'the':
                previous_det = True
                term = annotated_token['originalText'] + ' '

            if previous_det and 'NN' == annotated_token['pos']:
                if annotated_token['originalText'].lower() in types:
                    term += annotated_token['originalText']
                    nr = NominalReference(term.strip(), sentence_index)
                    nominal_references.add(nr)

        return nominal_references

    @staticmethod
    def _has_pronoun(sentence: str):
        return any(
            token.lower() in Resolver._personal_pronouns
            or token.lower() in Resolver._possessive_pronouns
            or token.lower() in Resolver._reflexive_pronouns
            for token in word_tokenize(sentence))

    @staticmethod
    def _pronominal_references(sentence: str, sentence_index: int) -> List[PronominalReference]:
        pronominal_references = []
        for token in word_tokenize(sentence):

            possible_pronoun = token.lower()

            if possible_pronoun in Resolver._personal_pronouns:
                lookup = Resolver._personal_pronouns[possible_pronoun]
            elif possible_pronoun in Resolver._possessive_pronouns:
                lookup = Resolver._possessive_pronouns[possible_pronoun]
            elif possible_pronoun in Resolver._reflexive_pronouns:
                lookup = Resolver._reflexive_pronouns[possible_pronoun]
            else:
                continue

            pronominal_references.append(PronominalReference(pronoun=token,
                                                             gender=lookup.get('gender'),
                                                             quantity=lookup.get('quantity'),
                                                             pronoun_type=Resolver._pronoun_type(possible_pronoun),
                                                             entity_type=Resolver._entity_type(possible_pronoun),
                                                             sentence_index=sentence_index,
                                                             word_position=sentence.index(token)))

        return pronominal_references

    @staticmethod
    def _pronoun_type(token: str) -> PronounType:

        token = token.strip().lower()

        if token in Resolver._personal_pronouns:
            return PronounType.PERSONAL
        if token in Resolver._possessive_pronouns:
            return PronounType.POSSESSIVE
        if token in Resolver._reflexive_pronouns:
            return PronounType.REFLEXIVE

        return PronounType.NONE

    @staticmethod
    def _entity_type(token: str) -> EntityType:
        if token.lower() in ['he', 'she', 'his', 'her', 'him', 'hers', 'they', 'their', 'theirs']:
            return EntityType.PERSON

        return EntityType.THING

    @staticmethod
    def _longest_precedent_string_with_substring(
            name_references: List[NameReference],
            substring: str,
            sentence_index: int) -> str:

        output = substring
        for name_reference in name_references:
            terms = name_reference.term.split(' ')
            if output in terms:
                if name_reference.sentence_index < sentence_index:
                    if len(terms) > len(output.split(' ')):
                        output = name_reference.term

        return output

    @staticmethod
    def _gender(
            name: str) -> GenderType:
        return Resolver._gender_classifier.classify(name.split(' ')[0])

    # noinspection PyUnusedLocal
    @staticmethod
    def _quantity(name: str) -> QuantityType:
        return QuantityType.SINGULAR

    @staticmethod
    def _valid_NER_type(terms: List[str]) -> bool:
        return all(x not in terms for x in ['DATE', 'NUMBER', 'SET', 'MONEY', 'PERCENT', 'DURATION', 'MISC', 'ORDINAL'])

    @staticmethod
    def get_passages_and_linked_entities(
            substitutions: List[Substitution],
            resolved_sentences: Dict[int, str],
            entity_links: Dict[str, str]) -> List[ResolvedPassage]:
        linked_passages = []

        for index, sentence in resolved_sentences.items():
            linked_entities = {}
            for substitution in substitutions:
                if substitution.sentence_index == index:
                    for entityLabel, entityLink in entity_links.items():
                        if substitution.reference.lower() == entityLabel.lower():
                            linked_entities[substitution.reference] = entityLink
                    if substitution.reference not in linked_entities:
                        linked_entities[substitution.reference] = ''

            if 'p.' not in sentence and '(' not in sentence and len(sentence) >= 25:
                linked_passages.append(
                    ResolvedPassage(index, linked_entities)
                )

        return linked_passages

    @staticmethod
    def get_entity_links(article_id: str, links: List[Dict[str, str]]) -> Dict[str, str]:
        entity_links = {}
        label = article_id[article_id.rfind('/') + 1:].replace('_', ' ')
        entity_links[label] = article_id
        for link in links:
            entity_links[link['anchorText']] = link['link']

        return entity_links
