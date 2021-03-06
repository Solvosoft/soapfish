# -*- coding: utf-8 -*-

from __future__ import absolute_import

from soapfish.core import SOAPRequest
from soapfish.soap_dispatch import SOAPDispatcher
import logging

__all__ = ['django_dispatcher']

logger = logging.getLogger('soapfish')
class DjangoEnvironWrapper(object):

    def __init__(self, environ):
        self.environ = environ

    def get(self, name, default=None):
        name = name.replace('-', '_').upper()
        for key in (name, 'HTTP_' + name):
            if key in self.environ:
                return self.environ[key]
        return default


def django_dispatcher(service, **dispatcher_kwargs):
    from django.http import HttpResponse
    from django.views.decorators.csrf import csrf_exempt

    def django_dispatch(request):
        soap_request = SOAPRequest(DjangoEnvironWrapper(request.environ), request.body)
        soap_request._original_request = request
        soap_dispatcher = SOAPDispatcher(service, **dispatcher_kwargs)
        soap_response = soap_dispatcher.dispatch(soap_request)

        response = HttpResponse(soap_response.http_content)
        response.status_code = soap_response.http_status_code
        if response.status_code >=300:
            logger.error("Response with error %s %s", response.status_code, soap_response.http_content)
        for k, v in soap_response.http_headers.items():
            response[k] = v
        return response

    return csrf_exempt(django_dispatch)
