# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields.encrypted


class Migration(migrations.Migration):

    dependencies = [
        ('djbraintree', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='pin',
            field=django_extensions.db.fields.encrypted.EncryptedCharField(max_length=100, null=True, blank=True),
        ),
    ]
