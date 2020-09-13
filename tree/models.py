"""
Models for the tree app.

"""
from django.db import models


class Ancestor(models.Model):
    """Model for the ancestor data."""

    birthdate = models.DateField('Geboortedatum', null=True, blank=True)

    birthplace = models.CharField('Geboorteplaats', max_length=100, blank=True)

    date_of_death = models.DateField('Overlijdensdatum', null=True, blank=True)

    details = models.TextField('Details', blank=True)

    father = models.ForeignKey(
        'self', related_name='children_of_father', on_delete=models.PROTECT,
        verbose_name='Vader', null=True, blank=True)

    firstname = models.CharField('Voornaam', max_length=100, blank=True)

    gender = models.CharField(max_length=1, choices=[
        ('m', 'Man'),
        ('f', 'Vrouw')
    ], blank=True)

    lastname = models.CharField('Achternaam', max_length=100, blank=True)

    middlename = models.CharField('Tussenvoegsel', max_length=100, blank=True)

    mother = models.ForeignKey(
        'self', related_name='children_of_mother', on_delete=models.PROTECT,
        verbose_name='Moeder', null=True, blank=True)

    place_of_death = models.CharField(
        'Plaats van overlijden', max_length=100, blank=True)

    class Meta:
        ordering = ['birthdate']
        verbose_name = 'Voorouder'
        verbose_name_plural = 'Voorouders'

    def __str__(self):
        parts = filter(None, [
            self.firstname,
            self.middlename,
            self.lastname
        ])
        return ' '.join(parts)


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
