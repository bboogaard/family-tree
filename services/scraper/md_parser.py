import logging
import re
from typing import Any, Callable, Dict, List, Optional


re_schema = re.compile(r'http://schema.org/([\w]+)')

re_url = re.compile(
    r'https://www\.genealogieonline\.nl(/bismeijer-family/)?([a-zA-Z0-9]+)\.php'
)


logger = logging.getLogger(__name__)


def parse_person(data: Dict) -> str:
    try:
        properties = data['properties']
        if not isinstance(properties, Dict):
            logger.error("Couldn't parse Person element: {}".format(data))
        if 'url' in properties:
            properties['url'] = _parse_url(properties['url'])
        return properties
    except KeyError:
        logger.error("Couldn't parse Person element: {}".format(data))
        return ''


def parse_place(data: Dict) -> str:
    try:
        return data['properties']['address']['properties']['addressLocality']
    except KeyError:
        logger.error("Couldn't parse Place element: {}".format(data))
        return ''


def get_parser(schema_type: str) -> Optional[Callable]:
    if schema_type == 'Person':
        return parse_person
    elif schema_type == 'Place':
        return parse_place


def parse(microdata: List[Dict]) -> Optional[Dict]:
    data = next(
        filter(lambda x: x['type'] == 'http://schema.org/Person', microdata), None
    )
    if not data:
        return

    result = {}
    for key, val in data['properties'].items():
        if isinstance(val, List):
            val = _parse_list(val)
        elif isinstance(val, Dict):
            val = _parse_dict(val)

        if val:
            result[key] = val
    return result


def _parse_list(data: List) -> List:
    return list(filter(None, [_parse_dict(val) for val in data]))


def _parse_dict(data: Dict) -> Any:
    match = re_schema.match(data['type'])
    if not match:
        return

    parser = get_parser(match.group(1))
    if parser:
        return parser(data)


def _parse_url(data: str) -> str:
    match = re_url.match(data)
    if match:
        return 'https://www.genealogieonline.nl/bismeijer-family/{}.php'.format(
            match.group(2).upper()
        )
    return ''
