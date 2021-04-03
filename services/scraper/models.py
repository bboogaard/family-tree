from dataclasses import dataclass
from typing import Dict, List, Optional

from dacite import from_dict

from lib.dataclasses import from_camel_keys
from services.scraper.md_parser import parse


@dataclass
class TreeScraperResult:
    url: str
    given_name: str
    family_name: str
    gender: Optional[str] = ''
    birth_date: Optional[str] = ''
    birth_place: Optional[str] = ''
    death_date: Optional[str] = ''
    death_place: Optional[str] = ''
    parent: Optional[List['TreeScraperResult']] = None
    spouse: Optional[List['TreeScraperResult']] = None
    children: Optional[List['TreeScraperResult']] = None

    @classmethod
    def from_microdata(cls, microdata: List[Dict]) -> 'TreeScraperResult':
        data = parse(microdata)
        parent = data.pop('parent', None)
        if parent:
            if not isinstance(parent, List):
                parent = [parent]
            parent = list(map(from_camel_keys, parent))
        spouse = data.pop('spouse', None)
        if spouse:
            if not isinstance(spouse, List):
                spouse = [spouse]
            spouse = list(map(from_camel_keys, spouse))
        children = data.pop('children', None)
        if children:
            if not isinstance(children, List):
                children = [children]
            children = list(map(from_camel_keys, children))
        data.update({
            'parent': parent,
            'spouse': spouse,
            'children': children
        })
        return from_dict(cls, from_camel_keys(data))


@dataclass
class ScraperResult:
    tree: TreeScraperResult
    bio: str
