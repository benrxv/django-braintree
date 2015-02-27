# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import braintree
from django.conf import settings


if settings.BT_SANDBOX:
    env = braintree.Environment.Sandbox
else:
    env = None
    raise Exception("")

braintree.Configuration.configure(env, merchant_id=settings.BT_MERCHANT_ID,
                                  public_key=settings.BT_PUBLIC_KEY,
                                  private_key=settings.BT_PRIVATE_KEY)
