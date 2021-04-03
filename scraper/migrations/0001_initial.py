# Generated by Django 3.1.1 on 2021-03-19 20:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tree', '0008_auto_20210205_2232'),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(unique=True, verbose_name='URL')),
                ('name', models.CharField(blank=True, max_length=100, verbose_name='Naam')),
                ('tree_data', models.JSONField(blank=True, null=True, verbose_name='Tree data')),
                ('bio_data', models.TextField(blank=True, verbose_name='Bio data')),
                ('processed', models.BooleanField(default=False, verbose_name='Verwerkt')),
                ('ancestor', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='page', to='tree.ancestor', verbose_name='Voorouder')),
            ],
            options={
                'verbose_name': 'Pagina',
                'verbose_name_plural': "Pagina's",
            },
        ),
    ]
