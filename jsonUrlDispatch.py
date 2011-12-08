# -*- coding: utf-8 -*- vim: set ts=4 sw=4 expandtab:
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2011  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the MIT style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import json
from .urlDispatch import UrlDispatch, BasicApiRoot, Response

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class JsonUrlDispatch(UrlDispatch):
    json_headers = {}

    def branch(self): 
        res = self.new(self.db, self.rules)
        res.json_headers = self.json_headers.copy()
        return res

    def adaptToResponse(self, request, res):
        try: return self.asResponse_json(request, res)
        except TypeError:
            return self.asResponse_fallback(request, res)

    def asResponse_json(self, request, res):
        res = json.dumps(res, indent=(None if request.is_xhr else 2))

        res = self._asRequestResponse(request, res, mimetype='application/json')
        return self.applyHeaders(request, res, self.json_headers)

    def asResponse_fallback(self, request, res):
        return self._asRequestResponse(request, res)

    def findStdHeaders(self, request, response):
        return self.json_headers

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class JsonApiRoot(BasicApiRoot):
    api = JsonUrlDispatch()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Example
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if 0:
    class ExampleJsonApiRoot(JsonApiRoot):
        api = JsonApiRoot.api.branch()
        api.json_headers.update({})

        @api.route('/', methods='GET POST')
        def root(self, request):
            return {'success': True}

    del ExampleJsonApiRoot

