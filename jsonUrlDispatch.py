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
from .urlDispatch import UrlDispatch, Response

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def jsonify(request, *args, **kw):
    """werkzeug version of Flask's jsonify"""
    top = dict(*args, **kw)
    top = json.dumps(top, indent=(None if request.is_xhr else 2))
    ResponseClass = getattr(request, 'Response', Response)
    return ResponseClass(top, mimetype='application/json')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class JsonUrlDispatch(UrlDispatch):
    jsonify = staticmethod(jsonify)
    json_headers = {}

    def adaptToResponse(self, request, res):
        if isinstance(res, list):
            res = {'items':res}
        elif not isinstance(res, dict):
            return self.asResponse_fallback(request, res)

        return self.asResponse_json(request, res)

    def asResponse_fallback(self):
        ResponseClass = getattr(request, 'Response', Response)
        return ResponseClass(res)

    def asResponse_json(self, request, res):
        res = self.jsonify(request, res)
        return self.setHeaderDefaults(res, self.json_headers)

    def setHeaderDefaults(self, response, headers):
        setkv = response.headers.setdefault
        for k,v in headers.iteritems():
            setkv(k, v)
        return response


