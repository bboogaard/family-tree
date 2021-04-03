from django.db import models


class Page(models.Model):
    """Contains links to pages to be scraped."""

    url = models.URLField('URL', unique=True)

    ancestor = models.OneToOneField(
        'tree.Ancestor',
        on_delete=models.CASCADE,
        related_name='page',
        verbose_name='Voorouder',
        null=True,
        blank=True
    )

    name = models.CharField('Naam', max_length=100, blank=True)

    tree_data = models.JSONField('Tree data', null=True, blank=True)

    bio_data = models.TextField('Bio data', blank=True)

    processed = models.BooleanField('Verwerkt', default=False)

    class Meta:
        verbose_name = 'Pagina'
        verbose_name_plural = "Pagina's"

    def __str__(self):
        return self.name
