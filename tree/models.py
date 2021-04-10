"""
Models for the tree app.

"""
from django.contrib.postgres.search import SearchVectorField
from django.db import models, transaction
from django.db.models import CharField, Exists, OuterRef, Prefetch, Q, \
    Value as V, When
from django.db.models.functions import Cast, Concat
from django.db.models.signals import post_save
from django.utils.text import slugify

from lib.cache.decorators import cache_method_result
from lib.search.search_vectors import register_search_vector


class SearchVectorModel(models.Model):

    search_vector = SearchVectorField('Search vector', null=True, blank=True)

    class Meta:
        abstract = True


class AncestorQuerySet(models.QuerySet):
    """Custom QuerySet for the Ancestor model."""

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def by_parent(self, parent):
        queryset = self._clone()

        if parent.gender == 'm':
            queryset = queryset.filter(father=parent)
        elif parent.gender == 'f':
            queryset = queryset.filter(mother=parent)

        return queryset

    def with_has_children(self):
        queryset = self._clone()

        queryset = (
            queryset.annotate(
                has_children=Exists(
                    self.model.objects
                    .filter(
                        Q(father=OuterRef('pk')) | Q(mother=OuterRef('pk'))
                    )
                )
            )
        )

        return queryset

    def with_children(self):
        queryset = self._clone()

        return queryset.with_has_children().filter(has_children=True)

    def with_marriages(self):
        queryset = self._clone()

        queryset = (
            queryset.prefetch_related(
                Prefetch(
                    'marriages_of_husband',
                    queryset=Marriage.objects.select_related(
                        'wife'
                    )
                ),
                Prefetch(
                    'marriages_of_wife',
                    queryset=Marriage.objects.select_related(
                        'husband'
                    )
                )
            )
        )

        return queryset

    def with_age(self):
        queryset = self._clone()

        return (
            queryset
            .annotate(
                birthyear_as_str=Cast('birthyear', output_field=CharField()),
                year_of_death_as_str=Cast(
                    'year_of_death', output_field=CharField()
                )
            )
            .annotate(
                age=models.Case(
                    When(
                        Q(
                            birthyear__isnull=False,
                            year_of_death__isnull=False
                        ),
                        then=Concat(
                            'birthyear_as_str', V(' - '),
                            'year_of_death_as_str'
                        )
                    ),
                    When(
                        Q(
                            birthyear__isnull=False,
                            has_expired=True
                        ),
                        then=Concat(
                            'birthyear_as_str', V(' - '), V('0000')
                        )
                    ),
                    When(
                        Q(
                            birthyear__isnull=False,
                            has_expired=False
                        ),
                        then=Concat(
                            'birthyear_as_str', V(' -')
                        )
                    ),
                    When(
                        year_of_death__isnull=False,
                        then=Concat(
                            V('0000'), V(' - '), 'year_of_death_as_str'
                        )
                    ),
                    When(
                        has_expired=True,
                        then=Concat(
                            V('0000'), V(' - '), V('0000')
                        )
                    ),
                    output_field=CharField()
                )
            )
        )

    def order_by_age(self):
        queryset = self._clone()
        return queryset.with_age().order_by('age')


class ChristianNameQuerySet(models.QuerySet):

    def get_or_create_name(self, name, gender):
        kwarg = 'female_name' if gender == 'f' else 'male_name'
        christian_name = self.filter(**{
            '{}__iexact'.format(kwarg): name
        }).first()
        if not christian_name:
            christian_name = self.create(**{
                kwarg: name,
                'name': name,
                'name_type': gender
            })
        return christian_name


class ChristianName(SearchVectorModel):
    """Model for first (christian) names."""

    alias_for = models.ForeignKey(
        'self',
        related_name='aliases',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    female_name = models.CharField(
        'Meisjesnaam', max_length=100, null=True, blank=True
    )

    male_name = models.CharField(
        'Jongensnaam', max_length=100, null=True, blank=True
    )

    name = models.CharField('Naam', max_length=201, blank=True)

    name_type = models.CharField('Soort naam', max_length=1, choices=[
        ('b', 'Jongens- en meisjesnaam'),
        ('f', 'Meisjesnaam'),
        ('m', 'Jongensnaam'),
    ])

    objects = ChristianNameQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name_type', 'female_name', 'male_name'],
                name="Unique constraint for boy's and girl's name",
                condition=models.Q(
                    name_type='b',
                    female_name__isnull=False,
                    male_name__isnull=False
                )
            ),
            models.UniqueConstraint(
                fields=['name_type', 'female_name', 'male_name'],
                name="Unique constraint for girl's name",
                condition=models.Q(
                    name_type='f',
                    female_name__isnull=False,
                    male_name__isnull=True
                )
            ),
            models.UniqueConstraint(
                fields=['name_type', 'female_name', 'male_name'],
                name="Unique constraint for boy's name",
                condition=models.Q(
                    name_type='m',
                    female_name__isnull=True,
                    male_name__isnull=False
                )
            )
        ]
        ordering = ['name']
        verbose_name = 'Doopnaam'
        verbose_name_plural = 'Doopnamen'

    def __str__(self):
        return self.name

    def clean(self):
        self.name = '/'.join(filter(None, [self.male_name, self.female_name]))

    def get_gender_name(self, gender):
        if gender == 'f':
            result = self.female_name
        elif gender == 'm':
            result = self.male_name
        else:
            result = None

        return result if result is not None else ''


register_search_vector(ChristianName, ['name'], ['ancestors'])


class NameNGram(models.Model):
    """NGram search cache for christian names."""

    search_query = models.CharField('Zoektekst', max_length=100)

    score = models.PositiveIntegerField('Score')

    christian_name = models.ForeignKey(
        ChristianName,
        on_delete=models.CASCADE,
        related_name='ngrams',
        verbose_name='Doopnaam'
    )

    class Meta:
        ordering = ['-score']
        unique_together = ['search_query', 'christian_name']

    def __str__(self):
        return self.search_query


class Ancestor(SearchVectorModel):
    """Model for the ancestor data."""

    birthdate = models.DateField('Geboortedatum', null=True, blank=True)

    birthyear = models.IntegerField('Geboortejaar', null=True, blank=True)

    birthplace = models.CharField('Geboorteplaats', max_length=100, blank=True)

    christian_name = models.ForeignKey(
        ChristianName,
        related_name='ancestors',
        on_delete=models.PROTECT,
        verbose_name='Doopnaam',
        null=True,
        blank=True
    )

    date_of_death = models.DateField('Overlijdensdatum', null=True, blank=True)

    father = models.ForeignKey(
        'self', related_name='children_of_father', on_delete=models.CASCADE,
        verbose_name='Vader', null=True, blank=True,
        limit_choices_to=models.Q(gender='m'))

    gender = models.CharField(max_length=1, choices=[
        ('m', 'Man'),
        ('f', 'Vrouw')
    ], blank=True)

    has_expired = models.BooleanField('Overleden', default=False)

    is_root = models.BooleanField('Begin stamboom', default=False)

    lastname = models.CharField('Achternaam', max_length=100, blank=True)

    middlename = models.CharField('Tussenvoegsel', max_length=100, blank=True)

    mother = models.ForeignKey(
        'self', related_name='children_of_mother', on_delete=models.CASCADE,
        verbose_name='Moeder', null=True, blank=True,
        limit_choices_to=models.Q(gender='f'))

    place_of_death = models.CharField(
        'Plaats van overlijden', max_length=100, blank=True)

    slug = models.SlugField('Slug', max_length=255, blank=True, db_index=True)

    year_of_death = models.IntegerField(
        'Jaar van overlijden', null=True, blank=True)

    objects = AncestorQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['is_root'], name='is_root_true',
                condition=models.Q(is_root=True)
            )
        ]
        indexes = [models.Index(fields=['middlename', 'lastname'])]
        ordering = ['birthdate']
        verbose_name = 'Voorouder'
        verbose_name_plural = 'Voorouders'

    def __str__(self):
        return ' '.join(filter(None, [self.get_fullname(), self.get_age()]))

    def clean(self):
        if self.year_of_death:
            self.has_expired = True

        if not self.slug:
            serial = 0
            while True:
                slug = self.generate_slug(
                    self.firstname,
                    self.middlename,
                    self.lastname,
                    self.birthyear,
                    self.year_of_death,
                    self.has_expired,
                    serial
                )
                if len(slug) > 255:
                    slug = '-'.join(filter(lambda s: s != '0', [
                        slug[:255 - (len(str(serial)) + 1 if serial else 0)],
                        str(serial)
                    ]))
                try:
                    queryset = self.__class__.objects.get_queryset()
                    if self.pk:
                        queryset = queryset.exclude(pk=self.pk)
                    queryset.get_by_natural_key(slug)
                    serial += 1
                except self.__class__.DoesNotExist:
                    break
            self.slug = slug

    def natural_key(self):
        return (self.slug, )

    @cache_method_result(key='ancestor-firstname', key_attrs=['pk'], timeout=24 * 60 * 60)
    def _get_firstname(self):
        if not self.christian_name:
            return ''

        return self.christian_name.get_gender_name(self.gender)

    firstname = property(_get_firstname)

    def get_fullname(self):
        return self.generate_fullname(
            self.firstname, self.middlename, self.lastname
        )
    get_fullname.short_description = 'Naam'

    @staticmethod
    def generate_fullname(firstname, middlename, lastname):
        parts = filter(None, [
            firstname,
            middlename,
            lastname
        ])
        return ' '.join(map(str, parts))

    def get_age(self, placeholder='????'):
        return self.generate_age(
            self.birthyear, self.year_of_death, self.has_expired, placeholder
        )
    get_age.short_description = 'Geboorte/sterftejaar'

    @staticmethod
    def generate_age(birthyear, year_of_death, has_expired, placeholder='????'):
        if birthyear and year_of_death:
            parts = [birthyear, year_of_death]
        elif birthyear:
            parts = [birthyear, placeholder if has_expired else '']
        elif year_of_death:
            parts = [placeholder, year_of_death]
        else:
            parts = [placeholder, placeholder if has_expired else '']

        return ' - '.join(map(str, parts)).rstrip()

    @staticmethod
    def generate_slug(firstname, middlename, lastname, birthyear, year_of_death, has_expired, serial=0):
        parts = [
            Ancestor.generate_fullname(firstname, middlename, lastname),
            Ancestor.generate_age(birthyear, year_of_death, has_expired, placeholder='xxxx'),
        ]
        if serial:
            parts.append(str(serial))
        return slugify(' '.join(parts))

    @property
    def was_married(self):
        if self.gender == 'm':
            return self.marriages_of_husband.count() > 0
        elif self.gender == 'f':
            return self.marriages_of_wife.count() > 0

        return False

    @property
    def children(self):
        if self.gender == 'm':
            return self.children_of_father
        elif self.gender == 'f':
            return self.children_of_mother

        return Ancestor.objects.none()

    @property
    def marriages(self):
        if self.gender == 'm':
            return self.marriages_of_husband
        elif self.gender == 'f':
            return self.marriages_of_wife

        return Marriage.objects.none()

    def get_spouse(self, marriage):
        if self.gender == 'm':
            return marriage.wife
        elif self.gender == 'f':
            return marriage.husband

        return None

    def get_lineage(self):
        try:
            return (
                Lineage.objects
                .select_related('descendant')
                .get(ancestor=self)
            )
        except Lineage.DoesNotExist:
            pass

    def get_bio(self):
        try:
            return (
                Bio.objects
                .select_related('ancestor')
                .get(ancestor=self)
            )
        except Bio.DoesNotExist:
            pass


register_search_vector(
    Ancestor, ['middlename', 'lastname', 'birthplace', 'place_of_death']
)


class Bio(SearchVectorModel):
    """Model for biographical info."""

    ancestor = models.OneToOneField(
        Ancestor,
        related_name='bio',
        on_delete=models.CASCADE,
        verbose_name='Voorouder'
    )

    details = models.TextField('Details', blank=True)

    class Meta:
        verbose_name = 'Persoonlijke gegevens'
        verbose_name_plural = 'Persoonlijke gegevens'

    def __str__(self):
        return 'Persoonlijke gegevens {}'.format(str(self.ancestor))

    @property
    def rendered_details(self):
        from .helpers import get_bio_details
        details = get_bio_details(self)
        return ', '.join(
            [': '.join(detail)
             if detail[0] else detail[1] for detail in details]
        )


register_search_vector(Bio, ['details'], ['ancestor'])


class BioLink(SearchVectorModel):
    """Model for links to biographical info."""

    bio = models.ForeignKey(
        Bio,
        related_name='links',
        on_delete=models.CASCADE,
        verbose_name='Bio'
    )

    link_text = models.CharField('Link text', max_length=100)

    url = models.URLField('Url', unique=True)

    class Meta:
        verbose_name = 'Link'
        verbose_name_plural = 'Links'

    def __str__(self):
        return self.link_text


register_search_vector(BioLink, ['link_text', 'url'], ['bio__ancestor'])


class Marriage(SearchVectorModel):
    """Model for the marriage data."""

    husband = models.ForeignKey(
        Ancestor,
        on_delete=models.CASCADE,
        related_name='marriages_of_husband',
        limit_choices_to=models.Q(gender='m'),
        verbose_name='Man'
    )

    wife = models.ForeignKey(
        Ancestor,
        on_delete=models.CASCADE,
        related_name='marriages_of_wife',
        limit_choices_to=models.Q(gender='f'),
        verbose_name='Vrouw'
    )

    date_of_divorce = models.DateField(
        'Scheidingsdatum', null=True, blank=True)

    date_of_marriage = models.DateField('Trouwdatum', null=True, blank=True)

    place_of_marriage = models.CharField(
        'Plaats van trouwen', max_length=100, blank=True)

    class Meta:
        ordering = ['date_of_marriage']
        verbose_name = 'Huwelijk'
        verbose_name_plural = 'Huwelijken'

    def __str__(self):
        return '{} x {}'.format(str(self.husband), str(self.wife))


register_search_vector(
    Marriage, ['place_of_marriage'], ['husband', 'wife']
)


class LineageQuerySet(models.QuerySet):
    """Custom QuerySet for the Lineage model."""

    def for_ancestor(self, ancestor):
        queryset = self._clone()

        generations = (
            Generation.objects
            .filter(lineage__ancestor=ancestor)
            .select_related(
                'ancestor__father'
            )
            .prefetch_related(
                'ancestor__father__children_of_father__marriages_of_husband',
                'ancestor__father__children_of_father__marriages_of_wife',
            )
        )
        descendants = [
            generation.ancestor for generation in generations.all()
        ]
        candidates = self._get_candidates(ancestor, descendants)

        return queryset.filter(ancestor__in=candidates)

    def for_ancestor_and_descendants(self, ancestor, descendants):
        queryset = self._clone()
        candidates = self._get_candidates(ancestor, descendants)
        return queryset.filter(ancestor__in=candidates)

    @staticmethod
    def _get_candidates(ancestor, descendants):
        candidates = [ancestor.pk]

        if ancestor.gender == 'm':
            for marriage in ancestor.marriages_of_husband.all():
                candidates.append(marriage.wife_id)
        elif ancestor.gender == 'f':
            for marriage in ancestor.marriages_of_wife.all():
                candidates.append(marriage.husband_id)

        for descendant in descendants:
            siblings = descendant.father.children.all()
            for child in siblings:
                candidates.append(child.pk)
                if child.gender == 'm':
                    for marriage in child.marriages_of_husband.all():
                        candidates.append(marriage.wife_id)
                elif child.gender == 'f':
                    for marriage in child.marriages_of_wife.all():
                        candidates.append(marriage.husband_id)

        return candidates


class Lineage(models.Model):
    """Model for lineage data."""

    ancestor = models.OneToOneField(
        Ancestor,
        on_delete=models.CASCADE,
        related_name='lineage',
        verbose_name='Voorouder'
    )

    descendant = models.ForeignKey(
        Ancestor,
        on_delete=models.CASCADE,
        related_name='lineages',
        verbose_name='Nakomeling'
    )

    objects = LineageQuerySet.as_manager()

    class Meta:
        unique_together = ['ancestor', 'descendant']
        verbose_name = 'Afstamming'
        verbose_name_plural = 'Afstammingen'

    def __str__(self):
        return '{} > {}'.format(str(self.ancestor), str(self.descendant))


class GenerationManager(models.Manager):
    """Custom manager for the Generation model."""

    @transaction.atomic()
    def build_generations(self, sender, **kwargs):
        from tree.helpers import build_lineage

        lineage = kwargs.get('instance')
        lineage.generations.all().delete()
        generations = build_lineage(lineage)
        generation_objects = [
            self.model(
                lineage=lineage, ancestor=ancestor, generation=generation
            )
            for ancestor, generation in generations
        ]
        self.bulk_create(generation_objects)


class Generation(models.Model):
    """Contains intermediate generations within a lineage.

    Note that this is filled by the app.

    """

    lineage = models.ForeignKey(
        Lineage,
        on_delete=models.CASCADE,
        related_name='generations',
        verbose_name='Afstamming'
    )

    ancestor = models.ForeignKey(
        Ancestor,
        on_delete=models.CASCADE,
        related_name='generations',
        verbose_name='Voorouder'
    )

    generation = models.IntegerField('Generatie')

    objects = GenerationManager()

    class Meta:
        indexes = [models.Index(fields=['lineage', 'generation'])]
        ordering = ['lineage', 'generation']
        unique_together = ['lineage', 'ancestor']
        verbose_name = 'Generatie'
        verbose_name_plural = 'Generaties'

    def __str__(self):
        return '{} ({})'.format(str(self.lineage), str(self.generation))


post_save.connect(Generation.objects.build_generations, sender=Lineage)
