# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import traceback

from .auth import braintree
from .managers import CustomerManager
# from .tasks import send_funds
from model_utils.models import TimeStampedModel
from delorean import Delorean
from jsonfield.fields import JSONField

from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.db import models
from django_extensions.db.fields.encrypted import EncryptedCharField


# def dwolla_charge(sub):
#     # Clear out any previous session
#     DWOLLA_GATE.start_gateway_session()

#     # Add a product to the purchase order
#     # DWOLLA_GATE.add_gateway_product(str(sub.customer), float(sub.amount))
#     DWOLLA_GATE.add_gateway_product('Devote.io subscription', 21.00)

#     # Generate a checkout URL; pass in the recipient's Dwolla ID
#     # url = DWOLLA_GATE.get_gateway_URL(str(sub.customer))
#     url = DWOLLA_GATE.get_gateway_URL(DWOLLA_ACCOUNT['user_id'])
#     return url


# def create_oauth_request_url():
#     """ Send users to this url to authorize us """
#     redirect_uri = "https://www.back2ursite.com/return"
#     scope = "send|balance|funding|transactions|accountinfofull"
#     authUrl = DWOLLA_APP.init_oauth_url(redirect_uri, scope)
#     return authUrl


class BraintreeObject(TimeStampedModel):

    braintree_id = models.CharField(max_length=50)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Customer(BraintreeObject):

    user = models.OneToOneField(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
                                null=True, related_name='bt_customer')
    token = models.CharField(max_length=100, null=True, blank=True)
    refresh_token = models.CharField(max_length=100, null=True, blank=True)
    pin = EncryptedCharField(max_length=100, null=True, blank=True)
    funds_source = models.CharField(max_length=50, blank=True, null=True)
    card_fingerprint = models.CharField(max_length=200, blank=True)
    card_last_4 = models.CharField(max_length=4, blank=True)
    card_kind = models.CharField(max_length=50, blank=True)
    date_purged = models.DateTimeField(null=True, editable=False)
    token_expiration = models.DateTimeField(null=True)

    objects = CustomerManager()

    def __str__(self):
        return unicode(self.user)

    @classmethod
    def get_or_create(cls, user):
        try:
            return Customer.objects.get(user=user), False
        except Customer.DoesNotExist:
            return cls.create(user), True

    @classmethod
    def create(cls, user, token=None):
        cus = Customer.objects.create(user=user)
        return cus

    def get_token(self):
        return None
        # if self.token_expiration <= Delorean().datetime:
        #     token = self.update_tokens()
        # return token

    def update_token(self, token):
        if self.braintree_id:
            braintree.Customer.update(self.braintree_id,
                                      {"payment_method_nonce": token})
        else:
            result = braintree.Customer.create({"email": self.user.email,
                                                "payment_method_nonce": token})
            self.braintree_id = result.customer.id
            self.token = token
            self.save(update_fields=['braintree_id', 'token'])
        return True

    def get_paypal_token(self):
        cus = braintree.Customer.find(self.braintree_id)
        return cus.paypal_accounts[0].token

    def charge_paypal(self, amount, token=None):
        """ amount is a string representation of the dollar amount """
        token = self.get_paypal_token()
        result = braintree.Transaction.sale({"amount": amount,
                                             "payment_method_token": token,
                                             "options": {
                                                 "submit_for_settlement": True
                                             }})
        if result.is_success:
            return result.transaction.id
        else:
            return result.message

        
class CurrentSubscription(TimeStampedModel):

    STATUS_TRIALING = "trialing"
    STATUS_ACTIVE = "active"
    STATUS_PAST_DUE = "past_due"
    STATUS_CANCELLED = "canceled"
    STATUS_UNPAID = "unpaid"

    customer = models.OneToOneField(
        Customer,
        related_name="current_subscription",
        null=True
    )
    plan = models.CharField(max_length=100)
    quantity = models.IntegerField()
    start = models.DateTimeField()
    # trialing, active, past_due, canceled, or unpaid
    # In progress of moving it to choices field
    status = models.CharField(max_length=25)
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True)
    current_period_start = models.DateTimeField(null=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    trial_start = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=7)

    def status_display(self):
        return self.status.replace("_", " ").title()

    def is_period_current(self):
        if self.current_period_end is None:
            return False
        return self.current_period_end > timezone.now()

    def is_status_current(self):
        return self.status in [self.STATUS_TRIALING, self.STATUS_ACTIVE]

    """
    Status when customer canceled their latest subscription, one that does not prorate,
    and therefore has a temporary active subscription until period end.
    """
    def is_status_temporarily_current(self):
        return self.canceled_at and self.start < self.canceled_at and self.cancel_at_period_end

    def is_valid(self):
        if not self.is_status_current():
            return False

        if self.cancel_at_period_end and not self.is_period_current():
            return False

        return True

    def create_charge(self):
        url = dwolla_charge(self)
        return url

    def get_plan(self):
        return Plan.objects.get(name=str(self.customer.user))

    def charge_subscription(self):
        token = self.customer.get_token()
        cus = self.customer
        metadata = {'recur': 'recur'}
        # Need to do something here...
        # send_funds.delay(token, DWOLLA_ACCOUNT['user_id'],
        #                  float(self.amount), cus.pin,
        #                  "Devote.io monthly subscription",
        #                  metadata=metadata)

    @classmethod
    def get_or_create(cls, customer, amount=0):
        try:
            return CurrentSubscription.objects.get(customer=customer), False
        except CurrentSubscription.DoesNotExist:
            return cls.create(customer, amount=amount), True

    @classmethod
    def create(cls, customer, amount=0):
        end = Delorean().next_month().truncate("month").datetime
        current_sub = CurrentSubscription.objects.create(customer=customer, quantity=1,
                                                         start=timezone.now(), status="active",
                                                         current_period_end=end, amount=amount,
                                                         current_period_start=timezone.now())
        return current_sub

    def update(self, amount):
        self.amount = amount
        self.save(update_fields=['amount'])

CURRENCIES = (
    ('usd', 'U.S. Dollars',),
    ('gbp', 'Pounds (GBP)',),
    ('eur', 'Euros',))

INTERVALS = (
    ('week', 'Week',),
    ('month', 'Month',),
    ('year', 'Year',))

