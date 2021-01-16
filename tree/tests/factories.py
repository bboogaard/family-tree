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

    firstname = factory.Faker('first_name')

    gender = factory.LazyAttribute(lambda obj: random.choice(['m', 'f']))

    has_expired = True

    lastname = factory.Faker('last_name')

    place_of_death = factory.Faker('city')

    year_of_death = factory.LazyAttribute(
        lambda obj: random.randrange(1950, 2001)
    )

    class Meta:
        model = models.Ancestor


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
