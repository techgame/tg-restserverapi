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

    def adaptToResponse(self, request, res):
        if isinstance(res, list):
            res = {'items':res}
        elif not isinstance(res, dict):
            ResponseClass = getattr(request, 'Response', Response)
            return ResponseClass(res)

        return self.jsonify(request, res)

