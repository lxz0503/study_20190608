# Generated by Django 2.2.5 on 2020-02-22 11:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0003_auto_20200222_1855'),
    ]

    operations = [
        migrations.RenameField(
            model_name='courseorg',
            old_name='category_2',
            new_name='category',
        ),
    ]