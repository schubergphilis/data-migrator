import re

_PHONE_CHARS=re.compile('[^\+\d]+')
_INTERNATIONAL_ZERO_START=re.compile('^00')
_MUNICIPALY_ZERO_START=re.compile('^0')

def clean_phone(v):
    '''Cleans phone numbers to dutch clean format

        00 31 6 - 20 20 20 20 -> +31620202020
        06 20 20 20 20 -> +31620202020
        020 -123 345 6 -> +31201233456
        +440.203.020.23 -> +4402030203
        +440a203a020a23 -> +4402030203
    '''

    v = _PHONE_CHARS.sub('', v)
    v = _INTERNATIONAL_ZERO_START.sub('+', v)
    v = _MUNICIPALY_ZERO_START.sub('+31', v)
    return v
