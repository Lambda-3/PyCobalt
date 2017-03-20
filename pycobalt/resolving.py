# -*- coding: utf-8 -*-
import logging
import os
from collections import Counter

from typing import List, Tuple, Dict, Union, Optional

from .classifier import GenderClassifier
from .constant_types import QuantityType, GenderType, NERType, POSType
from .language import Sentence, Token
from .language import pronouns
from .language.stanford_tools import annotate_text
from .references import NameReference, NominalReference, PronominalReference
from .references import ResolvedPassage
from .references import Substitution
from .references.TypeLookup import TypeLookup

logging.getLogger('requests').setLevel(logging.WARNING)

__log = logging.getLogger(__name__)

__types = {}

__gender_classifier = GenderClassifier()
__log.debug("GenderClassifier loaded")


def __load_types():
    type_lookup = TypeLookup(
        os.path.normpath(
            os.path.join(
                os.path.abspath(__file__),
                os.path.pardir,
                'resources',
                'instance.types.bz2'
            )
        )
    )

    __log.debug("TypeLookup loaded")

    return type_lookup


def resolve(text: str,
            entity_uri: str = ''
            ) -> Tuple[List[Sentence], List[Substitution]]:
    substitutions: List[Substitution] = []

    sentences: List[Sentence] = annotate_text(text)

    if len(sentences) < 1:
        return [], []

    if len(entity_uri) > 0 and 'lookup' in __types:
        __types['lookup'] = __load_types()
    else:
        __types['lookup'] = None

    if 'lookup' not in __types or __types['lookup'] is None:
        types = []
    else:
        types = __types['lookup'].type(entity_uri).split(' ')

    name_refs, pronominal_refs, nominal_refs = __collect_references_and_coreferences(
        sentences=sentences,
        types=types)

    first_name_mention = __first_name_mention(
        name_references=name_refs,
        predominant_gender=__predominant_gender(pronominal_refs),
        sentences=sentences)

    __resolve_name_coreferences(
        first_name_mention=first_name_mention,
        name_references=name_refs,
        substitutions=substitutions)

    __resolve_pronominal_coreferences(
        first_name_mention=first_name_mention,
        name_references=name_refs,
        pronominal_references=pronominal_refs,
        substitutions=substitutions)

    __resolve_nominal_coreferences(
        first_name_mention=first_name_mention,
        nominal_references=nominal_refs,
        substitutions=substitutions)

    return sentences, substitutions


def __collect_references_and_coreferences(sentences: List[Sentence],
                                          types: List[str]
                                          ) -> Tuple[List[NameReference],
                                                     List[PronominalReference],
                                                     List[NominalReference]]:
    name_refs, pronoun_refs, nominal_refs = [], [], []

    for sentence in sentences:
        name_refs.extend(__name_references(sentence))
        pronoun_refs.extend(__pronominal_references(sentence))
        nominal_refs.extend(__nominal_references(sentence, types))

    return name_refs, pronoun_refs, nominal_refs


def __name_references(sentence: Sentence
                      ) -> List[NameReference]:
    nes: List[NameReference] = []
    entity_tokens: List[Token] = []
    entity_types: List[str] = []
    for token in sentence.tokens:
        if token.ner is not NERType.OTHER:
            entity_tokens.append(token)
            entity_types.append(token.ner)
        else:
            if len(entity_types) > 0 and __valid_ner_type(entity_types):
                if len(entity_tokens) > 0:
                    ne = NameReference(tokens=entity_tokens,
                                       entity_type=entity_types[0],
                                       gender=__gender(entity_tokens),
                                       quantity=__quantity(entity_tokens),
                                       sentence_index=sentence.index)

                    nes.append(ne)
                    entity_tokens = []
                    entity_types = []
            else:
                entity_tokens = []
                entity_types = []

    return nes


def __pronominal_references(sentence: Sentence
                            ) -> List[PronominalReference]:
    pronominal_references: List[PronominalReference] = []
    for token in sentence.tokens:

        if token.lower in pronouns.PERSONAL:
            pronoun_lookup = pronouns.PERSONAL[token.lower]
        elif token.lower in pronouns.POSSESSIVE:
            pronoun_lookup = pronouns.POSSESSIVE[token.lower]
        elif token.lower in pronouns.REFLEXIVE:
            pronoun_lookup = pronouns.REFLEXIVE[token.lower]
        else:
            continue

        pronominal_references.append(PronominalReference(tokens=[token],
                                                         gender=pronoun_lookup.get('gender'),
                                                         quantity=pronoun_lookup.get('quantity'),
                                                         pronoun_type=pronouns.pronoun_type(token.lower),
                                                         entity_type=__entity_type(token.lower),
                                                         sentence_index=sentence.index))

    return pronominal_references


def __nominal_references(sentence: Sentence,
                         types: List[str]
                         ) -> List[NominalReference]:
    nominal_references: List[NominalReference] = []
    previous_det = False
    tokens: List[Token] = []
    for token in sentence.tokens:
        if token.lower == 'the':
            previous_det = True
            tokens = token

        if previous_det and token.pos == POSType.NN:
            if token.lower in types:
                tokens.append(token)
                nominal_references.append(NominalReference(sentence_index=sentence.index,
                                                           tokens=tokens))

    return nominal_references


def __resolve_name_coreferences(first_name_mention: NameReference,
                                name_references: List[NameReference],
                                substitutions: List[Substitution]
                                ) -> None:
    first_name: str = ' '.join([t.word for t in first_name_mention.tokens])
    for ne in name_references:

        if ' '.join([t.word for t in ne.tokens]) in first_name:
            reference: NameReference = first_name_mention
        else:
            reference = __longest_precedent(name_references, ne)

        substitutions.append(Substitution(ne.sentence_index, ne.tokens, reference))


def __resolve_pronominal_coreferences(first_name_mention: NameReference,
                                      name_references: List[NameReference],
                                      pronominal_references: List[PronominalReference],
                                      substitutions: List[Substitution]
                                      ) -> None:
    for pronoun_ref in pronominal_references:
        if pronoun_ref.gender == first_name_mention.gender:
            name_tokens: NameReference = first_name_mention
        else:
            name_tokens: NameReference = __closest_matching_name_mention(pronoun_ref, name_references)

        if name_tokens is None:
            name_tokens: NameReference = pronoun_ref

        substitutions.append(
            Substitution(
                sentence_index=pronoun_ref.sentence_index,
                original=pronoun_ref.tokens,
                reference=name_tokens))


def __closest_matching_name_mention(pronominal_reference: PronominalReference,
                                    name_references: List[NameReference]
                                    ) -> Optional[NameReference]:
    for name_reference in [n for n in sorted(name_references, key=lambda x: x.sentence_index, reverse=True) if
                           n.sentence_index <= pronominal_reference.sentence_index]:
        if __name_at_sentence(name_reference,
                              pronominal_reference.gender,
                              pronominal_reference.entity_type):
            return name_reference

    return None


def __name_at_sentence(name_reference: NameReference,
                       gender: GenderType,
                       entity_type: NERType
                       ) -> bool:
    return name_reference.gender == gender and name_reference.entity_type == entity_type


def __resolve_nominal_coreferences(first_name_mention: NameReference,
                                   nominal_references: List[NominalReference],
                                   substitutions
                                   ) -> None:
    for nominal_reference in nominal_references:
        substitutions.append(
            Substitution(nominal_reference.sentence_index, nominal_reference.tokens, first_name_mention.tokens))


def __first_name_mention(name_references: List[NameReference],
                         predominant_gender: GenderType,
                         sentences: List[Sentence]
                         ) -> NameReference:
    for name_reference in name_references:
        if name_reference.sentence_index == 0 and name_reference.tokens[0].index < 10:
            if predominant_gender in [GenderType.MALE, GenderType.FEMALE]:
                return NameReference(sentence_index=0,
                                     tokens=name_reference.tokens,
                                     entity_type=NERType.PERSON,
                                     gender=predominant_gender,
                                     quantity=QuantityType.SINGULAR)
            else:
                return NameReference(sentence_index=0,
                                     tokens=name_reference.tokens,
                                     entity_type=NERType.OTHER,
                                     gender=GenderType.NEUTRAL,
                                     quantity=QuantityType.SINGULAR)

    for sentence in sentences:
        if len(sentence.tokens) > 0:
            entity_tokens = []
            for token in sentence.tokens:
                if len(token.word) > 0 and token.word[0].isupper():
                    entity_tokens.append(token)
                else:
                    return NameReference(sentence_index=0,
                                         tokens=entity_tokens,
                                         entity_type=NERType.PERSON,
                                         gender=GenderType.NEUTRAL,
                                         quantity=QuantityType.SINGULAR)


def __predominant_gender(pronominal_references: List[PronominalReference]
                         ) -> GenderType:
    cnt = Counter(
        p.gender for p in pronominal_references
    ).most_common(n=1)

    if len(cnt) == 1:
        return cnt[0][0]

    return GenderType.NEUTRAL


def __has_pronoun(sentence: Sentence
                  ) -> bool:
    return any(
        token.lower in pronouns.PERSONAL
        or token.lower in pronouns.POSSESSIVE
        or token.lower in pronouns.REFLEXIVE
        for token in sentence.tokens)


def __entity_type(token: str
                  ) -> NERType:
    if token in ['he', 'she', 'his', 'her', 'him', 'hers', 'they', 'their', 'theirs']:
        return NERType.PERSON

    return NERType.THING


def __longest_precedent(name_references: List[NameReference],
                        sub_reference: NameReference
                        ) -> NameReference:
    reference: NameReference = sub_reference
    for name_reference in name_references:
        if name_reference.sentence_index < sub_reference.sentence_index \
                and len(name_references) > len(reference.tokens) \
                and ' '.join(t.word for t in reference.tokens) in ' '.join(t.word for t in name_reference.tokens):
            reference = name_reference

    return reference


def __gender(name: List[Token]
             ) -> GenderType:
    return __gender_classifier.classify(name[0].word)


def __quantity(name: List[Token]
               ) -> QuantityType:
    if name[-1].word.endswith('s'):
        return QuantityType.PLURAL
    return QuantityType.SINGULAR


def __valid_ner_type(terms: List[NERType]
                     ) -> bool:
    return all(x not in terms for x in
               [NERType.DATE, NERType.NUMBER, NERType.SET, NERType.MONEY, NERType.PERCENT, NERType.DURATION,
                NERType.MISC, NERType.ORDINAL])


def get_passages_and_linked_entities(substitutions: List[Substitution],
                                     resolved_sentences: List[Sentence],
                                     entity_links: Dict[str, str]
                                     ) -> List[ResolvedPassage]:
    linked_passages: List[ResolvedPassage] = []

    for sentence in resolved_sentences:
        linked_entities: Dict[str, str] = {}
        for substitution in substitutions:
            reference: str = " ".join(t.word for t in substitution.reference.tokens)
            reference_low: str = reference.lower()
            if substitution.sentence_index == sentence.index:
                for entity_label, entity_link in entity_links.items():
                    if reference_low == entity_label.lower():
                        linked_entities[reference] = entity_link
                if reference not in linked_entities:
                    linked_entities[reference] = ''

        sentence_string: str = " ".join(t.word for t in sentence.tokens)

        if 'p.' not in sentence_string and '(' not in sentence_string and len(sentence.tokens) >= 25:
            linked_passages.append(
                ResolvedPassage(sentence.index, linked_entities)
            )

    return linked_passages


def get_entity_links(article_id: str,
                     links: List[Dict[str, str]]
                     ) -> Dict[str, str]:
    entity_links: Dict[str, str] = {}
    label: str = article_id[article_id.rfind('/') + 1:].replace('_', ' ')
    entity_links[label] = article_id
    for link in links:
        entity_links[link['anchorText']] = link['link']

    return entity_links
