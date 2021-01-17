"""
Models for the tree app.

"""
from django.db import models, transaction
from django.db.models import CharField, Exists, OuterRef, Prefetch, Q, \
    Value as V, When
from django.db.models.functions import Cast, Concat
from django.db.models.signals import post_save
from django.utils.text import slugify


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

    def with_children(self):
        queryset = self._clone()

        queryset = (
            queryset.filter(
                Exists(
                    self.model.objects
                    .filter(
                        Q(father=OuterRef('pk')) | Q(mother=OuterRef('pk'))
                    )
                )
            )
        )

        return queryset

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

    def order_by_age(self):
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
            .order_by('age')
        )


class Ancestor(models.Model):
    """Model for the ancestor data."""

    birthdate = models.DateField('Geboortedatum', null=True, blank=True)

    birthyear = models.IntegerField('Geboortejaar', null=True, blank=True)

    birthplace = models.CharField('Geboorteplaats', max_length=100, blank=True)

    date_of_death = models.DateField('Overlijdensdatum', null=True, blank=True)

    father = models.ForeignKey(
        'self', related_name='children_of_father', on_delete=models.CASCADE,
        verbose_name='Vader', null=True, blank=True,
        limit_choices_to=models.Q(gender='m'))

    firstname = models.CharField('Voornaam', max_length=100, blank=True)

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
                parts = [self.get_fullname(), self.get_age('xxxx')]
                if serial:
                    parts.append(str(serial))
                slug = slugify(' '.join(parts))
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

    def get_fullname(self):
        parts = filter(None, [
            self.firstname,
            self.middlename,
            self.lastname
        ])
        return ' '.join(parts)
    get_fullname.short_description = 'Naam'

    def get_age(self, placeholder='????'):
        if self.birthyear and self.year_of_death:
            parts = [
                self.birthyear,
                self.year_of_death
            ]
        elif self.birthyear:
            parts = [self.birthyear, placeholder if self.has_expired else '']
        elif self.year_of_death:
            parts = [placeholder, self.year_of_death]
        else:
            parts = [placeholder, placeholder if self.has_expired else '']

        return ' - '.join(map(str, parts)).rstrip()
    get_age.short_description = 'Geboorte/sterftejaar'

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


class Bio(models.Model):
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


class BioLink(models.Model):
    """Model for links to biographical info."""

    bio = models.ForeignKey(
        Bio,
        related_name='links',
        on_delete=models.CASCADE,
        verbose_name='Bio'
    )

    link_text = models.CharField('Link text', max_length=100)

    url = models.URLField('Url')

    class Meta:
        verbose_name = 'Link'
        verbose_name_plural = 'Links'

    def __str__(self):
        return self.link_text


class Marriage(models.Model):
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

        candidates = [ancestor.pk]
        if ancestor.gender == 'm':
            for marriage in ancestor.marriages_of_husband.all():
                candidates.append(marriage.wife_id)
        elif ancestor.gender == 'f':
            for marriage in ancestor.marriages_of_wife.all():
                candidates.append(marriage.husband_id)

        for generation in generations:
            siblings = generation.ancestor.father.children.all()
            for child in siblings:
                candidates.append(child.pk)
                if child.gender == 'm':
                    for marriage in child.marriages_of_husband.all():
                        candidates.append(marriage.wife_id)
                elif child.gender == 'f':
                    for marriage in child.marriages_of_wife.all():
                        candidates.append(marriage.husband_id)

        return queryset.filter(ancestor__in=candidates)


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
