import datetime
import random

import factory

from tree import models


class AncestorFactory(factory.django.DjangoModelFactory):

    birthdate = factory.Faker(
        'date_between_dates',
        date_start=datetime.date(1800, 1, 1),
        date_end=datetime.date(1950, 1, 1)
    )

    birthyear = factory.LazyAttribute(lambda obj: random.randrange(1800, 1951))

    birthplace = factory.Faker('city')

    date_of_death = factory.Faker(
        'date_between_dates',
        date_start=datetime.date(1850, 12, 31),
        date_end=datetime.date(2000, 12, 31)
    )

    gender = factory.LazyAttribute(lambda obj: random.choice(['m', 'f']))

    has_expired = True

    lastname = factory.Faker('last_name')

    place_of_death = factory.Faker('city')

    year_of_death = factory.LazyAttribute(
        lambda obj: random.randrange(1950, 2001)
    )

    class Meta:
        model = models.Ancestor

    @factory.post_generation
    def firstname(self, create, extracted, **kwargs):
        if not create:
            return

        if not extracted:
            return

        if self.gender == 'f':
            try:
                self.christian_name = models.ChristianName.objects.get(
                    name_type='f',
                    female_name=extracted
                )
            except models.ChristianName.DoesNotExist:
                self.christian_name = models.ChristianName(
                    name_type='f',
                    female_name=extracted
                )
                self.christian_name.full_clean()
                self.christian_name.save()
        elif self.gender == 'm':
            try:
                self.christian_name = models.ChristianName.objects.get(
                    name_type='m',
                    male_name=extracted
                )
            except models.ChristianName.DoesNotExist:
                self.christian_name = models.ChristianName(
                    name_type='m',
                    male_name=extracted
                )
                self.christian_name.full_clean()
                self.christian_name.save()


class MarriageFactory(factory.django.DjangoModelFactory):

    husband = factory.SubFactory(AncestorFactory, gender='m')

    wife = factory.SubFactory(AncestorFactory, gender='f')

    date_of_marriage = factory.Faker(
        'date_between_dates',
        date_start=datetime.date(1810, 1, 1),
        date_end=datetime.date(1940, 1, 1)
    )

    place_of_marriage = factory.Faker('city')

    class Meta:
        model = models.Marriage


class LineageFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Lineage

    ancestor = factory.SubFactory(AncestorFactory, gender='m')

    descendant = factory.SubFactory(AncestorFactory)


class BioFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Bio

    @factory.post_generation
    def links(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for url, link_text in extracted:
            self.links.create(url=url, link_text=link_text)
