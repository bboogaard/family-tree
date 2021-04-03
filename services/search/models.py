from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchNameRequest:
    name: str


@dataclass
class SearchTextRequest:
    text: str


@dataclass
class SearchAncestorRequest:
    has_children: Optional[bool] = None
    lastname: Optional[str] = ''
    birthyear_from: Optional[int] = None
    birthyear_to: Optional[int] = None


@dataclass
class EmptySearchRequest:
    pass
