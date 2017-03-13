from ..constant_types.GenderType import GenderType
from ..constant_types.PronounType import PronounType
from ..constant_types.QuantityType import QuantityType

PERSONAL = {
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

POSSESSIVE = {
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

REFLEXIVE = {
    'himself': {
        'gender': GenderType.MALE,
        'quantity': QuantityType.SINGULAR
    },
    'herself': {
        'gender': GenderType.FEMALE,
        'quantity': QuantityType.SINGULAR
    }
}


def pronoun_type(token: str
                 ) -> PronounType:
    if token in PERSONAL:
        return PronounType.PERSONAL
    if token in POSSESSIVE:
        return PronounType.POSSESSIVE
    if token in REFLEXIVE:
        return PronounType.REFLEXIVE

    return PronounType.NONE
