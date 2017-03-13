import os
import re
from pycorenlp import StanfordCoreNLP
from typing import List, Dict, Any, Union

from .model import Sentence, Token
from ..constant_types import NERType, POSType

__corenlp_url = os.environ['PYCOBALT_CORENLP'] if 'PYCOBALT_CORENLP' in os.environ else 'http://localhost:9000'

__nlp = StanfordCoreNLP(__corenlp_url)


def annotate_text(text: str = "") -> List[Sentence]:
    annotations = __nlp.annotate(
        text=_clean_text(text),
        properties={
            'annotators': 'tokenize,ssplit,ner',
            'outputFormat': 'json'
        }
    )['sentences']

    return __convert_corenlp(annotations)


def __convert_corenlp(text: List[Dict[str, Union[int, str]]]) -> List[Sentence]:
    converted = []

    for sentence_index, sentence in enumerate(sorted(text, key=lambda x: x['index'])):
        tokens = sorted(sentence['tokens'], key=lambda x: x['index'])
        converted.append(
            Sentence(
                index=sentence_index,
                text=__merge_tokens(tokens),
                tokens=[
                    Token(
                        index=token_index,
                        word=token['word'],
                        original_word=token['originalText'],
                        pos=__convert_corenlp_pos(token['pos']),
                        ner=__convert_corenlp_ner(token['ner']))
                    for token_index, token in enumerate(tokens)
                ]
            )
        )

    return converted


def __merge_tokens(tokens: List[Dict[str, str]]) -> str:
    return "".join([t['originalText'] + t['after'] for t in tokens]).strip()


def _clean_text(text: str) -> str:
    # remove [123] from text
    text = re.sub(r'\[\d+\]', '', text)

    # remove trailing/leading whitespaces
    text = text.strip()

    # remove duplicated lines
    text = re.sub('r\n{2,}', '\n', text)

    return text


def __convert_corenlp_ner(ner: str) -> NERType:
    if ner is None or len(ner) < 1:
        return NERType.NONE

    if ner == 'PERSON':
        return NERType.PERSON
    elif ner == 'O':
        return NERType.OTHER
    elif ner == 'DATE':
        return NERType.DATE
    elif ner == 'NUMBER':
        return NERType.NUMBER
    elif ner == 'SET':
        return NERType.SET
    elif ner == 'MONEY':
        return NERType.MONEY
    elif ner == 'PERCENT':
        return NERType.PERCENT
    elif ner == 'DURATION':
        return NERType.DURATION
    elif ner == 'MISC':
        return NERType.MISC
    elif ner == 'ORDINAL':
        return NERType.ORDINAL
    else:
        return NERType.OTHER


def __convert_corenlp_pos(pos: str) -> POSType:
    if pos is None or len(pos) < 1:
        return POSType.NONE

    if pos in ['NN']:
        return POSType.NN
    else:
        return POSType.OTHER
