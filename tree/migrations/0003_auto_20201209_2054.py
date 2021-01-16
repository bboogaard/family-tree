# Generated by Django 3.1.1 on 2020-12-09 20:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tree', '0002_auto_20201205_1810'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('details', models.TextField(blank=True, verbose_name='Details')),
            ],
            options={
                'verbose_name': 'Persoonlijke gegevens',
                'verbose_name_plural': 'Persoonlijke gegevens',
            },
        ),
        migrations.RemoveField(
            model_name='ancestor',
            name='details',
        ),
        migrations.CreateModel(
            name='BioLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link_text', models.CharField(max_length=100, verbose_name='Link text')),
                ('url', models.URLField(verbose_name='Url')),
                ('bio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='tree.bio', verbose_name='Bio')),
            ],
            options={
                'verbose_name': 'Link',
                'verbose_name_plural': 'Links',
            },
        ),
        migrations.AddField(
            model_name='bio',
            name='ancestor',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bio', to='tree.ancestor', verbose_name='Voorouder'),
        ),
    ]