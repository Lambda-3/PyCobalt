# -*- coding: utf-8 -*-
from typing import List

from pycobalt.language import Token
from .constant_types import PronounType
from .language import Sentence
from .language import pronouns
from .references import Substitution, Reference


def substitute(sentences: List[Sentence],
               substitutions: List[Substitution]
               ) -> List[str]:
    for sentence in sentences:
        for substitution in substitutions:
            if sentence.index == substitution.sentence_index:
                __substitute_coreference(substitution.original,
                                         substitution.reference,
                                         sentence)
    return [t.text.strip() for t in sentences]


def __substitute_coreference(original_tokens: List[Token],
                             reference: Reference,
                             sentence: Sentence
                             ) -> None:
    original_term = " {} ".format(' '.join(t.word for t in original_tokens))
    reference_term = " {} ".format(' '.join(t.word for t in reference.tokens))

    new_text = " {} ".format(sentence.text)

    if pronouns.pronoun_type(original_tokens[0].lower) == PronounType.POSSESSIVE:
        new_text = new_text.replace(original_term, reference_term.rstrip() + "'s ")
    else:
        new_text = new_text.replace(original_term, reference_term)

    sentence.text = new_text
