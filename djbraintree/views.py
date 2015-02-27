# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.http import HttpResponse, HttpResponseBadRequest
from django.views import generic
from braces.views import CsrfExemptMixin
from .auth import braintree

# from .models import Customer
# from djstripe.models import Event, EventProcessingException
# from delorean import Delorean

import logging

logger = logging.getLogger("devote.debug")


class WebhookView(CsrfExemptMixin, generic.View):

    def record_transaction(self, data):
        kind = data.kind
        timestamp = data.timestamp
        # subtype = data["Subtype"]
        # kind = "dwolla.%s.%s" % (data["Type"], subtype)
        # data_dict = {
        #     "kind": kind,
        #     "webhook_message": data,
        #     "valid": True
        # }
        # if subtype == "Status":
        #     stripe_id = data["Id"]
        # elif subtype == "Returned":
        #     stripe_id = "%s_returned" % data["SenderTransactionId"]
        # else:
        #     stripe_id = "dwolla_%f" % Delorean().epoch()
        #     # logger.info("Dwolla webhook subtype unrecognized, check event \
        #     # with stripe_id '%s'" % stripe_id)
        # data_dict['stripe_id'] = stripe_id
        # try:
        #     c = Customer.objects.get(pk=data['Metadata']['customer'])
        #     user = c.user
        # except KeyError:
        #     c = user = None
        # data_dict.update({"dwolla_customer": c, "user": user})

        # existing_events = Event.objects.filter(stripe_id=stripe_id)
        # if existing_events:
        #     EventProcessingException.objects.create(
        #         event=existing_events[0],
        #         data=data,
        #         message="Duplicate event record",
        #         traceback=""
        #     )
        # else:
        #     Event.objects.create(**data_dict)
        #     # See djstripe Event model for next couple methods
        #     # event.validate()
        #     # event.process()

    def post(self, request, *args, **kwargs):
        sig = request.POST['bt_signature']
        payload = request.POST['bt_payload']
        try:
            webhook = braintree.WebhookNotification.parse(sig, payload)
            if webhook.kind == "Foo":
                self.record_transaction(webhook)
            return HttpResponse()
        except braintree.exceptions.InvalidSignatureError:
            message = "Braintree signature mismatch"
            logger.warning(message)
            return HttpResponseBadRequest(message)
