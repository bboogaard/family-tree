"""
Base scraper class.

"""
import datetime
from abc import ABC
from typing import List, Optional, Tuple

import requests
from dacite import from_dict
from dataclasses import asdict
from django.conf import settings
from django.db import transaction
from extruct.w3cmicrodata import MicrodataExtractor
from pyquery import PyQuery

from scraper.models import Page
from services.scraper.models import ScraperResult, TreeScraperResult
from tree.models import Ancestor, Bio, BioLink, ChristianName


class ScraperService(ABC):

    _page: Page

    _depth: int

    _direction: str

    @transaction.atomic()
    def find(self, page: Page, depth: Optional[int] = 1,
             direction: str = settings.SCRAPE_DIRECTION_DOWN):
        self._page = self._get_or_create_page(page.url)
        self._depth = depth
        self._direction = direction
        self._find(self._page)

    def _find(self, page: Page, level: int = 0):
        if not page.processed:
            return

        print("Scraping {}".format(page.url))
        result = from_dict(TreeScraperResult, page.tree_data)

        parents = self._create_related_pages(result.parent)
        if self._direction == settings.SCRAPE_DIRECTION_UP:
            self._find_recursive(parents, level)
        father = self._get_related_ancestor(parents, 'm')
        mother = self._get_related_ancestor(parents, 'f')

        spouses = self._create_related_pages(result.spouse)
        self._find_recursive(spouses, level)
        husband = self._get_related_ancestor(spouses, 'm')
        wife = self._get_related_ancestor(spouses, 'f')

        children = self._create_related_pages(result.children)
        if self._direction == settings.SCRAPE_DIRECTION_DOWN:
            self._find_recursive(children, level)

        if ancestor := page.ancestor:
            self._update_ancestor(ancestor, father, mother, husband, wife)

    def _find_recursive(self, pages: Optional[List[Page]], level: int):
        if not pages or level >= self._depth:
            return

        for page in pages:
            self._find(page, level + 1)

    def _get_or_create_ancestor(self, page: Page) -> Ancestor:
        result = from_dict(TreeScraperResult, page.tree_data)

        gender = 'f' if result.gender == 'female' else 'm'
        christian_name = ChristianName.objects.get_or_create_name(
            result.given_name, gender)
        birthdate, birthyear = self._parse_date_and_year(result.birth_date)
        date_of_death, year_of_death = self._parse_date_and_year(result.death_date)
        slug = Ancestor.generate_slug(
            firstname=str(christian_name),
            middlename='',
            lastname=result.family_name,
            birthyear=birthyear,
            year_of_death=year_of_death,
            has_expired=True
        )

        try:
            ancestor = Ancestor.objects.get_by_natural_key(slug)
        except Ancestor.DoesNotExist:
            ancestor = Ancestor(
                christian_name=christian_name,
                lastname=result.family_name,
                gender=gender,
                birthplace=result.birth_place,
                birthdate=birthdate,
                birthyear=birthyear,
                place_of_death=result.death_place,
                date_of_death=date_of_death,
                year_of_death=year_of_death,
                has_expired=True,
                slug=slug
            )
            ancestor.full_clean()
            ancestor.save()

        try:
            bio = Bio.objects.get(ancestor=ancestor)
        except Bio.DoesNotExist:
            bio = Bio(
                ancestor=ancestor,
                details=page.bio_data
            )
            bio.save()

        try:
            bio.links.get(url=page.url)
        except BioLink.DoesNotExist:
            bio_link = BioLink(
                bio=bio,
                url=page.url,
                link_text='Genealogie Online'
            )
            bio_link.save()

        return ancestor

    def _create_related_pages(self, result: List[TreeScraperResult]) -> Optional[List[Page]]:
        if not result:
            return

        related_pages = []
        for res in result:
            if (page := self._get_or_create_page(res.url)).processed:
                related_pages.append(page)
        return related_pages

    def _get_or_create_page(self, url: str) -> Page:
        is_dirty = False
        try:
            page = Page.objects.get(url=url)
        except Page.DoesNotExist:
            page = Page(url=url)
            is_dirty = True

        if not page.processed:
            result = self._scrape(page)
            if result:
                page.processed = True
                page.name = result.tree.given_name + ' ' + result.tree.family_name
                page.tree_data = asdict(result.tree)
                page.bio_data = result.bio
                if not is_dirty:
                    is_dirty = True

        if page.processed:
            ancestor = self._get_or_create_ancestor(page)
            if not Page.objects.filter(ancestor=ancestor).exists():
                page.ancestor = ancestor
                if not is_dirty:
                    is_dirty = True

        if is_dirty:
            page.save()
        return page

    @staticmethod
    def _scrape(page: Page) -> Optional[ScraperResult]:
        try:
            response = requests.get(page.url)
            if response.status_code != 200:
                response.raise_for_status()
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            return

        mde = MicrodataExtractor()
        microdata = mde.extract(response.content)
        doc = PyQuery(response.content)
        try:
            bio = PyQuery(doc.find('ul.nicelist')[0]).text()
        except (IndexError, TypeError):
            bio = ''
        return ScraperResult(
            tree=TreeScraperResult.from_microdata(microdata),
            bio=bio
        )

    @staticmethod
    def _parse_date_and_year(date_string: str) -> Tuple[Optional[datetime.date], Optional[int]]:
        try:
            date = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()
        except ValueError:
            date = None
        if date:
            year = date.year
        else:
            try:
                year = int(date_string)
            except ValueError:
                year = None
        return date, year

    @staticmethod
    def _get_related_ancestor(pages: Optional[List[Page]], gender: str) -> Optional[Ancestor]:
        if not pages:
            return

        page = next(filter(lambda p: p.ancestor and getattr(p.ancestor, 'gender') == gender, pages), None)
        return page.ancestor if page else None

    @staticmethod
    def _update_ancestor(ancestor: Ancestor, father: Optional[Ancestor], mother: Optional[Ancestor],
                         husband: Optional[Ancestor], wife: Optional[Ancestor]):
        is_dirty = False
        if father:
            ancestor.father = father
            is_dirty = True
        if mother:
            ancestor.mother = mother
            if not is_dirty:
                is_dirty = True
        if is_dirty:
            ancestor.save()

        if husband:
            if not ancestor.marriages_of_wife.filter(husband=husband).exists():
                ancestor.marriages_of_wife.create(husband=husband)
        if wife:
            if not ancestor.marriages_of_husband.filter(wife=wife).exists():
                ancestor.marriages_of_husband.create(wife=wife)
