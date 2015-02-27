# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

BT_MERCHANT_ID = getattr(settings, "BT_MERCHANT_ID", False)
BT_PUBLIC_KEY = getattr(settings, "BT_PUBLIC_KEY", False)
BT_PRIVATE_KEY = getattr(settings, "BT_PRIVATE_KEY", False)
BT_CSE_KEY = getattr(settings, "BT_CSE_KEY", False)
BT_SANDBOX = getattr(settings, "BT_SANDBOX", False)
