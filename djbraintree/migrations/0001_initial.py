# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import model_utils.fields
import django_extensions.db.fields.encrypted
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrentSubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('plan', models.CharField(max_length=100)),
                ('quantity', models.IntegerField()),
                ('start', models.DateTimeField()),
                ('status', models.CharField(max_length=25)),
                ('cancel_at_period_end', models.BooleanField(default=False)),
                ('canceled_at', models.DateTimeField(null=True, blank=True)),
                ('current_period_end', models.DateTimeField(null=True)),
                ('current_period_start', models.DateTimeField(null=True)),
                ('ended_at', models.DateTimeField(null=True, blank=True)),
                ('trial_end', models.DateTimeField(null=True, blank=True)),
                ('trial_start', models.DateTimeField(null=True, blank=True)),
                ('amount', models.DecimalField(max_digits=7, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('braintree_id', models.CharField(max_length=50)),
                ('token', models.CharField(max_length=100, null=True, blank=True)),
                ('refresh_token', models.CharField(max_length=100, null=True, blank=True)),
                ('pin', django_extensions.db.fields.encrypted.EncryptedCharField(max_length=364, null=True, blank=True)),
                ('funds_source', models.CharField(max_length=50, null=True, blank=True)),
                ('card_fingerprint', models.CharField(max_length=200, blank=True)),
                ('card_last_4', models.CharField(max_length=4, blank=True)),
                ('card_kind', models.CharField(max_length=50, blank=True)),
                ('date_purged', models.DateTimeField(null=True, editable=False)),
                ('token_expiration', models.DateTimeField(null=True)),
                ('user', models.OneToOneField(related_name='bt_customer', null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='currentsubscription',
            name='customer',
            field=models.OneToOneField(related_name='current_subscription', null=True, to='djbraintree.Customer'),
            preserve_default=True,
        ),
    ]
