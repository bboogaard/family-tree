import re
from typing import Dict

import inflection


camelize_re = re.compile(r"[a-z0-9]?_[a-z0-9]")


def underscore_to_camel(match):
    group = match.group()
    if len(group) == 3:
        return group[0] + group[2].upper()
    else:
        return group[1].upper()


def with_camel_keys(data: Dict) -> Dict:
    keys_map = {
        key: camelize(key)
        for key in data.keys()
        if isinstance(key, str) and "_" in key
    }
    return {
        keys_map.get(key, key): val
        for key, val in data.items()
    }


def from_camel_keys(data: Dict) -> Dict:
    keys_map = {
        key: inflection.underscore(key)
        for key in data.keys()
        if isinstance(key, str)
    }
    return {
        keys_map.get(key, key): val
        for key, val in data.items()
    }


def camelize(value: str) -> str:
    return re.sub(camelize_re, underscore_to_camel, value)
