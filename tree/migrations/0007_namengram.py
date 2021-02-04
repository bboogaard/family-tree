# Generated by Django 3.1.1 on 2021-02-03 21:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tree', '0006_remove_ancestor_firstname'),
    ]

    operations = [
        migrations.CreateModel(
            name='NameNGram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_query', models.CharField(max_length=100, verbose_name='Zoektekst')),
                ('score', models.PositiveIntegerField(verbose_name='Score')),
                ('christian_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ngrams', to='tree.christianname', verbose_name='Doopnaam')),
            ],
            options={
                'ordering': ['-score'],
                'unique_together': {('search_query', 'christian_name')},
            },
        ),
    ]