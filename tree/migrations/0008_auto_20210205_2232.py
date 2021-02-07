# Generated by Django 3.1.1 on 2021-02-05 22:32

import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tree', '0007_namengram'),
    ]

    operations = [
        migrations.AddField(
            model_name='ancestor',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(blank=True, null=True, verbose_name='Search vector'),
        ),
        migrations.AddField(
            model_name='bio',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(blank=True, null=True, verbose_name='Search vector'),
        ),
        migrations.AddField(
            model_name='biolink',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(blank=True, null=True, verbose_name='Search vector'),
        ),
        migrations.AddField(
            model_name='christianname',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(blank=True, null=True, verbose_name='Search vector'),
        ),
        migrations.AddField(
            model_name='marriage',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(blank=True, null=True, verbose_name='Search vector'),
        ),
    ]
